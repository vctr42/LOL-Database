import pytest
from core.models import SettlementDossier, SeriesSummary
from discord.formatters import DiscordFormatter

def test_discord_formatter_builds_ansi_panel():
    dossier = SettlementDossier(
        game_id="test_g1",
        match_id="test_m1",
        league_slug="cblol",
        league_name="CBLOL",
        match_title="[CBLOL] paiN Gaming (PNG) vs Vivo Keyd Stars (VKS) — MAPA 1",
        game_number=1,
        blue_team_name="paiN Gaming",
        blue_team_code="PNG",
        red_team_name="Vivo Keyd Stars",
        red_team_code="VKS",
        winner_name="paiN Gaming",
        winner_code="PNG",
        winner_side="BLUE",
        loser_name="Vivo Keyd Stars",
        loser_code="VKS",
        loser_side="RED",
        duration_seconds=1980,
        duration_formatted="33:00",
        blue_kills=18,
        red_kills=8,
        kill_leader_code="PNG",
        kill_spread=10,
        handicap_green_line="PNG até -9.5 | VKS a partir de +10.5",
        blue_towers=9,
        red_towers=2,
        blue_dragons=4,
        red_dragons=1,
        blue_barons=1,
        red_barons=0,
        first_blood_team="PNG",
        first_blood_time="03:20",
        first_tower_team="PNG",
        first_tower_time="13:45",
        first_dragon_team="PNG",
        first_dragon_time="07:50",
        first_baron_team="PNG",
        first_baron_time="22:15",
        race_to_5="PNG (09:10)",
        race_to_10="PNG (17:30)",
        race_to_15="PNG (26:40)"
    )

    ansi = DiscordFormatter.build_ansi_dossier(dossier)
    assert "```ansi" in ansi
    assert "VENCEDOR:" in ansi
    assert "PNG" in ansi
    assert "VKS" in ansi
    assert "33:00" in ansi
    assert "PNG até -9.5" in ansi
    assert "Auditoria Zero-Doubt" in ansi

def test_discord_formatter_builds_series_panel():
    series = SeriesSummary(
        event_id="ev_123",
        league_slug="cblol",
        league_name="CBLOL",
        match_title="[CBLOL] LOUD (LLL) vs paiN (PNG)",
        team_blue_name="LOUD",
        team_blue_code="LLL",
        team_blue_wins=2,
        team_red_name="paiN Gaming",
        team_red_code="PNG",
        team_red_wins=1,
        winner_code="LLL",
        winner_name="LOUD",
        winner_side="BLUE",
        is_completed=True,
        total_games=3
    )
    panel = DiscordFormatter.build_series_ansi_panel(series)
    assert "SÉRIE OFICIAL CONCLUÍDA" in panel
    assert "2 x 1" in panel
    assert "LLL" in panel
    assert "PNG" in panel
    assert "LOUD (LLL)" in panel
