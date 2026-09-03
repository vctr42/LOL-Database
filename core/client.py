import re
import httpx
from typing import Dict, Any, List, Optional
from config.settings import settings, normalize_league_slug, get_league_config
from core.models import SeriesSummary, GameRef

class AsyncRiotClient:
    """
    Cliente Assíncrono de Alta Performance para Ingestão da CDN e Schedule da Riot Games.
    Utiliza HTTP/2, pooling de conexões e headers oficiais.
    """

    BASE_LIVESTATS = "https://feed.lolesports.com/livestats/v1"
    SCHEDULE_URL = "https://lolesports.com/pt-BR"

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
                "Accept": "application/json, text/html"
            },
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def get_window(self, game_id: str, starting_time: Optional[str] = None) -> Dict[str, Any]:
        """Obtém snapshot de frames (telemetria e estado) da partida diretamente da CDN."""
        if not self.client:
            raise RuntimeError("AsyncRiotClient deve ser utilizado como context manager (async with).")
            
        url = f"{self.BASE_LIVESTATS}/window/{game_id}"
        params = {"startingTime": starting_time} if starting_time else {}
        
        try:
            resp = await self.client.get(url, params=params)
            if resp.status_code == 200:
                return resp.json()
            return {"error": f"HTTP {resp.status_code}", "status_code": resp.status_code, "gameId": game_id}
        except Exception as e:
            return {"error": str(e), "gameId": game_id}

    async def get_details(self, game_id: str, starting_time: Optional[str] = None) -> Dict[str, Any]:
        """Obtém detalhes estatísticos dos 10 jogadores diretamente da CDN."""
        if not self.client:
            raise RuntimeError("AsyncRiotClient deve ser utilizado como context manager (async with).")
            
        url = f"{self.BASE_LIVESTATS}/details/{game_id}"
        params = {"startingTime": starting_time} if starting_time else {}
        
        try:
            resp = await self.client.get(url, params=params)
            if resp.status_code == 200:
                return resp.json()
            return {"error": f"HTTP {resp.status_code}", "status_code": resp.status_code, "gameId": game_id}
        except Exception as e:
            return {"error": str(e), "gameId": game_id}

    async def fetch_schedule_matches(self) -> List[SeriesSummary]:
        """
        Realiza a ingestão e decodificação do feed oficial de agenda e confrontos da Riot Games.
        Mapeia automaticamente todos os slugs para canônicos e extrai placares oficiais.
        """
        if not self.client:
            raise RuntimeError("AsyncRiotClient deve ser utilizado como context manager (async with).")

        try:
            resp = await self.client.get(self.SCHEDULE_URL)
            if resp.status_code != 200:
                return []
            html = resp.text
        except Exception:
            return []

        event_regex = re.compile(r'\{"__typename":"EventMatch".*?"matchTeams":\[.*?\]\}')
        matches: List[SeriesSummary] = []

        for chunk_match in event_regex.finditer(html):
            chunk = chunk_match.group(0)
            try:
                state_match = re.search(r'"state":"([^"]+)"', chunk)
                state = state_match.group(1) if state_match else "unstarted"

                id_match = re.search(r'"id":"(\d+)"', chunk)
                event_id = id_match.group(1) if id_match else ""

                league_name_match = re.search(r'"league":\{"__typename":"League"[^}]*?"name":"([^"]+)"', chunk)
                league_slug_match = re.search(r'"league":\{"__typename":"League"[^}]*?"slug":"([^"]+)"', chunk)
                
                raw_league_name = league_name_match.group(1) if league_name_match else "CBLOL"
                raw_league_slug = league_slug_match.group(1) if league_slug_match else "cblol"
                canonical_slug = normalize_league_slug(raw_league_slug)
                league_config = get_league_config(canonical_slug)
                league_name = league_config.get("name", raw_league_name)

                tourney_match = re.search(r'"tournament":\{"__typename":"Tournament"[^}]*?"name":"([^"]+)"', chunk)
                tournament_name = tourney_match.group(1) if tourney_match else league_name

                team_pattern = re.compile(
                    r'\{"__typename":"MatchTeam"[^}]*?"name":"([^"]+)"[^}]*?"code":"([^"]+)"[^}]*?"result":\{"__typename":"TeamResult","gameWins":(\d+)'
                )
                teams = team_pattern.findall(chunk)
                if len(teams) < 2:
                    continue

                t1_name, t1_code, t1_w_str = teams[0]
                t2_name, t2_code, t2_w_str = teams[1]
                t1_wins, t2_wins = int(t1_w_str), int(t2_w_str)

                is_completed = (state == "completed" or (t1_wins + t2_wins) > 0)
                
                if t1_wins > t2_wins:
                    winner_code, winner_name, winner_side = t1_code, t1_name, "BLUE"
                elif t2_wins > t1_wins:
                    winner_code, winner_name, winner_side = t2_code, t2_name, "RED"
                else:
                    winner_code, winner_name, winner_side = t1_code, t1_name, "BLUE"

                # Extrair referências reais para cada mapa (Game)
                raw_games = re.findall(r'\{"__typename":"Game","id":"([^"]+)","number":(\d+),"state":"([^"]+)"', chunk)
                game_refs = [
                    GameRef(game_id=gid, number=int(num), state=st)
                    for gid, num, st in raw_games
                ]

                match_title = f"[{league_name}] {t1_name} ({t1_code}) vs {t2_name} ({t2_code})"

                matches.append(SeriesSummary(
                    event_id=event_id,
                    league_slug=canonical_slug,
                    league_name=league_name,
                    tournament_name=tournament_name,
                    match_title=match_title,
                    team_blue_name=t1_name,
                    team_blue_code=t1_code,
                    team_blue_wins=t1_wins,
                    team_red_name=t2_name,
                    team_red_code=t2_code,
                    team_red_wins=t2_wins,
                    winner_code=winner_code,
                    winner_name=winner_name,
                    winner_side=winner_side,
                    is_completed=is_completed,
                    total_games=max(1, len(game_refs) if game_refs else (t1_wins + t2_wins)),
                    games=game_refs
                ))
            except Exception:
                continue

        return matches
