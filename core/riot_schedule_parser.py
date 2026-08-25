import sys
import requests
import re
import json
from typing import List, Dict, Any, Optional

# Configurar stdout para UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

class RiotScheduleParser:
    """Parser oficial para extração de agenda e partidas reais do LoLEsports da Riot Games."""

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
        # Encontrar todas as ocorrências de matchTeams
        # Padrão: "name":"Nome do Time 1",...,"code":"COD1",...,"name":"Nome do Time 2",...,"code":"COD2"
        pattern = r'"tournament":\{"__typename":"Tournament"[^}]*?"name":"([^"]+)"\},"matchTeams":\[\{"__typename":"MatchTeam"[^}]*?"name":"([^"]+)"[^}]*?"code":"([^"]+)"[^}]*?\},\{"__typename":"MatchTeam"[^}]*?"name":"([^"]+)"[^}]*?"code":"([^"]+)"'
        
        found = re.findall(pattern, html)
        for tournament_name, t1_name, t1_code, t2_name, t2_code in found:
            # Deduzir a liga com base no torneio ou equipes
            league_slug = "cblol"
            if "lck" in tournament_name.lower() or "challengers" in tournament_name.lower():
                league_slug = "lck"
            elif "lpl" in tournament_name.lower():
                league_slug = "lpl"
            elif "lcp" in tournament_name.lower():
                league_slug = "lcp"
            elif "norte" in tournament_name.lower() or "lrn" in tournament_name.lower():
                league_slug = "lrn"
            elif "academy" in t1_name.lower() or "academy" in t2_name.lower():
                league_slug = "circuito-desafiante"

            matches.append({
                "tournament": tournament_name,
                "league_slug": league_slug,
                "team_blue": {"name": t1_name, "code": t1_code},
                "team_red": {"name": t2_name, "code": t2_code}
            })

        return matches

if __name__ == "__main__":
    real_matches = RiotScheduleParser.fetch_official_matches()
    print(f"✅ Total de confrontos oficiais extraídos da Riot Games: {len(real_matches)}")
    for m in real_matches[:10]:
        print(f" -> [{m['league_slug'].upper()}] {m['team_blue']['name']} ({m['team_blue']['code']}) vs {m['team_red']['name']} ({m['team_red']['code']}) | Torneio: {m['tournament']}")
