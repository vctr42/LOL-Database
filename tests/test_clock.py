import pytest
from core.compiler import SettlementCompiler

def test_in_game_clock_calculation():
    frames = [
        {"rfc460Timestamp": "2026-08-25T14:00:00.000Z"},
        {"rfc460Timestamp": "2026-08-25T14:15:30.000Z"},
        {"rfc460Timestamp": "2026-08-25T14:32:45.000Z"}
    ]
    sec, formatted = SettlementCompiler.calculate_in_game_duration(frames)
    assert sec == 1965
    assert formatted == "32:45"

def test_in_game_clock_handles_short_clock():
    frames = [
        {"rfc460Timestamp": "2026-08-25T10:00:00.000Z"},
        {"rfc460Timestamp": "2026-08-25T10:20:00.000Z"}
    ]
    sec, formatted = SettlementCompiler.calculate_in_game_duration(frames)
    assert sec == 1200
    assert formatted == "20:00"
