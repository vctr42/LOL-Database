import os
import json
import sqlite3
from typing import Dict, Any, List, Optional
from pathlib import Path
from config.settings import DB_MODE, SQLITE_DB_PATH, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
from core.settlement import SettlementDossier

class DatabaseManager:
    """Gerenciador central de persistência com suporte a Supabase (nuvem) e SQLite (local)."""

    def __init__(self, mode: Optional[str] = None, sqlite_path: Optional[str] = None):
        self.mode = (mode or DB_MODE).lower()
        self.sqlite_path = sqlite_path or SQLITE_DB_PATH
        self._init_sqlite()

    def _get_sqlite_conn(self) -> sqlite3.Connection:
        db_path = Path(self.sqlite_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite(self):
        """Inicializa as tabelas no SQLite local caso ainda não existam."""
        conn = self._get_sqlite_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id TEXT PRIMARY KEY,
            league_slug TEXT NOT NULL,
            league_name TEXT NOT NULL,
            team_blue_code TEXT NOT NULL,
            team_blue_name TEXT NOT NULL,
            team_red_code TEXT NOT NULL,
            team_red_name TEXT NOT NULL,
            best_of INTEGER DEFAULT 1,
            status TEXT DEFAULT 'completed',
            started_at TEXT,
            concluded_at TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY,
            match_id TEXT NOT NULL,
            game_number INTEGER NOT NULL,
            league_slug TEXT NOT NULL,
            winner_code TEXT NOT NULL,
            winner_side TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            duration_formatted TEXT NOT NULL,
            blue_kills INTEGER NOT NULL,
            red_kills INTEGER NOT NULL,
            blue_gold INTEGER NOT NULL,
            red_gold INTEGER NOT NULL,
            blue_towers INTEGER DEFAULT 0,
            red_towers INTEGER DEFAULT 0,
            blue_dragons INTEGER DEFAULT 0,
            red_dragons INTEGER DEFAULT 0,
            blue_barons INTEGER DEFAULT 0,
            red_barons INTEGER DEFAULT 0,
            blue_heralds INTEGER DEFAULT 0,
            red_heralds INTEGER DEFAULT 0,
            blue_inhibitors INTEGER DEFAULT 0,
            red_inhibitors INTEGER DEFAULT 0,
            first_blood_team TEXT,
            first_blood_time TEXT,
            first_tower_team TEXT,
            first_tower_time TEXT,
            first_dragon_team TEXT,
            first_dragon_time TEXT,
            first_herald_team TEXT,
            first_herald_time TEXT,
            first_baron_team TEXT,
            first_baron_time TEXT,
            race_to_5_kills TEXT,
            race_to_10_kills TEXT,
            race_to_15_kills TEXT,
            kill_spread_margin REAL,
            handicap_green_line TEXT,
            audit_passed INTEGER DEFAULT 1,
            raw_window_payload TEXT,
            settled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_participants (
            id TEXT PRIMARY KEY,
            game_id TEXT NOT NULL,
            participant_id INTEGER NOT NULL,
            team_side TEXT NOT NULL,
            team_code TEXT NOT NULL,
            player_name TEXT NOT NULL,
            champion_name TEXT NOT NULL,
            role TEXT,
            kills INTEGER DEFAULT 0,
            deaths INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            kda_ratio REAL,
            cs INTEGER DEFAULT 0,
            gold INTEGER DEFAULT 0,
            damage_to_champions INTEGER DEFAULT 0,
            damage_taken INTEGER DEFAULT 0,
            kill_participation_pct REAL,
            gold_share_pct REAL,
            vision_score INTEGER DEFAULT 0,
            items TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settlement_dossiers (
            id TEXT PRIMARY KEY,
            game_id TEXT NOT NULL,
            league_slug TEXT NOT NULL,
            match_title TEXT NOT NULL,
            yaml_dossier TEXT NOT NULL,
            json_summary TEXT NOT NULL,
            sent_to_discord INTEGER DEFAULT 0,
            discord_channel TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    def save_dossier(self, dossier: SettlementDossier, yaml_text: str, raw_window: Optional[Dict[str, Any]] = None) -> bool:
        """Salva o dossiê completo de liquidação e a telemetria dos jogadores."""
        try:
            # 1. Salvar no SQLite local
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            
            # Upsert Match
            cursor.execute("""
            INSERT OR REPLACE INTO matches (id, league_slug, league_name, team_blue_code, team_blue_name, team_red_code, team_red_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                dossier.match_id,
                dossier.league_slug,
                dossier.league_name,
                dossier.winner_code if dossier.winner_side == "BLUE" else dossier.loser_code,
                dossier.winner_code if dossier.winner_side == "BLUE" else dossier.loser_code,
                dossier.winner_code if dossier.winner_side == "RED" else dossier.loser_code,
                dossier.winner_code if dossier.winner_side == "RED" else dossier.loser_code
            ))

            # Upsert Game
            cursor.execute("""
            INSERT OR REPLACE INTO games (
                id, match_id, game_number, league_slug, winner_code, winner_side,
                duration_seconds, duration_formatted, blue_kills, red_kills, blue_gold, red_gold,
                blue_towers, red_towers, blue_dragons, red_dragons, blue_barons, red_barons,
                blue_heralds, red_heralds, blue_inhibitors, red_inhibitors,
                first_blood_team, first_blood_time, first_tower_team, first_tower_time,
                first_dragon_team, first_dragon_time, first_herald_team, first_herald_time,
                first_baron_team, first_baron_time, race_to_5_kills, race_to_10_kills, race_to_15_kills,
                kill_spread_margin, handicap_green_line, audit_passed, raw_window_payload
            ) VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?
            )
            """, (
                dossier.game_id, dossier.match_id, dossier.game_number, dossier.league_slug, dossier.winner_code, dossier.winner_side,
                dossier.duration_seconds, dossier.duration_formatted, dossier.blue_kills, dossier.red_kills, 0, 0,
                dossier.blue_towers, dossier.red_towers, dossier.blue_dragons, dossier.red_dragons, dossier.blue_barons, dossier.red_barons,
                dossier.blue_heralds, dossier.red_heralds, dossier.blue_inhibitors, dossier.red_inhibitors,
                dossier.first_blood_team, dossier.first_blood_time, dossier.first_tower_team, dossier.first_tower_time,
                dossier.first_dragon_team, dossier.first_dragon_time, dossier.first_herald_team, dossier.first_herald_time,
                dossier.first_baron_team, dossier.first_baron_time, dossier.race_to_5, dossier.race_to_10, dossier.race_to_15,
                float(dossier.kill_spread), dossier.handicap_green_line, 1 if dossier.audit_passed else 0,
                json.dumps(raw_window) if raw_window else None
            ))

            # Upsert Participants
            for p in dossier.participants:
                part_id = f"{dossier.game_id}_{p.participant_id}"
                cursor.execute("""
                INSERT OR REPLACE INTO game_participants (
                    id, game_id, participant_id, team_side, team_code, player_name, champion_name, role,
                    kills, deaths, assists, kda_ratio, cs, gold, damage_to_champions, damage_taken,
                    kill_participation_pct, gold_share_pct, vision_score, items
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    part_id, dossier.game_id, p.participant_id, p.team_side, p.team_code, p.player_name, p.champion_name, p.role,
                    p.kills, p.deaths, p.assists, p.kda_ratio, p.cs, p.gold, p.damage_to_champions, p.damage_taken,
                    p.kill_participation_pct, p.gold_share_pct, p.vision_score, json.dumps(p.items)
                ))

            # Upsert Settlement Dossier
            cursor.execute("""
            INSERT OR REPLACE INTO settlement_dossiers (
                id, game_id, league_slug, match_title, yaml_dossier, json_summary
            ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"dossier_{dossier.game_id}", dossier.game_id, dossier.league_slug, dossier.match_title,
                yaml_text, json.dumps(dossier.model_dump())
            ))

            conn.commit()
            conn.close()

            # 2. Se modo Supabase ativo e configurado, sincronizar com Supabase
            if self.mode == "supabase" and SUPABASE_URL and SUPABASE_ANON_KEY:
                self._sync_to_supabase(dossier, yaml_text)

            return True
        except Exception as e:
            print(f"[DatabaseManager Error] Erro ao salvar dossiê: {e}")
            return False

    def _sync_to_supabase(self, dossier: SettlementDossier, yaml_text: str):
        """Envia os dados estruturados para o Supabase via REST API."""
        try:
            import requests
            headers = {
                "apikey": SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            }
            # Upsert game
            url = f"{SUPABASE_URL}/rest/v1/games"
            payload = {
                "id": dossier.game_id,
                "match_id": dossier.match_id,
                "game_number": dossier.game_number,
                "league_slug": dossier.league_slug,
                "winner_code": dossier.winner_code,
                "winner_side": dossier.winner_side,
                "duration_seconds": dossier.duration_seconds,
                "duration_formatted": dossier.duration_formatted,
                "blue_kills": dossier.blue_kills,
                "red_kills": dossier.red_kills,
                "blue_gold": 0,
                "red_gold": 0,
                "blue_towers": dossier.blue_towers,
                "red_towers": dossier.red_towers,
                "blue_dragons": dossier.blue_dragons,
                "red_dragons": dossier.red_dragons,
                "blue_barons": dossier.blue_barons,
                "red_barons": dossier.red_barons,
                "blue_heralds": dossier.blue_heralds,
                "red_heralds": dossier.red_heralds,
                "blue_inhibitors": dossier.blue_inhibitors,
                "red_inhibitors": dossier.red_inhibitors,
                "first_blood_team": dossier.first_blood_team,
                "first_blood_time": dossier.first_blood_time,
                "first_tower_team": dossier.first_tower_team,
                "first_tower_time": dossier.first_tower_time,
                "first_dragon_team": dossier.first_dragon_team,
                "first_dragon_time": dossier.first_dragon_time,
                "first_herald_team": dossier.first_herald_team,
                "first_herald_time": dossier.first_herald_time,
                "first_baron_team": dossier.first_baron_team,
                "first_baron_time": dossier.first_baron_time,
                "race_to_5_kills": dossier.race_to_5,
                "race_to_10_kills": dossier.race_to_10,
                "race_to_15_kills": dossier.race_to_15,
                "kill_spread_margin": float(dossier.kill_spread),
                "handicap_green_line": dossier.handicap_green_line,
                "audit_passed": dossier.audit_passed
            }
            requests.post(url, headers=headers, json=payload, timeout=5)
        except Exception as e:
            print(f"[Supabase Sync Warning] Falha na sincronização com Supabase: {e}")

    def list_settlements(self, limit: int = 50, league_slug: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista liquidações recentes."""
        conn = self._get_sqlite_conn()
        cursor = conn.cursor()
        
        query = """
        SELECT d.id, d.game_id, d.league_slug, d.match_title, d.yaml_dossier, d.json_summary, d.created_at,
               g.winner_code, g.duration_formatted, g.blue_kills, g.red_kills, g.handicap_green_line
        FROM settlement_dossiers d
        LEFT JOIN games g ON d.game_id = g.id
        """
        params = []
        if league_slug:
            query += " WHERE d.league_slug = ?"
            params.append(league_slug.lower())
        query += " ORDER BY d.created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            item = dict(row)
            if item.get("json_summary"):
                try:
                    item["summary_obj"] = json.loads(item["json_summary"])
                except Exception:
                    item["summary_obj"] = {}
            result.append(item)
        conn.close()
        return result

    def get_settlement_by_game_id(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Busca um dossiê e participantes pelo game_id."""
        conn = self._get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM settlement_dossiers WHERE game_id = ?", (game_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        dossier_data = dict(row)
        
        cursor.execute("SELECT * FROM game_participants WHERE game_id = ? ORDER BY participant_id ASC", (game_id,))
        part_rows = cursor.fetchall()
        dossier_data["participants"] = [dict(p) for p in part_rows]
        conn.close()
        return dossier_data
