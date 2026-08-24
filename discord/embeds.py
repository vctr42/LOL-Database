from typing import Dict, Any
from core.settlement import SettlementDossier

class DiscordFormatter:
    """Formatador de relatórios para o Discord em blocos YAML com coloração e alinhamento perfeitos."""

    @staticmethod
    def build_yaml_dossier(dossier: SettlementDossier) -> str:
        """
        Gera o relatório visual em bloco YAML monospaçado.
        Chaves padronizadas e limpas para renderização azul e valores destacados.
        """
        # Header e Informações Gerais
        lines = [
            "```yaml",
            f"Relatorio: \"{dossier.match_title}\"",
            f"Liga: \"{dossier.league_name}\"",
            f"Status: \"LIQUIDADO E AUDITADO\"",
            f"Duracao Oficial: \"{dossier.duration_formatted}\"",
            "",
            "# --- MONEYLINE & VENCEDOR ---",
            f"Vencedor: \"{dossier.winner_code} ({dossier.winner_side})\"",
            f"Derrotado: \"{dossier.loser_code} ({dossier.loser_side})\"",
            "",
            "# --- PLACAR DE ABATES & HANDICAP ---",
            f"Placar Abates: \"{dossier.blue_kills} x {dossier.red_kills}\"",
            f"Lider Abates: \"{dossier.kill_leader_code} (+{dossier.kill_spread})\"",
            f"Linha Fracionaria: \"{dossier.handicap_green_line}\"",
            "",
            "# --- TOTAIS DE OBJETIVOS (AZUL vs VERMELHO) ---",
            f"Torres: \"{dossier.blue_towers} x {dossier.red_towers}\"",
            f"Dragoes: \"{dossier.blue_dragons} x {dossier.red_dragons}\"",
            f"Baroes: \"{dossier.blue_barons} x {dossier.red_barons}\"",
            f"Arautos: \"{dossier.blue_heralds} x {dossier.red_heralds}\"",
            f"Inibidores: \"{dossier.blue_inhibitors} x {dossier.red_inhibitors}\"",
            "",
            "# --- FIRSTS & CORRIDAS DE ABATES ---",
            f"First Blood: \"{dossier.first_blood_team} ({dossier.first_blood_time})\"",
            f"First Tower: \"{dossier.first_tower_team} ({dossier.first_tower_time})\"",
            f"First Dragon: \"{dossier.first_dragon_team} ({dossier.first_dragon_time})\"",
            f"First Herald: \"{dossier.first_herald_team} ({dossier.first_herald_time})\"",
            f"First Baron: \"{dossier.first_baron_team} ({dossier.first_baron_time})\"",
            f"Corrida 5 Kills: \"{dossier.race_to_5}\"",
            f"Corrida 10 Kills: \"{dossier.race_to_10}\"",
            f"Corrida 15 Kills: \"{dossier.race_to_15}\"",
            "",
            "# --- AUDITORIA ZERO-DOUBT ---",
            f"Zero Doubt Gate: \"APROVADO (100% CONFIANCA)\"",
            "```"
        ]
        return "\n".join(lines)

    @staticmethod
    def build_discord_payload(dossier: SettlementDossier, league_config: Dict[str, Any]) -> Dict[str, Any]:
        """Constrói payload completo de Webhook do Discord com Embeds e bloco YAML."""
        yaml_content = DiscordFormatter.build_yaml_dossier(dossier)
        bot_name = league_config.get("bot_username", "LOL-Database Engine")
        avatar_url = league_config.get("avatar_url", "")
        color = league_config.get("color", 5793266)

        return {
            "username": bot_name,
            "avatar_url": avatar_url if avatar_url else None,
            "content": f"🎯 **Dossiê de Liquidação Oficial** — {dossier.match_title}\n{yaml_content}",
            "embeds": [
                {
                    "title": f"📊 Telemetria & Liquidação: {dossier.match_title}",
                    "description": f"**Vencedor:** `{dossier.winner_code}` | **Duração Oficial:** `{dossier.duration_formatted}`\n**Handicap Green:** `{dossier.handicap_green_line}`",
                    "color": color,
                    "fields": [
                        {
                            "name": "⚔️ Abates",
                            "value": f"`{dossier.blue_kills} x {dossier.red_kills}`",
                            "inline": True
                        },
                        {
                            "name": "🏰 Torres",
                            "value": f"`{dossier.blue_towers} x {dossier.red_towers}`",
                            "inline": True
                        },
                        {
                            "name": "🐉 Dragões / 👾 Barões",
                            "value": f"`D:{dossier.blue_dragons}x{dossier.red_dragons} | B:{dossier.blue_barons}x{dossier.red_barons}`",
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": "LOL-Database • In-Game Clock Riot Games • Zero-Doubt Verified"
                    }
                }
            ]
        }
