from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ParticipantTelemetry(BaseModel):
    """Telemetria oficial individual dos 10 jogadores."""
    participant_id: int
    team_side: str  # "BLUE" ou "RED"
    team_code: str
    player_name: str
    champion_name: str
    role: str = "FLEX"
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    kda_ratio: float = 0.0
    cs: int = 0
    gold: int = 0
    damage_to_champions: int = 0
    damage_taken: int = 0
    kill_participation_pct: float = 0.0
    gold_share_pct: float = 0.0
    vision_score: int = 0
    items: List[int] = Field(default_factory=list)

class SettlementDossier(BaseModel):
    """
    Dossiê Oficial de Liquidação por Mapa (Telemetria 100% Real).
    Compilado estritamente após a queda do Nexus e aprovação pelo Zero-Doubt Gate.
    """
    game_id: str
    match_id: str
    league_slug: str
    league_name: str
    match_title: str
    game_number: int = 1
    patch_version: str = "14.16.1"

    # Equipes e Lados Oficiais
    blue_team_name: str
    blue_team_code: str
    red_team_name: str
    red_team_code: str

    winner_name: str
    winner_code: str
    winner_side: str  # "BLUE" ou "RED"
    loser_name: str
    loser_code: str
    loser_side: str

    # In-Game Clock Oficial (Cronômetro estrito da Riot)
    duration_seconds: int
    duration_formatted: str  # "MM:SS"

    # Placar de Abates & Linha Fracionária de Green (.5)
    blue_kills: int
    red_kills: int
    kill_leader_code: str
    kill_spread: int
    handicap_green_line: str

    # Totais de Objetivos Coletivos
    blue_towers: int = 0
    red_towers: int = 0
    blue_dragons: int = 0
    red_dragons: int = 0
    blue_barons: int = 0
    red_barons: int = 0
    blue_heralds: int = 0
    red_heralds: int = 0
    blue_inhibitors: int = 0
    red_inhibitors: int = 0

    # Firsts com Timestamps Reais (Formato "TIME (MM:SS)")
    first_blood_team: str = "NENHUM"
    first_blood_time: str = "00:00"
    first_tower_team: str = "NENHUM"
    first_tower_time: str = "00:00"
    first_dragon_team: str = "NENHUM"
    first_dragon_time: str = "00:00"
    first_herald_team: str = "NENHUM"
    first_herald_time: str = "00:00"
    first_baron_team: str = "NENHUM"
    first_baron_time: str = "00:00"

    # Corridas de Abates (Races to 5, 10, 15)
    race_to_5: str = "NENHUM"
    race_to_10: str = "NENHUM"
    race_to_15: str = "NENHUM"

    # Telemetria dos 10 Jogadores & Auditoria
    participants: List[ParticipantTelemetry] = Field(default_factory=list)
    audit_passed: bool = True
    audit_notes: List[str] = Field(default_factory=list)

class GameRef(BaseModel):
    """Referência oficial para cada mapa (Game) da série."""
    game_id: str
    number: int
    state: str = "unstarted"  # "inProgress", "completed", "unstarted", "unneeded"

class SeriesSummary(BaseModel):
    """
    Súmula Oficial de Série (Confronto MD1 / MD3 / MD5).
    Extraída diretamente da agenda oficial da Riot, sem telemetria estimada.
    """
    event_id: str
    league_slug: str
    league_name: str
    tournament_name: str = ""
    match_title: str

    team_blue_name: str
    team_blue_code: str
    team_blue_wins: int = 0

    team_red_name: str
    team_red_code: str
    team_red_wins: int = 0

    winner_code: str
    winner_name: str
    winner_side: str = "BLUE"
    is_completed: bool = False
    total_games: int = 1
    games: List[GameRef] = Field(default_factory=list)

class AuditResult(BaseModel):
    """Resultado da checagem do Zero-Doubt Verification Gate."""
    passed: bool
    reason: str
    checks: Dict[str, bool] = Field(default_factory=dict)

