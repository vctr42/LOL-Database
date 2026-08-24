import math
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from core.audit_gate import AuditGate, AuditResult

class ParticipantTelemetry(BaseModel):
    participant_id: int
    team_side: str # "BLUE" ou "RED"
    team_code: str
    player_name: str
    champion_name: str
    role: Optional[str] = "UNKNOWN"
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
    game_id: str
    match_id: str
    league_slug: str
    league_name: str
    match_title: str # ex: "[LCS] SEN vs FLY — MAPA 1"
    game_number: int
    
    # Moneyline
    winner_code: str
    winner_side: str # "BLUE" ou "RED"
    loser_code: str
    loser_side: str
    
    # In-Game Clock Oficial
    duration_seconds: int
    duration_formatted: str # "MM:SS"
    
    # Placar de Abates & Handicap
    blue_kills: int
    red_kills: int
    kill_leader_code: str
    kill_spread: int # Diferença absoluta
    handicap_green_line: str # Linha fracionária oficial de GREEN (.5)
    
    # Totais de Objetivos
    blue_towers: int
    red_towers: int
    blue_dragons: int
    red_dragons: int
    blue_barons: int
    red_barons: int
    blue_heralds: int
    red_heralds: int
    blue_inhibitors: int
    red_inhibitors: int
    
    # Firsts & Corridas
    first_blood_team: str
    first_blood_time: str
    first_tower_team: str
    first_tower_time: str
    first_dragon_team: str
    first_dragon_time: str
    first_herald_team: str
    first_herald_time: str
    first_baron_team: str
    first_baron_time: str
    race_to_5: str
    race_to_10: str
    race_to_15: str
    
    # Telemetria dos 10 Jogadores
    participants: List[ParticipantTelemetry] = Field(default_factory=list)
    audit_passed: bool = True
    audit_notes: List[str] = Field(default_factory=list)

class SettlementCompiler:
    """Compilador oficial do Dossiê de Liquidação de Apostas."""

    @classmethod
    def compile_from_window_and_details(
        cls,
        window_data: Dict[str, Any],
        details_data: Optional[Dict[str, Any]] = None,
        league_meta: Optional[Dict[str, Any]] = None
    ) -> Optional[SettlementDossier]:
        
        # 1. Executar o Zero-Doubt Verification Gate
        audit = AuditGate.audit_game_window(window_data, details_data)
        if not audit.passed:
            # Bloqueio estrito de segurança
            return None

        frames = window_data.get("frames", [])
        last_frame = frames[-1]
        
        blue_team = last_frame.get("blueTeam", {})
        red_team = last_frame.get("redTeam", {})
        
        blue_code = blue_team.get("code") or blue_team.get("name") or "BLUE"
        red_code = red_team.get("code") or red_team.get("name") or "RED"
        
        league_meta = league_meta or {}
        league_slug = league_meta.get("league_slug") or window_data.get("leagueSlug") or "LOL"
        league_name = league_meta.get("league_name") or league_slug.upper()
        game_number = league_meta.get("game_number", 1)
        match_id = league_meta.get("match_id", window_data.get("gameId", "unknown"))
        game_id = window_data.get("gameId", "unknown")
        
        match_title = f"[{league_name}] {blue_code} vs {red_code} — MAPA {game_number}"
        
        # Vencedor e Perdedor
        winner_code = audit.winner_code or (blue_code if audit.winner_side == "BLUE" else red_code)
        winner_side = audit.winner_side or "BLUE"
        loser_code = red_code if winner_side == "BLUE" else blue_code
        loser_side = "RED" if winner_side == "BLUE" else "BLUE"
        
        # Placar de Kills
        blue_kills = audit.blue_kills
        red_kills = audit.red_kills
        
        if blue_kills >= red_kills:
            kill_leader = blue_code
            kill_trailer = red_code
            spread = blue_kills - red_kills
        else:
            kill_leader = red_code
            kill_trailer = blue_code
            spread = red_kills - blue_kills
            
        # Cálculo exato de Handicap Fracionário (.5)
        # Se Leader venceu por +10 kills: Linha Green é "LEADER até -9.5 | TRAILER a partir de +10.5"
        if spread == 0:
            handicap_line = f"EMPATE EM KILLS ({blue_kills} x {red_kills})"
        else:
            line_margin = spread - 0.5
            trailer_margin = spread + 0.5
            handicap_line = f"{kill_leader} até -{line_margin:.1f} | {kill_trailer} a partir de +{trailer_margin:.1f}"

        # Totais de Objetivos do último frame
        blue_towers = int(blue_team.get("towers", 0))
        red_towers = int(red_team.get("towers", 0))
        blue_dragons = int(blue_team.get("dragons", 0) if isinstance(blue_team.get("dragons"), int) else len(blue_team.get("dragons", [])))
        red_dragons = int(red_team.get("dragons", 0) if isinstance(red_team.get("dragons"), int) else len(red_team.get("dragons", [])))
        blue_barons = int(blue_team.get("barons", 0))
        red_barons = int(red_team.get("barons", 0))
        blue_heralds = int(blue_team.get("heralds", 0) or blue_team.get("riftHeralds", 0))
        red_heralds = int(red_team.get("heralds", 0) or red_team.get("riftHeralds", 0))
        blue_inhibitors = int(blue_team.get("inhibitors", 0))
        red_inhibitors = int(red_team.get("inhibitors", 0))

        # Eventos de Firsts e Corridas
        firsts_and_races = cls._extract_events_and_races(frames, blue_code, red_code)
        
        # Telemetria dos 10 Jogadores
        participants_telemetry = cls._extract_participants(window_data, details_data, blue_code, red_code, blue_kills, red_kills, audit.blue_gold, audit.red_gold)

        return SettlementDossier(
            game_id=game_id,
            match_id=match_id,
            league_slug=league_slug.lower(),
            league_name=league_name,
            match_title=match_title,
            game_number=game_number,
            winner_code=winner_code,
            winner_side=winner_side,
            loser_code=loser_code,
            loser_side=loser_side,
            duration_seconds=audit.duration_seconds,
            duration_formatted=audit.duration_formatted,
            blue_kills=blue_kills,
            red_kills=red_kills,
            kill_leader_code=kill_leader,
            kill_spread=spread,
            handicap_green_line=handicap_line,
            blue_towers=blue_towers,
            red_towers=red_towers,
            blue_dragons=blue_dragons,
            red_dragons=red_dragons,
            blue_barons=blue_barons,
            red_barons=red_barons,
            blue_heralds=blue_heralds,
            red_heralds=red_heralds,
            blue_inhibitors=blue_inhibitors,
            red_inhibitors=red_inhibitors,
            first_blood_team=firsts_and_races["first_blood_team"],
            first_blood_time=firsts_and_races["first_blood_time"],
            first_tower_team=firsts_and_races["first_tower_team"],
            first_tower_time=firsts_and_races["first_tower_time"],
            first_dragon_team=firsts_and_races["first_dragon_team"],
            first_dragon_time=firsts_and_races["first_dragon_time"],
            first_herald_team=firsts_and_races["first_herald_team"],
            first_herald_time=firsts_and_races["first_herald_time"],
            first_baron_team=firsts_and_races["first_baron_team"],
            first_baron_time=firsts_and_races["first_baron_time"],
            race_to_5=firsts_and_races["race_to_5"],
            race_to_10=firsts_and_races["race_to_10"],
            race_to_15=firsts_and_races["race_to_15"],
            participants=participants_telemetry,
            audit_passed=True,
            audit_notes=[]
        )

    @classmethod
    def _extract_events_and_races(cls, frames: List[Dict[str, Any]], blue_code: str, red_code: str) -> Dict[str, str]:
        events = {
            "first_blood_team": "NENHUM",
            "first_blood_time": "--:--",
            "first_tower_team": "NENHUM",
            "first_tower_time": "--:--",
            "first_dragon_team": "NENHUM",
            "first_dragon_time": "--:--",
            "first_herald_team": "NENHUM",
            "first_herald_time": "--:--",
            "first_baron_team": "NENHUM",
            "first_baron_time": "--:--",
            "race_to_5": "NENHUM",
            "race_to_10": "NENHUM",
            "race_to_15": "NENHUM"
        }

        prev_blue_kills = 0
        prev_red_kills = 0
        prev_blue_towers = 0
        prev_red_towers = 0
        prev_blue_dragons = 0
        prev_red_dragons = 0
        prev_blue_barons = 0
        prev_red_barons = 0
        prev_blue_heralds = 0
        prev_red_heralds = 0

        for frame in frames:
            # Extrair in-game clock do frame
            clock_str = "--:--"
            if "inGameClock" in frame:
                sec = int(frame["inGameClock"])
                clock_str = f"{sec//60:02d}:{sec%60:02d}"
            elif "current_game_time" in frame:
                sec = int(frame["current_game_time"])
                clock_str = f"{sec//60:02d}:{sec%60:02d}"

            b_team = frame.get("blueTeam", {})
            r_team = frame.get("redTeam", {})
            
            b_kills = int(b_team.get("totalKills", 0) or b_team.get("kills", 0))
            r_kills = int(r_team.get("totalKills", 0) or r_team.get("kills", 0))
            b_towers = int(b_team.get("towers", 0))
            r_towers = int(r_team.get("towers", 0))
            b_dragons = int(b_team.get("dragons", 0) if isinstance(b_team.get("dragons"), int) else len(b_team.get("dragons", [])))
            r_dragons = int(r_team.get("dragons", 0) if isinstance(r_team.get("dragons"), int) else len(r_team.get("dragons", [])))
            b_barons = int(b_team.get("barons", 0))
            r_barons = int(r_team.get("barons", 0))
            b_heralds = int(b_team.get("heralds", 0) or b_team.get("riftHeralds", 0))
            r_heralds = int(r_team.get("heralds", 0) or r_team.get("riftHeralds", 0))

            # First Blood
            if events["first_blood_team"] == "NENHUM":
                if b_kills > prev_blue_kills and r_kills == 0:
                    events["first_blood_team"] = blue_code
                    events["first_blood_time"] = clock_str
                elif r_kills > prev_red_kills and b_kills == 0:
                    events["first_blood_team"] = red_code
                    events["first_blood_time"] = clock_str
                elif b_kills > 0 or r_kills > 0:
                    events["first_blood_team"] = blue_code if b_kills > r_kills else red_code
                    events["first_blood_time"] = clock_str

            # First Tower
            if events["first_tower_team"] == "NENHUM":
                if b_towers > prev_blue_towers and r_towers == 0:
                    events["first_tower_team"] = blue_code
                    events["first_tower_time"] = clock_str
                elif r_towers > prev_red_towers and b_towers == 0:
                    events["first_tower_team"] = red_code
                    events["first_tower_time"] = clock_str

            # First Dragon
            if events["first_dragon_team"] == "NENHUM":
                if b_dragons > prev_blue_dragons and r_dragons == 0:
                    events["first_dragon_team"] = blue_code
                    events["first_dragon_time"] = clock_str
                elif r_dragons > prev_red_dragons and b_dragons == 0:
                    events["first_dragon_team"] = red_code
                    events["first_dragon_time"] = clock_str

            # First Herald
            if events["first_herald_team"] == "NENHUM":
                if b_heralds > prev_blue_heralds and r_heralds == 0:
                    events["first_herald_team"] = blue_code
                    events["first_herald_time"] = clock_str
                elif r_heralds > prev_red_heralds and b_heralds == 0:
                    events["first_herald_team"] = red_code
                    events["first_herald_time"] = clock_str

            # First Baron
            if events["first_baron_team"] == "NENHUM":
                if b_barons > prev_blue_barons and r_barons == 0:
                    events["first_baron_team"] = blue_code
                    events["first_baron_time"] = clock_str
                elif r_barons > prev_red_barons and b_barons == 0:
                    events["first_baron_team"] = red_code
                    events["first_baron_time"] = clock_str

            # Corridas de Abates
            if events["race_to_5"] == "NENHUM":
                if b_kills >= 5 and r_kills < 5:
                    events["race_to_5"] = f"{blue_code} ({clock_str})"
                elif r_kills >= 5 and b_kills < 5:
                    events["race_to_5"] = f"{red_code} ({clock_str})"

            if events["race_to_10"] == "NENHUM":
                if b_kills >= 10 and r_kills < 10:
                    events["race_to_10"] = f"{blue_code} ({clock_str})"
                elif r_kills >= 10 and b_kills < 10:
                    events["race_to_10"] = f"{red_code} ({clock_str})"

            if events["race_to_15"] == "NENHUM":
                if b_kills >= 15 and r_kills < 15:
                    events["race_to_15"] = f"{blue_code} ({clock_str})"
                elif r_kills >= 15 and b_kills < 15:
                    events["race_to_15"] = f"{red_code} ({clock_str})"

            prev_blue_kills, prev_red_kills = b_kills, r_kills
            prev_blue_towers, prev_red_towers = b_towers, r_towers
            prev_blue_dragons, prev_red_dragons = b_dragons, r_dragons
            prev_blue_barons, prev_red_barons = b_barons, r_barons
            prev_blue_heralds, prev_red_heralds = b_heralds, r_heralds

        return events

    @classmethod
    def _extract_participants(
        cls,
        window_data: Dict[str, Any],
        details_data: Optional[Dict[str, Any]],
        blue_code: str,
        red_code: str,
        blue_total_kills: int,
        red_total_kills: int,
        blue_total_gold: int,
        red_total_gold: int
    ) -> List[ParticipantTelemetry]:
        
        participants_list = []
        frames = window_data.get("frames", [])
        last_frame = frames[-1] if frames else {}
        
        raw_participants = last_frame.get("participants", [])
        if not raw_participants:
            b_parts = last_frame.get("blueTeam", {}).get("participants", [])
            r_parts = last_frame.get("redTeam", {}).get("participants", [])
            raw_participants = b_parts + r_parts

        for idx, p in enumerate(raw_participants):
            p_id = p.get("participantId") or (idx + 1)
            is_blue = p_id <= 5 or p.get("teamId") in (100, "100", "BLUE")
            team_side = "BLUE" if is_blue else "RED"
            team_code = blue_code if is_blue else red_code
            team_kills = blue_total_kills if is_blue else red_total_kills
            team_gold = blue_total_gold if is_blue else red_total_gold

            kills = int(p.get("kills", 0))
            deaths = int(p.get("deaths", 0))
            assists = int(p.get("assists", 0))
            kda = round((kills + assists) / max(1, deaths), 2)
            
            cs = int(p.get("totalMinionsKilled", 0) or p.get("creepScore", 0) or p.get("cs", 0))
            gold = int(p.get("currentGold", 0) or p.get("totalGold", 0) or p.get("gold", 0))
            dmg = int(p.get("totalDamageDealtToChampions", 0) or p.get("damageDealt", 0) or p.get("damage", 0))
            dmg_taken = int(p.get("totalDamageTaken", 0) or p.get("damageTaken", 0))
            vision = int(p.get("visionScore", 0))

            kp_pct = round(((kills + assists) / max(1, team_kills)) * 100, 1) if team_kills > 0 else 0.0
            gold_share_pct = round((gold / max(1, team_gold)) * 100, 1) if team_gold > 0 else 0.0

            p_telemetry = ParticipantTelemetry(
                participant_id=p_id,
                team_side=team_side,
                team_code=team_code,
                player_name=p.get("summonerName") or p.get("playerName") or f"Player {p_id}",
                champion_name=p.get("championId") or p.get("championName") or "Champion",
                role=p.get("role") or p.get("position") or "FLEX",
                kills=kills,
                deaths=deaths,
                assists=assists,
                kda_ratio=kda,
                cs=cs,
                gold=gold,
                damage_to_champions=dmg,
                damage_taken=dmg_taken,
                kill_participation_pct=kp_pct,
                gold_share_pct=gold_share_pct,
                vision_score=vision,
                items=p.get("items", [])
            )
            participants_list.append(p_telemetry)

        return participants_list
