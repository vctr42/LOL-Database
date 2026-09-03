-- ==============================================================================
-- LIVE BET CORE • SCHEMA DEFINITIVO UNIFICADO (SUPABASE POSTGRESQL & SQLITE)
-- ==============================================================================

-- 1. Tabela Principal de Mapas e Telemetria de Apostas
CREATE TABLE IF NOT EXISTS lol_games (
    id TEXT PRIMARY KEY,
    match_id TEXT NOT NULL,
    game_number INTEGER DEFAULT 1,
    league_slug TEXT NOT NULL,
    patch_version TEXT DEFAULT '14.16.1',
    winner_code TEXT NOT NULL,
    winner_side TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    duration_formatted TEXT NOT NULL,
    blue_kills INTEGER DEFAULT 0,
    red_kills INTEGER DEFAULT 0,
    blue_gold INTEGER DEFAULT 0,
    red_gold INTEGER DEFAULT 0,
    blue_towers INTEGER DEFAULT 0,
    red_towers INTEGER DEFAULT 0,
    blue_dragons INTEGER DEFAULT 0,
    red_dragons INTEGER DEFAULT 0,
    blue_barons INTEGER DEFAULT 0,
    red_barons INTEGER DEFAULT 0,
    blue_heralds INTEGER DEFAULT 0,
    red_heralds INTEGER DEFAULT 0,
    blue_inhibitors INTEGER DEFAULT 0,
    red_inhibitors INTEGER DEFAULT 0,
    first_blood_team TEXT,
    first_blood_time TEXT,
    first_tower_team TEXT,
    first_tower_time TEXT,
    first_dragon_team TEXT,
    first_dragon_time TEXT,
    first_herald_team TEXT,
    first_herald_time TEXT,
    first_baron_team TEXT,
    first_baron_time TEXT,
    race_to_5_kills TEXT,
    race_to_10_kills TEXT,
    race_to_15_kills TEXT,
    kill_spread_margin NUMERIC DEFAULT 0.0,
    handicap_green_line TEXT,
    audit_passed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lol_games_league ON lol_games(league_slug);
CREATE INDEX IF NOT EXISTS idx_lol_games_created ON lol_games(created_at DESC);

-- 2. Tabela de Súmulas de Séries e Confrontos
CREATE TABLE IF NOT EXISTS lol_matches (
    id TEXT PRIMARY KEY,
    league_slug TEXT NOT NULL,
    league_name TEXT NOT NULL,
    tournament_name TEXT DEFAULT '',
    team_blue_code TEXT NOT NULL,
    team_blue_name TEXT NOT NULL,
    team_blue_wins INTEGER DEFAULT 0,
    team_red_code TEXT NOT NULL,
    team_red_name TEXT NOT NULL,
    team_red_wins INTEGER DEFAULT 0,
    winner_code TEXT,
    winner_name TEXT,
    best_of INTEGER DEFAULT 1,
    status TEXT DEFAULT 'unstarted',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lol_matches_league ON lol_matches(league_slug);

-- 3. Tabela de Dossiês Oficiais de Liquidação (YAML & JSON)
CREATE TABLE IF NOT EXISTS settlement_dossiers (
    id TEXT PRIMARY KEY,
    game_id TEXT NOT NULL UNIQUE,
    league_slug TEXT NOT NULL,
    match_title TEXT NOT NULL,
    yaml_dossier TEXT NOT NULL,
    json_summary JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_settlement_dossiers_game ON settlement_dossiers(game_id);
CREATE INDEX IF NOT EXISTS idx_settlement_dossiers_created ON settlement_dossiers(created_at DESC);
