import pytest
from core.audit_gate import AuditGate
from tests.mock_data import (
    get_valid_cblol_window_payload,
    get_corrupted_zero_gold_payload,
    get_unfinished_game_payload
)

def test_audit_gate_approves_valid_game():
    """Garante que uma partida válida passe no Zero-Doubt Gate com 100% de integridade."""
    payload = get_valid_cblol_window_payload()
    result = AuditGate.audit_game_window(payload)
    
    assert result.passed is True
    assert result.winner_side == "BLUE"
    assert result.winner_code == "PNG"
    assert result.blue_kills == 19
    assert result.red_kills == 7
    assert result.duration_formatted == "32:45"
    assert len(result.reasons) == 0

def test_audit_gate_blocks_corrupted_zero_gold():
    """Garante o bloqueio imediato se houver ouro zerado na telemetria."""
    payload = get_corrupted_zero_gold_payload()
    result = AuditGate.audit_game_window(payload)
    
    assert result.passed is False
    assert any("ouro zerado" in r.lower() for r in result.reasons)

def test_audit_gate_blocks_unfinished_game():
    """Garante que partidas ainda em andamento não sejam enviadas precocemente."""
    payload = get_unfinished_game_payload()
    result = AuditGate.audit_game_window(payload)
    
    assert result.passed is False
    assert any("não concluída" in r.lower() for r in result.reasons)
