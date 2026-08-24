import sqlite3
from typing import Dict, Any, List, Optional
from core.database import DatabaseManager

class H2HEngine:
    """Motor de cálculo analítico para confrontos diretos (Head-to-Head) e tendências pré-jogo."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def compare_teams(self, team_a: str, team_b: str, limit_games: int = 20) -> Dict[str, Any]:
        """
        Calcula estatísticas de confronto direto entre Time A e Time B.
        Usa os dados persistidos no Data Lake (SQLite / Supabase).
        """
        team_a = team_a.upper().strip()
        team_b = team_b.upper().strip()
        
        conn = self.db._get_sqlite_conn()
        cursor = conn.cursor()

        # Buscar jogos onde ambos participaram
        query = """
        SELECT g.*, m.team_blue_code, m.team_red_code, m.league_name
        FROM games g
        JOIN matches m ON g.match_id = m.id
        WHERE (m.team_blue_code = ? AND m.team_red_code = ?)
           OR (m.team_blue_code = ? AND m.team_red_code = ?)
        ORDER BY g.settled_at DESC LIMIT ?
        """
        cursor.execute(query, (team_a, team_b, team_b, team_a, limit_games))
        games = [dict(row) for row in cursor.fetchall()]
        conn.close()

        total_games = len(games)
        if total_games == 0:
            # Retornar estatísticas isoladas de cada time se não houver confronto direto
            stats_a = self.get_team_profile(team_a)
            stats_b = self.get_team_profile(team_b)
            return {
                "direct_h2h_found": False,
                "team_a": team_a,
                "team_b": team_b,
                "total_games": 0,
                "stats_a": stats_a,
                "stats_b": stats_b,
                "recent_games": []
            }

        wins_a = sum(1 for g in games if g["winner_code"].upper() == team_a)
        wins_b = total_games - wins_a
        
        total_duration_sec = sum(g["duration_seconds"] for g in games)
        avg_duration_sec = int(total_duration_sec / total_games)
        avg_duration_fmt = f"{avg_duration_sec//60:02d}:{avg_duration_sec%60:02d}"

        # Firsts em H2H
        fb_a = sum(1 for g in games if (g.get("first_blood_team") or "").upper() == team_a)
        ft_a = sum(1 for g in games if (g.get("first_tower_team") or "").upper() == team_a)
        fd_a = sum(1 for g in games if (g.get("first_dragon_team") or "").upper() == team_a)
        fbaron_a = sum(1 for g in games if (g.get("first_baron_team") or "").upper() == team_a)

        # Médias de kills
        kills_a_list = []
        kills_b_list = []
        for g in games:
            if g["winner_side"] == "BLUE":
                is_a_blue = (g.get("team_blue_code", "").upper() == team_a)
                kills_a_list.append(g["blue_kills"] if is_a_blue else g["red_kills"])
                kills_b_list.append(g["red_kills"] if is_a_blue else g["blue_kills"])
            else:
                is_a_red = (g.get("team_red_code", "").upper() == team_a)
                kills_a_list.append(g["red_kills"] if is_a_red else g["blue_kills"])
                kills_b_list.append(g["blue_kills"] if is_a_red else g["red_kills"])

        avg_kills_a = round(sum(kills_a_list) / max(1, total_games), 1)
        avg_kills_b = round(sum(kills_b_list) / max(1, total_games), 1)

        return {
            "direct_h2h_found": True,
            "team_a": team_a,
            "team_b": team_b,
            "total_games": total_games,
            "wins_a": wins_a,
            "wins_b": wins_b,
            "win_rate_a_pct": round((wins_a / total_games) * 100, 1),
            "win_rate_b_pct": round((wins_b / total_games) * 100, 1),
            "avg_duration_formatted": avg_duration_fmt,
            "avg_duration_seconds": avg_duration_sec,
            "avg_kills_a": avg_kills_a,
            "avg_kills_b": avg_kills_b,
            "first_blood_rate_a_pct": round((fb_a / total_games) * 100, 1),
            "first_tower_rate_a_pct": round((ft_a / total_games) * 100, 1),
            "first_dragon_rate_a_pct": round((fd_a / total_games) * 100, 1),
            "first_baron_rate_a_pct": round((fbaron_a / total_games) * 100, 1),
            "recent_games": games[:5]
        }

    def get_team_profile(self, team_code: str, limit_games: int = 15) -> Dict[str, Any]:
        """Calcula o perfil estatístico recente de uma equipe individual."""
        team_code = team_code.upper().strip()
        conn = self.db._get_sqlite_conn()
        cursor = conn.cursor()
        
        query = """
        SELECT g.*, m.team_blue_code, m.team_red_code, m.league_name
        FROM games g
        JOIN matches m ON g.match_id = m.id
        WHERE m.team_blue_code = ? OR m.team_red_code = ?
        ORDER BY g.settled_at DESC LIMIT ?
        """
        cursor.execute(query, (team_code, team_code, limit_games))
        games = [dict(row) for row in cursor.fetchall()]
        conn.close()

        total = len(games)
        if total == 0:
            return {
                "team_code": team_code,
                "total_games": 0,
                "win_rate_pct": 0.0,
                "avg_duration_formatted": "00:00",
                "avg_kills": 0.0,
                "first_blood_rate_pct": 0.0,
                "first_tower_rate_pct": 0.0,
                "first_dragon_rate_pct": 0.0
            }

        wins = sum(1 for g in games if g["winner_code"].upper() == team_code)
        total_sec = sum(g["duration_seconds"] for g in games)
        avg_sec = int(total_sec / total)

        fb = sum(1 for g in games if (g.get("first_blood_team") or "").upper() == team_code)
        ft = sum(1 for g in games if (g.get("first_tower_team") or "").upper() == team_code)
        fd = sum(1 for g in games if (g.get("first_dragon_team") or "").upper() == team_code)

        return {
            "team_code": team_code,
            "total_games": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate_pct": round((wins / total) * 100, 1),
            "avg_duration_formatted": f"{avg_sec//60:02d}:{avg_sec%60:02d}",
            "avg_duration_seconds": avg_sec,
            "first_blood_rate_pct": round((fb / total) * 100, 1),
            "first_tower_rate_pct": round((ft / total) * 100, 1),
            "first_dragon_rate_pct": round((fd / total) * 100, 1)
        }
