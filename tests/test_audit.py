import pytest
from core.audit import ZeroDoubtGate

def test_audit_gate_approves_valid_game():
    valid_window = {
        "frames": [
            {
                "rfc460Timestamp": "2026-08-25T14:00:00.000Z",
                "gameState": "in_game",
                "blueTeam": {"totalGold": 2500, "totalKills": 0, "towers": 0},
                "redTeam": {"totalGold": 2500, "totalKills": 0, "towers": 0}
            },
            {
                "rfc460Timestamp": "2026-08-25T14:32:00.000Z",
                "gameState": "complete",
                "blueTeam": {"totalGold": 65000, "totalKills": 18, "towers": 9},
                "redTeam": {"totalGold": 52000, "totalKills": 8, "towers": 2}
            }
        ]
    }
    res = ZeroDoubtGate.audit_game_window(valid_window)
    assert res.passed is True
    assert res.checks["game_completed"] is True
    assert res.checks["duration_valid"] is True
    assert res.checks["positive_gold"] is True

def test_audit_gate_blocks_incomplete_game():
    incomplete_window = {
        "frames": [
            {
                "rfc460Timestamp": "2026-08-25T14:00:00.000Z",
                "gameState": "in_game",
                "blueTeam": {"totalGold": 2500, "totalKills": 0, "towers": 0},
                "redTeam": {"totalGold": 2500, "totalKills": 0, "towers": 0}
            },
            {
                "rfc460Timestamp": "2026-08-25T14:15:00.000Z",
                "gameState": "in_game",
                "blueTeam": {"totalGold": 30000, "totalKills": 5, "towers": 1},
                "redTeam": {"totalGold": 28000, "totalKills": 4, "towers": 0}
            }
        ]
    }
    res = ZeroDoubtGate.audit_game_window(incomplete_window)
    assert res.passed is False
    assert "Aguardando queda do Nexus" in res.reason

def test_audit_gate_blocks_remake():
    remake_window = {
        "frames": [
            {
                "rfc460Timestamp": "2026-08-25T14:00:00.000Z",
                "gameState": "in_game",
                "blueTeam": {"totalGold": 2500, "totalKills": 0, "towers": 0},
                "redTeam": {"totalGold": 2500, "totalKills": 0, "towers": 0}
            },
            {
                "rfc460Timestamp": "2026-08-25T14:03:00.000Z",
                "gameState": "complete",
                "blueTeam": {"totalGold": 3000, "totalKills": 0, "towers": 0},
                "redTeam": {"totalGold": 3000, "totalKills": 0, "towers": 0}
            }
        ]
    }
    res = ZeroDoubtGate.audit_game_window(remake_window)
    assert res.passed is False
    assert "remake" in res.reason.lower()

def test_audit_gate_blocks_zero_gold():
    zero_gold_window = {
        "frames": [
            {
                "rfc460Timestamp": "2026-08-25T14:00:00.000Z",
                "gameState": "in_game",
                "blueTeam": {"totalGold": 0, "totalKills": 0, "towers": 0},
                "redTeam": {"totalGold": 0, "totalKills": 0, "towers": 0}
            },
            {
                "rfc460Timestamp": "2026-08-25T14:32:00.000Z",
                "gameState": "complete",
                "blueTeam": {"totalGold": 0, "totalKills": 18, "towers": 9},
                "redTeam": {"totalGold": 0, "totalKills": 8, "towers": 2}
            }
        ]
    }
    res = ZeroDoubtGate.audit_game_window(zero_gold_window)
    assert res.passed is False
    assert "ouro total" in res.reason.lower()
