import requests
import datetime
from typing import Dict, Any, Optional, List
from config.settings import RIOT_API_KEY, RIOT_LOCALE

class RiotFeedClient:
    """Cliente para ingestão direta dos feeds oficiais e abertos da Riot Games Esports."""
    
    BASE_ESPORTS_API = "https://esports-api.lolesports.com/persisted/val"
    BASE_LIVESTATS_FEED = "https://feed.lolesports.com/livestats/v1"
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        self.api_key = api_key or RIOT_API_KEY
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "LOL-Database/1.0",
            "Accept": "application/json"
        })
        if self.api_key:
            self.session.headers["x-api-key"] = self.api_key

    def get_live_schedule(self) -> Dict[str, Any]:
        """Obtém agenda de partidas ao vivo e recentes da Riot Esports API com fallback."""
        from core.riot_schedule_parser import RiotScheduleParser
        matches = RiotScheduleParser.fetch_official_matches()
        return {"events": matches, "count": len(matches)}

    def get_active_matches(self) -> List[Dict[str, Any]]:
        """Retorna todas as partidas e confrontos oficiais ativos no momento."""
        from core.riot_schedule_parser import RiotScheduleParser
        return RiotScheduleParser.fetch_official_matches()

    def get_window(self, game_id: str, starting_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém snapshot de frames (telemetria e estado) de uma partida pelo gameId.
        O endpoint retorna o array 'frames' com os snapshots in-game.
        """
        url = f"{self.BASE_LIVESTATS_FEED}/window/{game_id}"
        params = {}
        if starting_time:
            params["startingTime"] = starting_time
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e), "gameId": game_id}

    def get_details(self, game_id: str, starting_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém detalhes estatísticos aprofundados e eventos de uma partida pelo gameId.
        """
        url = f"{self.BASE_LIVESTATS_FEED}/details/{game_id}"
        params = {}
        if starting_time:
            params["startingTime"] = starting_time
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e), "gameId": game_id}

    @staticmethod
    def calculate_in_game_duration(frames: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula a duração oficial estrita baseada no in-game clock do servidor da Riot.
        REGRA DO LICOES.MD:
        - Deve ser calculada estritamente pelo relógio do motor de jogo.
        - Imune a pausas técnicas e delays de transmissão.
        - Usa a diferença entre o timestamp do frame inicial (rfc3339/ISO do game start)
          e o frame final onde o Nexus cai (ou gameState == finished).
        """
        if not frames or len(frames) < 2:
            return {"seconds": 0, "formatted": "00:00", "error": "Frames insuficientes"}

        # Identificar primeiro frame válido com participantes ativos ou tempo 0
        first_frame = frames[0]
        last_frame = frames[-1]

        # Verificar se os frames contêm RFC3339Timestamp
        first_ts_str = first_frame.get("rfc3339Timestamp") or first_frame.get("timestamp")
        last_ts_str = last_frame.get("rfc3339Timestamp") or last_frame.get("timestamp")

        if first_ts_str and last_ts_str:
            try:
                # Normalizar timestamps ISO
                dt_first = datetime.datetime.fromisoformat(first_ts_str.replace("Z", "+00:00"))
                dt_last = datetime.datetime.fromisoformat(last_ts_str.replace("Z", "+00:00"))
                
                # Se houver campo inGameClock direto no frame, priorizá-lo
                if "inGameClock" in last_frame:
                    seconds = int(last_frame["inGameClock"])
                elif "current_game_time" in last_frame:
                    seconds = int(last_frame["current_game_time"])
                else:
                    seconds = int((dt_last - dt_first).total_seconds())
                
                minutes = seconds // 60
                remaining_sec = seconds % 60
                return {
                    "seconds": seconds,
                    "formatted": f"{minutes:02d}:{remaining_sec:02d}",
                    "start_ts": first_ts_str,
                    "end_ts": last_ts_str
                }
            except Exception as e:
                pass

        # Fallback se houver campo 'gameTime' ou 'game_time' em milissegundos ou segundos
        if "gameTime" in last_frame:
            ms = last_frame["gameTime"]
            seconds = int(ms / 1000) if ms > 10000 else int(ms)
            minutes = seconds // 60
            remaining_sec = seconds % 60
            return {
                "seconds": seconds,
                "formatted": f"{minutes:02d}:{remaining_sec:02d}"
            }

        return {"seconds": 0, "formatted": "00:00", "error": "Não foi possível extrair inGameClock"}
