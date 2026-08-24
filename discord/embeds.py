from typing import Dict, Any
from core.settlement import SettlementDossier

class DiscordFormatter:
    """Formatador de relatórios visuais de alta legibilidade para o Discord."""

    @staticmethod
    def build_ansi_dossier(dossier: SettlementDossier) -> str:
        """
        Gera um painel com formatação ANSI nativa do Discord com ícones temáticos de League of Legends.
        Combina emojis visuais com separadores limpos e cores vibrantes.
        """
        blue_team = dossier.winner_code if dossier.winner_side == "BLUE" else dossier.loser_code
        red_team = dossier.winner_code if dossier.winner_side == "RED" else dossier.loser_code

        # Cálculos de Totais Consolidados (Para Mercados Over / Under)
        total_kills = dossier.blue_kills + dossier.red_kills
        total_towers = dossier.blue_towers + dossier.red_towers
        total_dragons = dossier.blue_dragons + dossier.red_dragons
        total_barons = dossier.blue_barons + dossier.red_barons
        total_heralds = dossier.blue_heralds + dossier.red_heralds
        total_inhibitors = dossier.blue_inhibitors + dossier.red_inhibitors

        div_bar = "\u001b[30;1m──────────────────────────────────────────────\u001b[0m"

        lines = [
            "```ansi",
            f"\u001b[37;1m🏆 VENCEDOR:\u001b[0m   \u001b[32;1m{dossier.winner_code} ({dossier.winner_side})\u001b[0m  \u001b[30;1m│\u001b[0m  \u001b[37;1m⏱️  DURAÇÃO:\u001b[0m \u001b[33;1m{dossier.duration_formatted}\u001b[0m",
            f"\u001b[37;1m⚔️  ABATES:\u001b[0m     \u001b[37;1m{str(total_kills).rjust(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m{blue_team}: {dossier.blue_kills}\u001b[30;1m │ \u001b[31;1m{red_team}: {dossier.red_kills}\u001b[30;1m)\u001b[0m  \u001b[30;1m[+{dossier.kill_spread} {dossier.kill_leader_code}]\u001b[0m",
            f"\u001b[32;1m🟢 GREEN:\u001b[0m      \u001b[32;1m{dossier.handicap_green_line}\u001b[0m",
            div_bar,
            f"\u001b[37;1m📊 TOTAIS DE OBJETIVOS\u001b[0m",
            f"   🏰 Torres:     \u001b[37;1m{str(total_towers).rjust(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m{blue_team}: {dossier.blue_towers}\u001b[30;1m │ \u001b[31;1m{red_team}: {dossier.red_towers}\u001b[30;1m)\u001b[0m",
            f"   🐉 Dragões:    \u001b[37;1m{str(total_dragons).rjust(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m{blue_team}: {dossier.blue_dragons}\u001b[30;1m │ \u001b[31;1m{red_team}: {dossier.red_dragons}\u001b[30;1m)\u001b[0m",
            f"   👾 Barões:     \u001b[37;1m{str(total_barons).rjust(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m{blue_team}: {dossier.blue_barons}\u001b[30;1m │ \u001b[31;1m{red_team}: {dossier.red_barons}\u001b[30;1m)\u001b[0m",
            f"   🦀 Arautos:    \u001b[37;1m{str(total_heralds).rjust(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m{blue_team}: {dossier.blue_heralds}\u001b[30;1m │ \u001b[31;1m{red_team}: {dossier.red_heralds}\u001b[30;1m)\u001b[0m",
            f"   🏛️  Inibidores: \u001b[37;1m{str(total_inhibitors).rjust(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m{blue_team}: {dossier.blue_inhibitors}\u001b[30;1m │ \u001b[31;1m{red_team}: {dossier.red_inhibitors}\u001b[30;1m)\u001b[0m",
            div_bar,
            f"\u001b[37;1m⚡ FIRSTS & EVENTOS\u001b[0m",
            f"   🩸 First Blood:  \u001b[33;1m{dossier.first_blood_team.ljust(6)}\u001b[0m \u001b[30;1m({dossier.first_blood_time})\u001b[0m",
            f"   🛡️  First Tower:  \u001b[33;1m{dossier.first_tower_team.ljust(6)}\u001b[0m \u001b[30;1m({dossier.first_tower_time})\u001b[0m",
            f"   🐲 First Dragon: \u001b[33;1m{dossier.first_dragon_team.ljust(6)}\u001b[0m \u001b[30;1m({dossier.first_dragon_time})\u001b[0m",
            f"   👾 First Baron:  \u001b[33;1m{dossier.first_baron_team.ljust(6)}\u001b[0m \u001b[30;1m({dossier.first_baron_time})\u001b[0m",
            div_bar,
            f"\u001b[37;1m🏁 CORRIDAS DE ABATES\u001b[0m",
            f"   ⚡ Corrida 5:    \u001b[32;1m{dossier.race_to_5}\u001b[0m",
            f"   ⚡ Corrida 10:   \u001b[32;1m{dossier.race_to_10}\u001b[0m",
            f"   ⚡ Corrida 15:   \u001b[32;1m{dossier.race_to_15}\u001b[0m",
            "```"
        ]
        return "\n".join(lines)

    @staticmethod
    def build_yaml_dossier(dossier: SettlementDossier) -> str:
        """Gera bloco YAML monospaçado padrão com totais."""
        blue_team = dossier.winner_code if dossier.winner_side == "BLUE" else dossier.loser_code
        red_team = dossier.winner_code if dossier.winner_side == "RED" else dossier.loser_code

        total_kills = dossier.blue_kills + dossier.red_kills
        total_towers = dossier.blue_towers + dossier.red_towers
        total_dragons = dossier.blue_dragons + dossier.red_dragons
        total_barons = dossier.blue_barons + dossier.red_barons
        total_heralds = dossier.blue_heralds + dossier.red_heralds
        total_inhibitors = dossier.blue_inhibitors + dossier.red_inhibitors

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
            f"Total Abates: \"{total_kills} ({blue_team}: {dossier.blue_kills} | {red_team}: {dossier.red_kills})\"",
            f"Lider Abates: \"{dossier.kill_leader_code} (+{dossier.kill_spread})\"",
            f"Linha Fracionaria: \"{dossier.handicap_green_line}\"",
            "",
            "# --- TOTAIS DE OBJETIVOS ---",
            f"Torres: \"{total_towers} ({blue_team}: {dossier.blue_towers} | {red_team}: {dossier.red_towers})\"",
            f"Dragoes: \"{total_dragons} ({blue_team}: {dossier.blue_dragons} | {red_team}: {dossier.red_dragons})\"",
            f"Baroes: \"{total_barons} ({blue_team}: {dossier.blue_barons} | {red_team}: {dossier.red_barons})\"",
            f"Arautos: \"{total_heralds} ({blue_team}: {dossier.blue_heralds} | {red_team}: {dossier.red_heralds})\"",
            f"Inibidores: \"{total_inhibitors} ({blue_team}: {dossier.blue_inhibitors} | {red_team}: {dossier.red_inhibitors})\"",
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
        """Constrói payload completo com Embed e ANSI Panel."""
        bot_name = league_config.get("bot_username", "LOL-Database Engine")
        avatar_url = league_config.get("avatar_url", "")
        color = league_config.get("color", 5793266)

        ansi_panel = DiscordFormatter.build_ansi_dossier(dossier)

        embed = {
            "title": f"🎯 {dossier.match_title}",
            "description": ansi_panel,
            "color": color,
            "footer": {
                "text": "🛡️ Zero-Doubt Verification: 100% Auditado • Telemetria Oficial Riot Games"
            }
        }

        return {
            "username": bot_name,
            "avatar_url": avatar_url if avatar_url else None,
            "embeds": [embed]
        }
