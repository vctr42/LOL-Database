from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AuditResult(BaseModel):
    passed: bool
    game_id: str
    reasons: List[str] = Field(default_factory=list)
    winner_code: Optional[str] = None
    winner_side: Optional[str] = None
    duration_seconds: int = 0
    duration_formatted: str = "00:00"
    blue_kills: int = 0
    red_kills: int = 0
    blue_gold: int = 0
    red_gold: int = 0
    participants_count: int = 0

class AuditGate:
    """
    Zero-Doubt Verification Gate.
    Validação rigorosa antes de qualquer emissão de relatório ou liquidação.
    Bloqueia se houver dados incompletos, inconsistência de ouro, vencedor indefinido ou erros de telemetria.
    """

    @staticmethod
    def audit_game_window(window_payload: Dict[str, Any], details_payload: Optional[Dict[str, Any]] = None) -> AuditResult:
        reasons = []
        game_id = window_payload.get("gameId", "unknown")
        
        # 1. Verificar se payload é válido
        if not window_payload or not isinstance(window_payload, dict):
            return AuditResult(passed=False, game_id=game_id, reasons=["Payload de janela inválido ou vazio"])

        # 2. Verificar estado do jogo
        game_state = str(window_payload.get("gameState", "")).lower()
        frames = window_payload.get("frames", [])
        
        if not frames:
            reasons.append("Nenhum frame de telemetria encontrado na janela")
            return AuditResult(passed=False, game_id=game_id, reasons=reasons)

        last_frame = frames[-1]
        
        # Se gameState não for 'finished' ou 'completed', verificar se o último frame indica término
        is_finished = game_state in ("finished", "completed", "game_over")
        if not is_finished:
            # Checar se no último frame há vitória explícita
            blue_info = last_frame.get("blueTeam", {})
            red_info = last_frame.get("redTeam", {})
            if not (blue_info.get("win") or red_info.get("win") or last_frame.get("winningTeam")):
                reasons.append(f"Partida ainda não concluída (gameState='{game_state}')")

        # 3. Validar ouro dos dois lados
        blue_team = last_frame.get("blueTeam", {})
        red_team = last_frame.get("redTeam", {})
        blue_gold = int(blue_team.get("totalGold", 0) or blue_team.get("gold", 0))
        red_gold = int(red_team.get("totalGold", 0) or red_team.get("gold", 0))

        if blue_gold <= 0 or red_gold <= 0:
            reasons.append(f"Ouro zerado ou inconsistente detectado: Azul={blue_gold}, Vermelho={red_gold}")

        # 4. Validar abates e placar
        blue_kills = int(blue_team.get("totalKills", 0) or blue_team.get("kills", 0))
        red_kills = int(red_team.get("totalKills", 0) or red_team.get("kills", 0))

        # 5. Validar participantes (deve haver 10 participantes ativos)
        participants = last_frame.get("participants", [])
        participants_count = len(participants)
        if participants_count < 10:
            # Em alguns feeds, os participantes estão divididos dentro de blueTeam/redTeam
            blue_participants = blue_team.get("participants", [])
            red_participants = red_team.get("participants", [])
            participants_count = len(blue_participants) + len(red_participants)
            if participants_count < 10 and not details_payload:
                reasons.append(f"Número de participantes incompleto ({participants_count}/10)")

        # 6. Identificar Vencedor Oficial
        winner_side = None
        winner_code = None

        if blue_team.get("win") is True:
            winner_side = "BLUE"
            winner_code = blue_team.get("code") or blue_team.get("name") or "BLUE"
        elif red_team.get("win") is True:
            winner_side = "RED"
            winner_code = red_team.get("code") or red_team.get("name") or "RED"
        elif "winningTeam" in last_frame:
            wt = str(last_frame["winningTeam"]).upper()
            if "100" in wt or "BLUE" in wt:
                winner_side = "BLUE"
                winner_code = blue_team.get("code") or "BLUE"
            elif "200" in wt or "RED" in wt:
                winner_side = "RED"
                winner_code = red_team.get("code") or "RED"

        if not winner_side and is_finished:
            # Checar inibidores/torres ou details_payload
            if details_payload and "winningTeam" in details_payload:
                wt = str(details_payload["winningTeam"]).upper()
                winner_side = "BLUE" if ("100" in wt or "BLUE" in wt) else "RED"
                winner_code = blue_team.get("code") if winner_side == "BLUE" else red_team.get("code")
            else:
                reasons.append("Vencedor do mapa não pôde ser determinado com 100% de certeza")

        # 7. Validar duração oficial
        from core.riot_feed import RiotFeedClient
        duration_info = RiotFeedClient.calculate_in_game_duration(frames)
        duration_seconds = duration_info.get("seconds", 0)
        duration_formatted = duration_info.get("formatted", "00:00")

        if duration_seconds < 600 and is_finished: # Menos de 10 minutos é anômalo/remake
            reasons.append(f"Duração anômala ({duration_formatted}) - Possível remake ou erro de feed")

        # Decisão do Gate
        passed = len(reasons) == 0

        return AuditResult(
            passed=passed,
            game_id=game_id,
            reasons=reasons,
            winner_code=winner_code,
            winner_side=winner_side,
            duration_seconds=duration_seconds,
            duration_formatted=duration_formatted,
            blue_kills=blue_kills,
            red_kills=red_kills,
            blue_gold=blue_gold,
            red_gold=red_gold,
            participants_count=participants_count
        )
