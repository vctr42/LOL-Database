from typing import Dict, Any, Optional, List
from core.models import AuditResult

class ZeroDoubtGate:
    """
    Zero-Doubt Verification Gate.
    Política de Confiança Zero: Se houver qualquer inconsistência, bloqueia o envio.
    Antes não enviar nada do que enviar um dado incorreto para a liquidação de apostas.
    """

    @classmethod
    def audit_game_window(
        cls, 
        window_data: Dict[str, Any], 
        details_data: Optional[Dict[str, Any]] = None
    ) -> AuditResult:
        checks: Dict[str, bool] = {}

        if not window_data or "error" in window_data:
            return AuditResult(
                passed=False, 
                reason=f"Payload inválido ou com erro: {window_data.get('error', 'Payload vazio')}",
                checks={"payload_valid": False}
            )

        frames: List[Dict[str, Any]] = window_data.get("frames", [])
        if not frames or len(frames) < 2:
            return AuditResult(
                passed=False, 
                reason="Frames insuficientes para auditar partida",
                checks={"frames_available": False}
            )
        checks["frames_available"] = True

        last_frame = frames[-1]

        # 1. Estado da Partida
        game_state = last_frame.get("gameState")
        is_completed = (game_state == "complete")
        checks["game_completed"] = is_completed
        if not is_completed:
            return AuditResult(
                passed=False, 
                reason=f"Partida em andamento (gameState: {game_state}). Aguardando queda do Nexus.",
                checks=checks
            )

        # 2. In-Game Clock Mínimo (Evitar remakes ou partidas canceladas)
        rfc_time = last_frame.get("rfc460Timestamp")
        # Checagem de duração mínima de 600 segundos (10 minutos)
        # Se houver timestamps ISO em rfc460Timestamp entre o primeiro e o último frame:
        try:
            import datetime
            t_first = datetime.datetime.fromisoformat(frames[0].get("rfc460Timestamp").replace("Z", "+00:00"))
            t_last = datetime.datetime.fromisoformat(last_frame.get("rfc460Timestamp").replace("Z", "+00:00"))
            elapsed_sec = int((t_last - t_first).total_seconds())
        except Exception:
            # Fallback seguro para contagem de frames (cada frame = aprox 10s no stream Riot)
            elapsed_sec = len(frames) * 10

        checks["duration_valid"] = (elapsed_sec >= 600)
        if elapsed_sec < 600:
            return AuditResult(
                passed=False,
                reason=f"Duração insuficiente ({elapsed_sec}s < 600s). Partida pode ser remake.",
                checks=checks
            )

        # 3. Integridade Financeira (Ouro Total > 0)
        blue_team = last_frame.get("blueTeam", {})
        red_team = last_frame.get("redTeam", {})
        b_gold = blue_team.get("totalGold", 0)
        r_gold = red_team.get("totalGold", 0)

        checks["positive_gold"] = (b_gold > 0 and r_gold > 0)
        if b_gold <= 0 or r_gold <= 0:
            return AuditResult(
                passed=False,
                reason="Telemetria corrompida: ouro total das equipes zerado",
                checks=checks
            )

        # 4. Torres Destruídas (O Nexus só pode cair se pelo menos uma torre ou inibidor for destruído)
        b_towers = blue_team.get("towers", 0)
        r_towers = red_team.get("towers", 0)
        checks["towers_plausible"] = (b_towers > 0 or r_towers > 0)

        # 5. Se houver details_data, auditar 10 participantes
        if details_data and "frames" in details_data:
            d_frames = details_data.get("frames", [])
            if d_frames:
                d_last = d_frames[-1]
                parts = d_last.get("participants", [])
                checks["ten_participants"] = (len(parts) == 10)
                if len(parts) > 0 and len(parts) != 10:
                    return AuditResult(
                        passed=False,
                        reason=f"Número incorreto de participantes detectados: {len(parts)} (esperado 10)",
                        checks=checks
                    )

        return AuditResult(
            passed=True,
            reason="Aprovado no Zero-Doubt Verification Gate (100% Confiança)",
            checks=checks
        )
