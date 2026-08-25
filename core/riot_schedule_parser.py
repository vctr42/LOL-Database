import sys
import requests
import re
import json
from typing import List, Dict, Any, Optional

# Configurar stdout para UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

class RiotScheduleParser:
    """Parser oficial para extração de agenda, partidas e mapas reais do LoLEsports da Riot Games."""

    SCHEDULE_URL = "https://lolesports.com/pt-BR/schedule"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"
    }

    @classmethod
    def fetch_official_matches(cls) -> List[Dict[str, Any]]:
        """Busca e decodifica as partidas reais diretamente do portal oficial da Riot."""
        try:
            resp = requests.get(cls.SCHEDULE_URL, headers=cls.HEADERS, timeout=10)
            if resp.status_code != 200:
                return []
            return cls.parse_matches_from_html(resp.text)
        except Exception as e:
            print(f"[RiotScheduleParser] Erro ao buscar agenda oficial: {e}")
            return []

    @classmethod
    def parse_matches_from_html(cls, html: str) -> List[Dict[str, Any]]:
        matches = []
        
        # Extrair cada bloco de evento EventMatch
        event_chunks = re.findall(r'(\{"__typename":"EventMatch".*?"matchTeams":\[.*?\]\})', html)
        
        for chunk in event_chunks:
            try:
                # Extrair estado do evento
                state_match = re.search(r'"state":"([^"]+)"', chunk)
                event_state = state_match.group(1) if state_match else "unstarted"

                # Extrair ID do evento
                id_match = re.search(r'"id":"(\d+)"', chunk)
                event_id = id_match.group(1) if id_match else ""

                # Extrair Liga
                league_name_match = re.search(r'"league":\{"__typename":"League"[^}]*?"name":"([^"]+)"', chunk)
                league_slug_match = re.search(r'"league":\{"__typename":"League"[^}]*?"slug":"([^"]+)"', chunk)
                league_name = league_name_match.group(1) if league_name_match else "CBLOL"
                league_slug_raw = league_slug_match.group(1) if league_slug_match else "cblol"
                league_slug = league_slug_raw.replace("_", "-").lower()

                # Normalização de slug para nossos canais
                if "cblol" in league_slug:
                    league_slug = "cblol"
                elif "prime" in league_slug or "prm" in league_slug:
                    league_slug = "prime-league"
                elif "rift" in league_slug or "legends" in league_slug:
                    league_slug = "rift-legends"
                elif "norte" in league_slug or "lrn" in league_slug:
                    league_slug = "lrn"
                elif "desafiante" in league_slug or "academy" in league_slug:
                    league_slug = "circuito-desafiante"

                # Extrair Tournament
                tourney_match = re.search(r'"tournament":\{"__typename":"Tournament"[^}]*?"name":"([^"]+)"', chunk)
                tournament_name = tourney_match.group(1) if tourney_match else ""

                # Extrair Times e Placar
                team_pattern = r'\{"__typename":"MatchTeam"[^}]*?"name":"([^"]+)"[^}]*?"code":"([^"]+)"[^}]*?"result":\{"__typename":"TeamResult","gameWins":(\d+)'
                teams = re.findall(team_pattern, chunk)
                
                if len(teams) >= 2:
                    t1_name, t1_code, t1_w_str = teams[0]
                    t2_name, t2_code, t2_w_str = teams[1]
                    t1_wins = int(t1_w_str)
                    t2_wins = int(t2_w_str)
                    
                    is_completed = (event_state == "completed" or (t1_wins + t2_wins) > 0)
                    winner_code = t1_code if t1_wins > t2_wins else (t2_code if t2_wins > t1_wins else None)
                    winner_side = "BLUE" if t1_wins > t2_wins else ("RED" if t2_wins > t1_wins else None)

                    matches.append({
                        "event_id": event_id,
                        "state": event_state,
                        "tournament": tournament_name,
                        "league_slug": league_slug,
                        "league_name": league_name,
                        "team_blue": {"name": t1_name, "code": t1_code, "wins": t1_wins},
                        "team_red": {"name": t2_name, "code": t2_code, "wins": t2_wins},
                        "is_completed": is_completed,
                        "winner_code": winner_code,
                        "winner_side": winner_side,
                        "total_games_played": t1_wins + t2_wins
                    })
            except Exception as e:
                continue

        return matches

if __name__ == "__main__":
    real_matches = RiotScheduleParser.fetch_official_matches()
    print(f"Total de confrontos oficiais extraídos da Riot Games: {len(real_matches)}")
    completed = [m for m in real_matches if m.get("is_completed")]
    print(f"Confrontos com mapas finalizados: {len(completed)}")
    for m in completed[:10]:
        print(f" -> [{m['league_name']} ({m['league_slug']})] {m['team_blue']['name']} ({m['team_blue']['code']}) [{m['team_blue']['wins']}] x [{m['team_red']['wins']}] {m['team_red']['name']} ({m['team_red']['code']}) | Vencedor: {m.get('winner_code')}")
