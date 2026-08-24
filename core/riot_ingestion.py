import requests
import json
import time
from typing import Dict, Any, List, Optional
from core.riot_feed import RiotFeedClient
from core.audit_gate import AuditGate
from core.settlement import SettlementCompiler
from core.database import DatabaseManager
from discord.embeds import DiscordFormatter
from discord.router import DiscordRouter

class RiotLiveIngestion:
    """Motor de ingestão de telemetria 100% real e soberana da Riot Games Esports."""

    SCHEDULE_URL = "https://esports-api.lolesports.com/persisted/val/getSchedule"
    LIVE_DETAILS_URL = "https://esports-api.lolesports.com/persisted/val/getLiveDetails"

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.client = RiotFeedClient()
        self.db = db_manager or DatabaseManager()

    def fetch_official_schedule(self, league_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Busca agenda oficial de eventos da Riot Esports."""
        params = {"hl": "pt-BR"}
        if league_id:
            params["leagueId"] = league_id
        try:
            resp = requests.get(self.SCHEDULE_URL, params=params, headers={"User-Agent": "LOL-Database/1.0"}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data", {}).get("schedule", {}).get("events", [])
            return []
        except Exception as e:
            print(f"[Riot Ingestion] Erro ao buscar agenda oficial: {e}")
            return []

    def fetch_live_events(self) -> List[Dict[str, Any]]:
        """Busca eventos ao vivo ou recém-finalizados."""
        try:
            resp = requests.get(self.LIVE_DETAILS_URL, params={"hl": "pt-BR"}, headers={"User-Agent": "LOL-Database/1.0"}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data", {}).get("schedule", {}).get("events", [])
            return []
        except Exception as e:
            print(f"[Riot Ingestion] Erro ao buscar eventos ao vivo: {e}")
            return []

    def process_and_settle_game(self, game_id: str, league_slug: str, league_name: str, game_number: int = 1, match_id: str = "") -> Optional[Dict[str, Any]]:
        """
        Ingere frames reais da Riot, valida com Zero-Doubt Gate,
        compila o dossiê oficial e salva no Data Lake.
        """
        print(f"[Riot Ingestion] Buscando telemetria oficial do gameId: {game_id}...")
        window_payload = self.client.get_window(game_id)
        
        if "error" in window_payload:
            print(f"[Riot Ingestion] Erro ao obter window da Riot: {window_payload['error']}")
            return None

        # Zero-Doubt Verification Gate
        audit = AuditGate.audit_game_window(window_payload)
        if not audit.passed:
            print(f"[Riot Ingestion] Partida {game_id} bloqueada pelo Zero-Doubt Gate: {audit.reasons}")
            return None

        league_meta = {
            "league_slug": league_slug.lower(),
            "league_name": league_name.upper(),
            "game_number": game_number,
            "match_id": match_id or game_id
        }

        # Compilar Dossiê Oficial 100% Real
        dossier = SettlementCompiler.compile_from_window_and_details(window_payload, league_meta=league_meta)
        if not dossier:
            return None

        yaml_text = DiscordFormatter.build_yaml_dossier(dossier)

        # Salvar no Data Lake
        self.db.save_dossier(dossier, yaml_text, raw_window=window_payload)
        print(f"✅ Partida oficial {dossier.match_title} liquidada e salva com 100% de integridade!")

        return dossier.model_dump()

    def scan_all_recent(self):
        """Varre eventos da Riot Games e processa partidas finalizadas."""
        events = self.fetch_live_events()
        if not events:
            events = self.fetch_official_schedule()

        print(f"[Riot Ingestion] Total de eventos oficiais encontrados: {len(events)}")
        processed = 0

        for evt in events:
            league = evt.get("league", {})
            league_slug = league.get("slug", "lol")
            league_name = league.get("name", "LOL")
            match = evt.get("match", {})
            match_id = match.get("id", evt.get("id", ""))
            games = match.get("games", [])

            for idx, g in enumerate(games):
                if g.get("state") == "completed" and g.get("id"):
                    g_id = str(g["id"])
                    res = self.process_and_settle_game(
                        game_id=g_id,
                        league_slug=league_slug,
                        league_name=league_name,
                        game_number=idx + 1,
                        match_id=match_id
                    )
                    if res:
                        processed += 1

        print(f"[Riot Ingestion] Varredura concluída. {processed} partidas oficiais reais liquidadas.")
