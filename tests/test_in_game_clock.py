import pytest
from core.riot_feed import RiotFeedClient
from tests.mock_data import get_valid_cblol_window_payload, get_match_with_pause_payload

def test_normal_game_in_game_clock():
    """Valida o cálculo de in-game clock em uma partida regular de 32:45."""
    payload = get_valid_cblol_window_payload()
    res = RiotFeedClient.calculate_in_game_duration(payload["frames"])
    
    assert res["seconds"] == 1965 # 32 minutos e 45 segundos
    assert res["formatted"] == "32:45"

def test_pause_immunity_in_game_clock():
    """
    Valida a imunidade a pausas técnicas.
    O relógio UTC correu 45 minutos, mas o inGameClock oficial foi 30 minutos (1800 seg).
    O sistema NÃO pode retornar 45 minutos (2700 seg). DEVE retornar 30:00 (1800 seg).
    """
    payload = get_match_with_pause_payload()
    res = RiotFeedClient.calculate_in_game_duration(payload["frames"])
    
    assert res["seconds"] == 1800
    assert res["formatted"] == "30:00"
