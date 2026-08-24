import requests
from typing import Dict, Any, Optional
from config.settings import LEAGUE_CONFIG, get_league_webhook, ENABLE_DISCORD_NOTIFICATIONS
from core.settlement import SettlementDossier
from discord.embeds import DiscordFormatter

class DiscordRouter:
    """Roteador inteligente de envio para canais e bots temáticos do Discord."""

    @classmethod
    def dispatch_settlement(cls, dossier: SettlementDossier) -> Dict[str, Any]:
        """
        Envia o relatório para o canal correto de acordo com a liga da partida.
        Se notificações estiverem desativadas, apenas simula e retorna sucesso.
        """
        league_slug = dossier.league_slug.lower()
        league_info = LEAGUE_CONFIG.get(league_slug, LEAGUE_CONFIG.get("default", {}))
        webhook_url = get_league_webhook(league_slug)

        yaml_text = DiscordFormatter.build_yaml_dossier(dossier)
        payload = DiscordFormatter.build_discord_payload(dossier, league_info)

        if not ENABLE_DISCORD_NOTIFICATIONS or not webhook_url:
            return {
                "sent": False,
                "reason": "Notificações desativadas ou Webhook URL não configurada",
                "league": league_slug,
                "channel": league_info.get("channel_name", "#geral"),
                "yaml_dossier": yaml_text
            }

        try:
            response = requests.post(webhook_url, json=payload, timeout=8)
            response.raise_for_status()
            return {
                "sent": True,
                "status_code": response.status_code,
                "league": league_slug,
                "channel": league_info.get("channel_name", "#geral"),
                "yaml_dossier": yaml_text
            }
        except Exception as e:
            return {
                "sent": False,
                "error": str(e),
                "league": league_slug,
                "channel": league_info.get("channel_name", "#geral"),
                "yaml_dossier": yaml_text
            }
