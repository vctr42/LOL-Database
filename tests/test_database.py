import os
import pytest
from core.settlement import SettlementCompiler
from core.database import DatabaseManager
from discord.embeds import DiscordFormatter
from tests.mock_data import get_valid_cblol_window_payload

def test_database_sqlite_persistence(tmp_path):
    test_db = tmp_path / "test_settlement.db"
    db_mgr = DatabaseManager(mode="sqlite", sqlite_path=str(test_db))
    
    payload = get_valid_cblol_window_payload()
    league_meta = {"league_slug": "cblol", "league_name": "CBLOL", "game_number": 1, "match_id": "test_m1"}
    dossier = SettlementCompiler.compile_from_window_and_details(payload, league_meta=league_meta)
    yaml_text = DiscordFormatter.build_yaml_dossier(dossier)
    
    # Salvar dossiê
    success = db_mgr.save_dossier(dossier, yaml_text, raw_window=payload)
    assert success is True
    
    # Listar dossiês
    items = db_mgr.list_settlements()
    assert len(items) == 1
    assert items[0]["game_id"] == "1001"
    assert items[0]["winner_code"] == "PNG"
    assert items[0]["duration_formatted"] == "32:45"
    
    # Consultar por ID e verificar 10 participantes
    retrieved = db_mgr.get_settlement_by_game_id("1001")
    assert retrieved is not None
    assert len(retrieved["participants"]) == 10
