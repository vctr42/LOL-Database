import pytest
from core.settlement import SettlementCompiler
from tests.mock_data import get_valid_cblol_window_payload

def test_settlement_compiler_cblol():
    payload = get_valid_cblol_window_payload()
    league_meta = {
        "league_slug": "cblol",
        "league_name": "CBLOL",
        "game_number": 1,
        "match_id": "match_cblol_png_lll"
    }
    
    dossier = SettlementCompiler.compile_from_window_and_details(payload, league_meta=league_meta)
    
    assert dossier is not None
    assert dossier.match_title == "[CBLOL] PNG vs LLL — MAPA 1"
    assert dossier.winner_code == "PNG"
    assert dossier.winner_side == "BLUE"
    assert dossier.loser_code == "LLL"
    assert dossier.loser_side == "RED"
    assert dossier.duration_formatted == "32:45"
    
    # Placar e Handicap
    assert dossier.blue_kills == 19
    assert dossier.red_kills == 7
    assert dossier.kill_spread == 12 # +12 kills
    assert dossier.handicap_green_line == "PNG até -11.5 | LLL a partir de +12.5"
    
    # Objetivos
    assert dossier.blue_towers == 9
    assert dossier.red_towers == 2
    assert dossier.blue_dragons == 4
    assert dossier.red_dragons == 1
    assert dossier.blue_barons == 2
    assert dossier.red_barons == 0
    assert dossier.blue_inhibitors == 2
    
    # Firsts & Corridas
    assert dossier.first_blood_team == "PNG"
    assert dossier.first_blood_time == "03:12"
    
    # 10 Participantes
    assert len(dossier.participants) == 10
    top_blue = dossier.participants[0]
    assert top_blue.player_name == "Wizer"
    assert top_blue.champion_name == "KSante"
    assert top_blue.kills == 3
    assert top_blue.deaths == 1
    assert top_blue.assists == 8
    assert top_blue.kda_ratio == 11.0
    assert top_blue.cs == 280
