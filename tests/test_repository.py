import pytest
import asyncio
from database.repository import DatabaseRepository
from core.models import SettlementDossier, SeriesSummary

@pytest.mark.asyncio
async def test_repository_saves_and_retrieves_sqlite():
    repo = DatabaseRepository()
    dossier = SettlementDossier(
        game_id="test_repo_g1",
        match_id="test_repo_m1",
        league_slug="cblol",
        league_name="CBLOL",
        match_title="[CBLOL] paiN vs Vivo Keyd",
        game_number=1,
        blue_team_name="paiN",
        blue_team_code="PNG",
        red_team_name="Vivo Keyd",
        red_team_code="VKS",
        winner_name="paiN",
        winner_code="PNG",
        winner_side="BLUE",
        loser_name="Vivo Keyd",
        loser_code="VKS",
        loser_side="RED",
        duration_seconds=1800,
        duration_formatted="30:00",
        blue_kills=15,
        red_kills=5,
        kill_leader_code="PNG",
        kill_spread=10,
        handicap_green_line="PNG até -9.5 | VKS a partir de +10.5"
    )

    saved = await repo.save_dossier(dossier, "dossier_yaml_mock")
    assert saved is True

    ids = repo.get_all_settled_ids()
    assert "test_repo_g1" in ids
