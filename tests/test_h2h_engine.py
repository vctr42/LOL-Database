import pytest
from core.settlement import SettlementCompiler
from core.database import DatabaseManager
from discord.embeds import DiscordFormatter
from analytics.h2h_engine import H2HEngine
from tests.mock_data import get_valid_cblol_window_payload

def test_h2h_engine_direct_comparison(tmp_path):
    test_db = tmp_path / "test_h2h.db"
    db_mgr = DatabaseManager(mode="sqlite", sqlite_path=str(test_db))
    
    # Inserir partida PNG vs LLL
    payload = get_valid_cblol_window_payload()
    league_meta = {"league_slug": "cblol", "league_name": "CBLOL", "game_number": 1, "match_id": "cblol_1"}
    dossier = SettlementCompiler.compile_from_window_and_details(payload, league_meta=league_meta)
    yaml_text = DiscordFormatter.build_yaml_dossier(dossier)
    db_mgr.save_dossier(dossier, yaml_text)
    
    h2h = H2HEngine(db_manager=db_mgr)
    comparison = h2h.compare_teams("PNG", "LLL")
    
    assert comparison["direct_h2h_found"] is True
    assert comparison["total_games"] == 1
    assert comparison["wins_a"] == 1
    assert comparison["wins_b"] == 0
    assert comparison["win_rate_a_pct"] == 100.0
    assert comparison["first_blood_rate_a_pct"] == 100.0
