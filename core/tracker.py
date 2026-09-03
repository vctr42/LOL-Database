import logging
from typing import Set, Dict, Any, Optional

logger = logging.getLogger("LiveBetCore.Tracker")

class SettlementLedger:
    """
    Ledger de Idempotência e Rastreamento de Estado de Partidas.
    Garante que nenhuma partida seja liquidada ou disparada mais de uma vez.
    """

    def __init__(self):
        self._settled_game_ids: Set[str] = set()
        self._known_schedule_events: Set[str] = set()
        self._active_live_games: Dict[str, Dict[str, Any]] = {}
        self.is_bootstrapping: bool = True

    def register_settled_id(self, game_id: str):
        """Registra um ID de partida como definitivamente liquidado."""
        if game_id:
            self._settled_game_ids.add(str(game_id).strip())

    def is_settled(self, game_id: str) -> bool:
        """Verifica se o mapa já foi liquidado e salvo anteriormente."""
        return str(game_id).strip() in self._settled_game_ids

    def register_known_event(self, event_id: str):
        """Registra ID de evento da agenda oficial."""
        if event_id:
            self._known_schedule_events.add(str(event_id).strip())

    def is_known_event(self, event_id: str) -> bool:
        """Verifica se o evento já era conhecido no bootstrap."""
        return str(event_id).strip() in self._known_schedule_events

    def preload_from_database(self, settled_ids: list[str]):
        """Carrega IDs liquidados do banco de dados na inicialização."""
        for gid in settled_ids:
            self.register_settled_id(gid)
        logger.info(f"Ledger inicializado com {len(self._settled_game_ids)} mapas conhecidos no Data Lake.")

    def finish_bootstrap(self):
        """Finaliza a fase de bootstrap inicial (ativa a escuta em tempo real)."""
        self.is_bootstrapping = False
        logger.info("Bootstrap concluído. Monitoramento autônomo em tempo real ATIVADO.")

    @property
    def total_settled(self) -> int:
        return len(self._settled_game_ids)
