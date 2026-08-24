# tests/mock_data.py

def get_valid_cblol_window_payload():
    """Payload de janela válido e completo do CBLOL (PNG vs LLL)."""
    return {
        "gameId": "1001",
        "gameState": "finished",
        "leagueSlug": "cblol",
        "frames": [
            {
                "rfc3339Timestamp": "2026-08-24T18:00:00.000Z",
                "inGameClock": 0,
                "blueTeam": {"code": "PNG", "totalGold": 2500, "totalKills": 0, "towers": 0, "dragons": 0, "barons": 0, "heralds": 0, "inhibitors": 0},
                "redTeam": {"code": "LLL", "totalGold": 2500, "totalKills": 0, "towers": 0, "dragons": 0, "barons": 0, "heralds": 0, "inhibitors": 0},
                "participants": [{"participantId": i, "totalGold": 500, "kills": 0, "deaths": 0, "assists": 0} for i in range(1, 11)]
            },
            {
                "rfc3339Timestamp": "2026-08-24T18:03:12.000Z",
                "inGameClock": 192,
                "blueTeam": {"code": "PNG", "totalGold": 4100, "totalKills": 1, "towers": 0, "dragons": 0, "barons": 0, "heralds": 0, "inhibitors": 0},
                "redTeam": {"code": "LLL", "totalGold": 3400, "totalKills": 0, "towers": 0, "dragons": 0, "barons": 0, "heralds": 0, "inhibitors": 0},
                "participants": [{"participantId": i, "totalGold": 700, "kills": 1 if i == 4 else 0, "deaths": 1 if i == 9 else 0, "assists": 0} for i in range(1, 11)]
            },
            {
                "rfc3339Timestamp": "2026-08-24T18:32:45.000Z",
                "inGameClock": 1965, # 32 min 45 seg
                "winningTeam": "100",
                "blueTeam": {
                    "code": "PNG",
                    "win": True,
                    "totalGold": 68400,
                    "totalKills": 19,
                    "towers": 9,
                    "dragons": 4,
                    "barons": 2,
                    "heralds": 1,
                    "inhibitors": 2
                },
                "redTeam": {
                    "code": "LLL",
                    "win": False,
                    "totalGold": 51200,
                    "totalKills": 7,
                    "towers": 2,
                    "dragons": 1,
                    "barons": 0,
                    "heralds": 1,
                    "inhibitors": 0
                },
                "participants": [
                    {"participantId": 1, "playerName": "Wizer", "championName": "KSante", "role": "TOP", "kills": 3, "deaths": 1, "assists": 8, "totalGold": 13500, "totalMinionsKilled": 280, "totalDamageDealtToChampions": 18400},
                    {"participantId": 2, "playerName": "CarioK", "championName": "Sejuani", "role": "JUNGLE", "kills": 2, "deaths": 2, "assists": 12, "totalGold": 11200, "totalMinionsKilled": 190, "totalDamageDealtToChampions": 9800},
                    {"participantId": 3, "playerName": "Dynquedo", "championName": "Azir", "role": "MID", "kills": 7, "deaths": 1, "assists": 6, "totalGold": 16800, "totalMinionsKilled": 320, "totalDamageDealtToChampions": 28900},
                    {"participantId": 4, "playerName": "TitaN", "championName": "Varus", "role": "BOTTOM", "kills": 6, "deaths": 1, "assists": 9, "totalGold": 15900, "totalMinionsKilled": 310, "totalDamageDealtToChampions": 26400},
                    {"participantId": 5, "playerName": "Kuri", "championName": "Nautilus", "role": "SUPPORT", "kills": 1, "deaths": 2, "assists": 14, "totalGold": 8200, "totalMinionsKilled": 45, "totalDamageDealtToChampions": 5200},
                    {"participantId": 6, "playerName": "Robo", "championName": "Renekton", "role": "TOP", "kills": 2, "deaths": 4, "assists": 2, "totalGold": 11800, "totalMinionsKilled": 260, "totalDamageDealtToChampions": 14200},
                    {"participantId": 7, "playerName": "Croc", "championName": "Vi", "role": "JUNGLE", "kills": 1, "deaths": 4, "assists": 4, "totalGold": 9600, "totalMinionsKilled": 175, "totalDamageDealtToChampions": 7400},
                    {"participantId": 8, "playerName": "Tinowns", "championName": "Orianna", "role": "MID", "kills": 3, "deaths": 3, "assists": 2, "totalGold": 13400, "totalMinionsKilled": 290, "totalDamageDealtToChampions": 21100},
                    {"participantId": 9, "playerName": "Route", "championName": "Kalista", "role": "BOTTOM", "kills": 1, "deaths": 4, "assists": 3, "totalGold": 12100, "totalMinionsKilled": 275, "totalDamageDealtToChampions": 16500},
                    {"participantId": 10, "playerName": "RedBert", "championName": "Rell", "role": "SUPPORT", "kills": 0, "deaths": 4, "assists": 5, "totalGold": 6900, "totalMinionsKilled": 38, "totalDamageDealtToChampions": 3900}
                ]
            }
        ]
    }

def get_match_with_pause_payload():
    """
    Partida com 15 minutos de PAUSA TÉCNICA no palco.
    O relógio UTC correu 45 minutos no total, mas o inGameClock oficial foi de 30 minutos (1800 seg).
    O sistema DEVE calcular exatamente 30:00 (1800 segundos), ignorando os 15 min de pausa.
    """
    return {
        "gameId": "2002",
        "gameState": "finished",
        "leagueSlug": "lck",
        "frames": [
            {
                "rfc3339Timestamp": "2026-08-24T10:00:00.000Z",
                "inGameClock": 0,
                "blueTeam": {"code": "T1", "totalGold": 2500, "totalKills": 0},
                "redTeam": {"code": "GEN", "totalGold": 2500, "totalKills": 0},
                "participants": [{"participantId": i} for i in range(1, 11)]
            },
            {
                # Frame final após pausa técnica de 15 minutos na transmissão
                "rfc3339Timestamp": "2026-08-24T10:45:00.000Z", # Relógio UTC correu 45 minutos
                "inGameClock": 1800, # In-Game Clock oficial da Riot foi 30:00 minutos
                "winningTeam": "200",
                "blueTeam": {"code": "T1", "win": False, "totalGold": 52000, "totalKills": 10, "towers": 3},
                "redTeam": {"code": "GEN", "win": True, "totalGold": 61000, "totalKills": 17, "towers": 9},
                "participants": [{"participantId": i, "playerName": f"P{i}", "championName": f"C{i}"} for i in range(1, 11)]
            }
        ]
    }

def get_corrupted_zero_gold_payload():
    """Payload com ouro zerado (erro grave de telemetria). DEVE ser barrado pelo Zero-Doubt Gate."""
    return {
        "gameId": "9999",
        "gameState": "finished",
        "frames": [
            {
                "inGameClock": 0,
                "blueTeam": {"code": "ABC", "totalGold": 0, "totalKills": 0},
                "redTeam": {"code": "XYZ", "totalGold": 0, "totalKills": 0}
            },
            {
                "inGameClock": 1500,
                "blueTeam": {"code": "ABC", "win": True, "totalGold": 0, "totalKills": 15}, # OURO ZERADO!
                "redTeam": {"code": "XYZ", "win": False, "totalGold": 0, "totalKills": 5}
            }
        ]
    }

def get_unfinished_game_payload():
    """Partida ainda em andamento. DEVE ser barrada pelo Zero-Doubt Gate."""
    return {
        "gameId": "5555",
        "gameState": "in_game",
        "frames": [
            {
                "inGameClock": 600,
                "blueTeam": {"code": "TEAM1", "totalGold": 15000, "totalKills": 2},
                "redTeam": {"code": "TEAM2", "totalGold": 14000, "totalKills": 3},
                "participants": [{"participantId": i} for i in range(1, 11)]
            }
        ]
    }
