import pytest
from core.compiler import SettlementCompiler

def test_compiler_calculates_fractional_handicap():
    frames = [
        {
            "rfc460Timestamp": "2026-08-25T14:00:00.000Z",
            "gameState": "in_game",
            "blueTeam": {"code": "PNG", "totalGold": 2500, "totalKills": 0, "towers": 0, "dragons": [], "barons": 0, "heralds": 0, "inhibitors": 0},
            "redTeam": {"code": "RED", "totalGold": 2500, "totalKills": 0, "towers": 0, "dragons": [], "barons": 0, "heralds": 0, "inhibitors": 0}
        },
        {
            "rfc460Timestamp": "2026-08-25T14:32:00.000Z",
            "gameState": "complete",
            "blueTeam": {"code": "PNG", "totalGold": 65000, "totalKills": 18, "towers": 9, "dragons": ["fire", "water"], "barons": 1, "heralds": 1, "inhibitors": 2},
            "redTeam": {"code": "RED", "totalGold": 52000, "totalKills": 8, "towers": 2, "dragons": ["earth"], "barons": 0, "heralds": 0, "inhibitors": 0}
        }
    ]
    window = {"frames": frames}
    league_meta = {
        "league_slug": "cblol",
        "league_name": "CBLOL",
        "game_number": 1,
        "team_blue_name": "paiN Gaming",
        "team_blue_code": "PNG",
        "team_red_name": "RED Canids",
        "team_red_code": "RED"
    }

    dossier = SettlementCompiler.compile_from_window_and_details(window, None, league_meta)
    assert dossier is not None
    assert dossier.winner_code == "PNG"
    assert dossier.blue_kills == 18
    assert dossier.red_kills == 8
    assert dossier.kill_spread == 10
    # Spread 10 -> Leader margin: 10 - 0.5 = 9.5; Trailer margin: 10 + 0.5 = 10.5
    assert "PNG até -9.5" in dossier.handicap_green_line
    assert "RED a partir de +10.5" in dossier.handicap_green_line
    assert dossier.blue_towers == 9
    assert dossier.red_towers == 2
    assert dossier.blue_dragons == 2
    assert dossier.red_dragons == 1
    assert dossier.blue_barons == 1
