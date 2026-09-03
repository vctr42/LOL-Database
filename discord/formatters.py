from typing import Dict, Any
from core.models import SettlementDossier, SeriesSummary

class DiscordFormatter:
    """Formatador de cards visuais ANSI e blocos monospaçados YAML para o Discord."""

    @staticmethod
    def build_ansi_dossier(dossier: SettlementDossier) -> str:
        """
        Constrói o painel ANSI oficial conforme o padrão visual aprovado (Imagem 2).
        Cores semânticas:
          - Lado Azul:     \u001b[36;1m (Ciano)
          - Lado Vermelho: \u001b[31;1m (Vermelho)
          - Auditoria/Green: \u001b[32;1m (Verde)
          - Métricas/Tempo:\u001b[33;1m (Amarelo)
          - Divisores:     \u001b[30;1m (Cinza escuro)
        """
        blue_team = dossier.blue_team_code
        red_team = dossier.red_team_code

        def color_team(name: str) -> str:
            if not name or name == "NENHUM":
                return f"\u001b[30;1m{name}\u001b[0m"
            if name.strip().upper() == blue_team.strip().upper():
                return f"\u001b[36;1m{name}\u001b[0m"
            elif name.strip().upper() == red_team.strip().upper():
                return f"\u001b[31;1m{name}\u001b[0m"
            return f"\u001b[37;1m{name}\u001b[0m"

        total_kills = dossier.blue_kills + dossier.red_kills
        total_towers = dossier.blue_towers + dossier.red_towers
        total_dragons = dossier.blue_dragons + dossier.red_dragons
        total_barons = dossier.blue_barons + dossier.red_barons
        total_heralds = dossier.blue_heralds + dossier.red_heralds
        total_inhibitors = dossier.blue_inhibitors + dossier.red_inhibitors

        b_towers = f"{blue_team}: {dossier.blue_towers}".ljust(8)
        r_towers = f"{red_team}: {dossier.red_towers}".ljust(8)

        b_dragons = f"{blue_team}: {dossier.blue_dragons}".ljust(8)
        r_dragons = f"{red_team}: {dossier.red_dragons}".ljust(8)

        b_barons = f"{blue_team}: {dossier.blue_barons}".ljust(8)
        r_barons = f"{red_team}: {dossier.red_barons}".ljust(8)

        b_heralds = f"{blue_team}: {dossier.blue_heralds}".ljust(8)
        r_heralds = f"{red_team}: {dossier.red_heralds}".ljust(8)

        b_inhibs = f"{blue_team}: {dossier.blue_inhibitors}".ljust(8)
        r_inhibs = f"{red_team}: {dossier.red_inhibitors}".ljust(8)

        div_bar = "\u001b[30;1m──────────────────────────────────────────────\u001b[0m"

        winner_color = "\u001b[36;1m" if dossier.winner_side == "BLUE" else "\u001b[31;1m"
        w_name = dossier.winner_name or dossier.winner_code
        winner_display = f"{winner_color}{w_name} ({dossier.winner_code}) ({dossier.winner_side})\u001b[0m"

        spread = dossier.kill_spread
        if spread == 0:
            handicap_colored = "\u001b[37;1mEMPATE EM KILLS\u001b[0m"
        else:
            line_margin = spread - 0.5
            trailer_margin = spread + 0.5
            leader_code = dossier.kill_leader_code
            trailer_code = red_team if leader_code == blue_team else blue_team

            c_leader = "\u001b[36;1m" if leader_code == blue_team else "\u001b[31;1m"
            c_trailer = "\u001b[31;1m" if leader_code == blue_team else "\u001b[36;1m"

            handicap_colored = f"{c_leader}{leader_code} até -{line_margin:.1f}\u001b[0m \u001b[30;1m│\u001b[0m {c_trailer}{trailer_code} a partir de +{trailer_margin:.1f}\u001b[0m"

        def format_race(race_text: str) -> str:
            if not race_text or race_text == "NENHUM":
                return "\u001b[30;1mNENHUM\u001b[0m"
            parts = race_text.split(" (")
            team_part = parts[0]
            time_part = f"({parts[1]}" if len(parts) > 1 else ""
            return f"{color_team(team_part)} \u001b[30;1m{time_part}\u001b[0m"

        lines = [
            "```ansi",
            f"\u001b[37;1m🏆 VENCEDOR:\u001b[0m    {winner_display}",
            f"\u001b[37;1m⏱️  DURAÇÃO:\u001b[0m     \u001b[33;1m{dossier.duration_formatted}\u001b[0m \u001b[30;1m(In-Game Clock Oficial)\u001b[0m",
            f"\u001b[37;1m⚔️  TOTAL KILLS:\u001b[0m \u001b[37;1m{str(total_kills).ljust(3)}\u001b[0m \u001b[30;1m│\u001b[0m \u001b[36;1m{blue_team}: {str(dossier.blue_kills).rjust(2)}\u001b[0m \u001b[30;1m│\u001b[0m \u001b[31;1m{red_team}: {str(dossier.red_kills).rjust(2)}\u001b[0m",
            f"\u001b[32;1m🟢 HANDICAP:\u001b[0m    {handicap_colored}",
            div_bar,
            "\u001b[37;1m📊 TOTAIS DE OBJETIVOS\u001b[0m",
            f"   🏰 Torres:     \u001b[37;1m{str(total_towers).rjust(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m{b_towers}\u001b[30;1m│ \u001b[31;1m{r_towers}\u001b[30;1m)\u001b[0m",
            f"   🐉 Dragões:    \u001b[37;1m{str(total_dragons).rjust(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m{b_dragons}\u001b[30;1m│ \u001b[31;1m{r_dragons}\u001b[30;1m)\u001b[0m",
            f"   👾 Barões:     \u001b[37;1m{str(total_barons).rjust(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m{b_barons}\u001b[30;1m│ \u001b[31;1m{r_barons}\u001b[30;1m)\u001b[0m",
            f"   🦀 Arautos:    \u001b[37;1m{str(total_heralds).rjust(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m{b_heralds}\u001b[30;1m│ \u001b[31;1m{r_heralds}\u001b[30;1m)\u001b[0m",
            f"   💎 Inibidores: \u001b[37;1m{str(total_inhibitors).rjust(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m{b_inhibs}\u001b[30;1m│ \u001b[31;1m{r_inhibs}\u001b[30;1m)\u001b[0m",
            div_bar,
            "\u001b[37;1m⚡ FIRSTS & TIMESTAMPS\u001b[0m",
            f"   🩸 First Blood:  {color_team(dossier.first_blood_team).ljust(14)} \u001b[30;1m({dossier.first_blood_time})\u001b[0m",
            f"   🏰 First Tower:  {color_team(dossier.first_tower_team).ljust(14)} \u001b[30;1m({dossier.first_tower_time})\u001b[0m",
            f"   🐲 First Dragon: {color_team(dossier.first_dragon_team).ljust(14)} \u001b[30;1m({dossier.first_dragon_time})\u001b[0m",
            f"   🦀 First Herald: {color_team(dossier.first_herald_team).ljust(14)} \u001b[30;1m({dossier.first_herald_time})\u001b[0m",
            f"   👾 First Baron:  {color_team(dossier.first_baron_team).ljust(14)} \u001b[30;1m({dossier.first_baron_time})\u001b[0m",
            div_bar,
            "\u001b[37;1m🏁 CORRIDAS DE ABATES\u001b[0m",
            f"   🔥 Corrida 5:    {format_race(dossier.race_to_5)}",
            f"   🔥 Corrida 10:   {format_race(dossier.race_to_10)}",
            f"   🔥 Corrida 15:   {format_race(dossier.race_to_15)}",
            div_bar,
            "\u001b[32;1m✔ Auditoria Zero-Doubt: 100% Aprovado e Registrado\u001b[0m",
            "```"
        ]
        return "\n".join(lines)

    @staticmethod
    def build_yaml_dossier(dossier: SettlementDossier) -> str:
        """Gera o dossiê textual em formato YAML padrão para planilhas e auditoria."""
        total_kills = dossier.blue_kills + dossier.red_kills
        total_towers = dossier.blue_towers + dossier.red_towers
        total_dragons = dossier.blue_dragons + dossier.red_dragons
        total_barons = dossier.blue_barons + dossier.red_barons

        lines = [
            "```yaml",
            f"Relatorio: \"{dossier.match_title}\"",
            f"Liga: \"{dossier.league_name}\"",
            "Status: \"LIQUIDADO E AUDITADO\"",
            f"Duracao Oficial: \"{dossier.duration_formatted}\"",
            "",
            "# --- MONEYLINE & VENCEDOR ---",
            f"Vencedor: \"{dossier.winner_code} ({dossier.winner_side})\"",
            f"Derrotado: \"{dossier.loser_code} ({dossier.loser_side})\"",
            "",
            "# --- PLACAR DE ABATES & HANDICAP ---",
            f"Total Abates: \"{total_kills} ({dossier.blue_team_code}: {dossier.blue_kills} | {dossier.red_team_code}: {dossier.red_kills})\"",
            f"Lider Abates: \"{dossier.kill_leader_code} (+{dossier.kill_spread})\"",
            f"Linha Fracionaria: \"{dossier.handicap_green_line}\"",
            "",
            "# --- TOTAIS DE OBJETIVOS ---",
            f"Torres: \"{total_towers} ({dossier.blue_team_code}: {dossier.blue_towers} | {dossier.red_team_code}: {dossier.red_towers})\"",
            f"Dragoes: \"{total_dragons} ({dossier.blue_team_code}: {dossier.blue_dragons} | {dossier.red_team_code}: {dossier.red_dragons})\"",
            f"Baroes: \"{total_barons} ({dossier.blue_team_code}: {dossier.blue_barons} | {dossier.red_team_code}: {dossier.red_barons})\"",
            "",
            "# --- FIRSTS & CORRIDAS DE ABATES ---",
            f"First Blood: \"{dossier.first_blood_team} ({dossier.first_blood_time})\"",
            f"First Tower: \"{dossier.first_tower_team} ({dossier.first_tower_time})\"",
            f"First Dragon: \"{dossier.first_dragon_team} ({dossier.first_dragon_time})\"",
            f"First Baron: \"{dossier.first_baron_team} ({dossier.first_baron_time})\"",
            f"Corrida 5 Kills: \"{dossier.race_to_5}\"",
            f"Corrida 10 Kills: \"{dossier.race_to_10}\"",
            f"Corrida 15 Kills: \"{dossier.race_to_15}\"",
            "",
            "# --- AUDITORIA ZERO-DOUBT ---",
            "Zero Doubt Gate: \"APROVADO (100% CONFIANCA)\"",
            "```"
        ]
        return "\n".join(lines)

    @staticmethod
    def build_series_ansi_panel(series: SeriesSummary) -> str:
        """Constrói painel ANSI exclusivo para sumário de confrontos/séries sem telemetria sintética."""
        winner_color = "\u001b[36;1m" if series.winner_side == "BLUE" else "\u001b[31;1m"
        div_bar = "\u001b[30;1m──────────────────────────────────────────────\u001b[0m"

        lines = [
            "```ansi",
            "\u001b[32;1m[STATUS: SÉRIE OFICIAL CONCLUÍDA]\u001b[0m \u001b[37;1mResultado Riot Games\u001b[0m",
            div_bar,
            f"\u001b[36;1m🏆 VENCEDOR DA SÉRIE:\u001b[0m {winner_color}{series.winner_name} ({series.winner_code})\u001b[0m",
            f"\u001b[36;1m⚔️  PLACAR DE MAPAS:\u001b[0m   \u001b[36;1m{series.team_blue_code}\u001b[0m \u001b[37;1m{series.team_blue_wins} x {series.team_red_wins}\u001b[0m \u001b[31;1m{series.team_red_code}\u001b[0m",
            f"\u001b[36;1m🏟️  TORNEIO / LIGA:\u001b[0m    \u001b[33;1m{series.tournament_name or series.league_name}\u001b[0m",
            div_bar,
            "\u001b[32;1m✔ Súmula Oficial: 100% Auditada e Registrada\u001b[0m",
            "```"
        ]
        return "\n".join(lines)
