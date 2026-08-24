-- =========================================================================
-- LOL-DATABASE - SUPABASE DATA LAKE & TELEMETRY SCHEMA
-- =========================================================================

-- 1. TABELA DE SÉRIES / CONFRONTOS (Matches)
CREATE TABLE IF NOT EXISTS matches (
    id VARCHAR(64) PRIMARY KEY,
    league_slug VARCHAR(32) NOT NULL,
    league_name VARCHAR(64) NOT NULL,
    team_blue_code VARCHAR(16) NOT NULL,
    team_blue_name VARCHAR(64) NOT NULL,
    team_red_code VARCHAR(16) NOT NULL,
    team_red_name VARCHAR(64) NOT NULL,
    best_of INTEGER DEFAULT 1,
    status VARCHAR(32) DEFAULT 'completed',
    started_at TIMESTAMPTZ,
    concluded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. TABELA DE MAPAS INDIVIDUAIS (Games)
CREATE TABLE IF NOT EXISTS games (
    id VARCHAR(64) PRIMARY KEY,
    match_id VARCHAR(64) REFERENCES matches(id) ON DELETE CASCADE,
    game_number INTEGER NOT NULL,
    league_slug VARCHAR(32) NOT NULL,
    winner_code VARCHAR(16) NOT NULL,
    winner_side VARCHAR(8) NOT NULL, -- 'BLUE' ou 'RED'
    
    -- Duração oficial estrita baseada no In-Game Clock da Riot
    duration_seconds INTEGER NOT NULL,
    duration_formatted VARCHAR(16) NOT NULL, -- 'MM:SS'
    
    -- Placar e Ouro
    blue_kills INTEGER NOT NULL,
    red_kills INTEGER NOT NULL,
    blue_gold INTEGER NOT NULL,
    red_gold INTEGER NOT NULL,
    
    -- Objetivos
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
    
    -- Firsts & Corridas
    first_blood_team VARCHAR(16),
    first_blood_time VARCHAR(16),
    first_tower_team VARCHAR(16),
    first_tower_time VARCHAR(16),
    first_dragon_team VARCHAR(16),
    first_dragon_time VARCHAR(16),
    first_herald_team VARCHAR(16),
    first_herald_time VARCHAR(16),
    first_baron_team VARCHAR(16),
    first_baron_time VARCHAR(16),
    race_to_5_kills VARCHAR(16),
    race_to_10_kills VARCHAR(16),
    race_to_15_kills VARCHAR(16),
    
    -- Handicap Fracionário Oficial (.5)
    kill_spread_margin NUMERIC(4, 1),
    handicap_green_line VARCHAR(128),
    
    -- Auditoria Zero-Doubt
    audit_passed BOOLEAN DEFAULT TRUE,
    raw_window_payload JSONB,
    settled_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. TABELA DE TELEMETRIA DOS 10 JOGADORES (Game Participants)
CREATE TABLE IF NOT EXISTS game_participants (
    id VARCHAR(128) PRIMARY KEY, -- gameId_participantNumber
    game_id VARCHAR(64) REFERENCES games(id) ON DELETE CASCADE,
    participant_id INTEGER NOT NULL,
    team_side VARCHAR(8) NOT NULL, -- 'BLUE' ou 'RED'
    team_code VARCHAR(16) NOT NULL,
    player_name VARCHAR(64) NOT NULL,
    champion_name VARCHAR(64) NOT NULL,
    role VARCHAR(16), -- 'TOP', 'JUNGLE', 'MID', 'BOTTOM', 'SUPPORT'
    
    kills INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    kda_ratio NUMERIC(5, 2),
    
    cs INTEGER DEFAULT 0,
    gold INTEGER DEFAULT 0,
    damage_to_champions INTEGER DEFAULT 0,
    damage_taken INTEGER DEFAULT 0,
    kill_participation_pct NUMERIC(5, 2),
    gold_share_pct NUMERIC(5, 2),
    vision_score INTEGER DEFAULT 0,
    
    items JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. TABELA DE DOSSIÊS DE LIQUIDAÇÃO & AUDITORIA
CREATE TABLE IF NOT EXISTS settlement_dossiers (
    id VARCHAR(64) PRIMARY KEY,
    game_id VARCHAR(64) REFERENCES games(id) ON DELETE CASCADE,
    league_slug VARCHAR(32) NOT NULL,
    match_title VARCHAR(128) NOT NULL,
    yaml_dossier TEXT NOT NULL,
    json_summary JSONB NOT NULL,
    sent_to_discord BOOLEAN DEFAULT FALSE,
    discord_channel VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ÍNDICES PARA CONSULTAS RÁPIDAS
CREATE INDEX IF NOT EXISTS idx_games_league ON games(league_slug);
CREATE INDEX IF NOT EXISTS idx_games_settled ON games(settled_at DESC);
CREATE INDEX IF NOT EXISTS idx_participants_player ON game_participants(player_name);
CREATE INDEX IF NOT EXISTS idx_participants_champion ON game_participants(champion_name);
CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches(team_blue_code, team_red_code);
