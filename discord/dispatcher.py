import asyncio
import logging
from typing import Dict, Any, Optional
import httpx

from config.settings import settings, get_league_config, get_league_webhook
from core.models import SettlementDossier, SeriesSummary
from discord.formatters import DiscordFormatter

logger = logging.getLogger("LiveBetCore.Discord")

class DiscordDispatcher:
    """
    Despachante Inteligente e Assíncrono com Controle de Taxa para Discord.
    Roteia cada evento para o canal e bot exclusivo de sua liga oficial.
    """

    def __init__(self):
        self._lock = asyncio.Lock()
        self._last_dispatch_time = 0.0
        self._min_delay_seconds = 0.5  # Proteção contra rate-limit burst

    async def _rate_limit_wait(self):
        async with self._lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_dispatch_time
            if elapsed < self._min_delay_seconds:
                await asyncio.sleep(self._min_delay_seconds - elapsed)
            self._last_dispatch_time = asyncio.get_event_loop().time()

    async def dispatch_map_dossier(self, dossier: SettlementDossier) -> Dict[str, Any]:
        """Envia o card ANSI detalhado de liquidação do mapa."""
        if not settings.enable_discord_notifications:
            logger.info(f"[DISCORD DESATIVADO] Ignorando envio do mapa {dossier.game_id}")
            return {"sent": False, "reason": "Notificações desativadas"}

        webhook_url = get_league_webhook(dossier.league_slug)
        league_conf = get_league_config(dossier.league_slug)
        channel = league_conf.get("channel_name", "#geral")

        if not webhook_url:
            logger.warning(f"Nenhum webhook configurado para a liga {dossier.league_slug} ({channel})")
            return {"sent": False, "reason": "Webhook não configurado"}

        ansi_panel = DiscordFormatter.build_ansi_dossier(dossier)
        bot_name = league_conf.get("bot_username", "LIVE BET CORE Engine")
        color = league_conf.get("color", 5793266)

        payload = {
            "username": bot_name,
            "embeds": [
                {
                    "title": f"🎯 {dossier.match_title}",
                    "description": ansi_panel,
                    "color": color,
                    "footer": {
                        "text": "🛡️ Zero-Doubt Verification: 100% Auditado • Telemetria Oficial Riot Games"
                    }
                }
            ]
        }

        await self._rate_limit_wait()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(webhook_url, json=payload)
                if resp.status_code in (200, 204):
                    logger.info(f"🚀 [DISCORD ENVIADO] {dossier.match_title} publicado com sucesso em {channel}!")
                    return {"sent": True, "channel": channel, "status_code": resp.status_code}
                elif resp.status_code == 429:
                    retry_after = float(resp.headers.get("Retry-After", 2.0))
                    logger.warning(f"Rate limited pelo Discord. Aguardando {retry_after}s...")
                    await asyncio.sleep(retry_after)
                    retry_resp = await client.post(webhook_url, json=payload)
                    return {"sent": retry_resp.status_code in (200, 204), "channel": channel}
                else:
                    logger.error(f"Erro ao postar no Discord ({channel}): HTTP {resp.status_code} - {resp.text}")
                    return {"sent": False, "error": resp.text, "channel": channel}
        except Exception as e:
            logger.error(f"Exceção ao disparar webhook Discord: {e}")
            return {"sent": False, "error": str(e), "channel": channel}

    async def dispatch_series_summary(self, series: SeriesSummary) -> Dict[str, Any]:
        """Envia a súmula oficial de confronto/série MD1/MD3/MD5 (sem telemetria sintética)."""
        if not settings.enable_discord_notifications:
            return {"sent": False, "reason": "Notificações desativadas"}

        webhook_url = get_league_webhook(series.league_slug)
        league_conf = get_league_config(series.league_slug)
        channel = league_conf.get("channel_name", "#geral")

        if not webhook_url:
            return {"sent": False, "reason": "Webhook não configurado"}

        ansi_panel = DiscordFormatter.build_series_ansi_panel(series)
        bot_name = league_conf.get("bot_username", "LIVE BET CORE Engine")
        color = league_conf.get("color", 5793266)

        payload = {
            "username": bot_name,
            "embeds": [
                {
                    "title": f"🎯 [{series.league_name}] {series.team_blue_name} ({series.team_blue_code}) vs {series.team_red_name} ({series.team_red_code}) — SÉRIE FINALIZADA",
                    "description": ansi_panel,
                    "color": color,
                    "footer": {
                        "text": "🛡️ Súmula Oficial LoLEsports • 100% Dados Reais Auditados"
                    }
                }
            ]
        }

        await self._rate_limit_wait()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(webhook_url, json=payload)
                if resp.status_code in (200, 204):
                    logger.info(f"🚀 [DISCORD SÉRIE ENVIADA] {series.match_title} publicado em {channel}!")
                    return {"sent": True, "channel": channel}
                else:
                    logger.error(f"Erro ao postar série no Discord: HTTP {resp.status_code}")
                    return {"sent": False, "error": resp.text}
        except Exception as e:
            logger.error(f"Exceção ao postar série no Discord: {e}")
            return {"sent": False, "error": str(e)}
