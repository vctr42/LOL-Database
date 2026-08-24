import pytest
from core.settlement import SettlementCompiler
from discord.embeds import DiscordFormatter
from tests.mock_data import get_valid_cblol_window_payload

def test_discord_yaml_formatting():
    payload = get_valid_cblol_window_payload()
    league_meta = {"league_slug": "cblol", "league_name": "CBLOL", "game_number": 1}
    dossier = SettlementCompiler.compile_from_window_and_details(payload, league_meta=league_meta)
    
    yaml_text = DiscordFormatter.build_yaml_dossier(dossier)
    
    assert yaml_text.startswith("```yaml")
    assert yaml_text.endswith("```")
    assert "Relatorio: \"[CBLOL] PNG vs LLL — MAPA 1\"" in yaml_text
    assert "Duracao Oficial: \"32:45\"" in yaml_text
    assert "Placar Abates: \"19 x 7\"" in yaml_text
    assert "Linha Fracionaria: \"PNG até -11.5 | LLL a partir de +12.5\"" in yaml_text
    assert "First Blood: \"PNG (03:12)\"" in yaml_text
    assert "Zero Doubt Gate: \"APROVADO (100% CONFIANCA)\"" in yaml_text
