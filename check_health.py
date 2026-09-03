#!/usr/bin/env python3
"""
==============================================================================
LIVE BET CORE • Utilitário de Diagnóstico & Health Check Completo
==============================================================================
Testa os 5 pilares do sistema de ponta a ponta:
  1. Configuração & Variáveis de Ambiente
  2. Conectividade com Riot Games (Schedule & CDN)
  3. Persistência Dual (Supabase Cloud + SQLite Local)
  4. Motor de Auditoria Zero-Doubt & Compilador de Handicap
  5. Despacho & Formatação do Discord
"""

import sys
import asyncio
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

console = Console()

from config.settings import settings, LEAGUES_DATA, get_league_webhook
from core.client import AsyncRiotClient
from core.audit import ZeroDoubtGate
from core.compiler import SettlementCompiler
from database.repository import DatabaseRepository
from discord.formatters import DiscordFormatter

async def run_diagnostics():
    table = Table(title="🔍 DIAGNÓSTICO DO SISTEMA • LIVE BET CORE", show_lines=True)
    table.add_column("Pilar / Módulo", style="bold cyan", width=26)
    table.add_column("Status", width=12)
    table.add_column("Detalhes da Verificação", style="white")

    # 1. Configurações & Variáveis de Ambiente
    try:
        assert settings.supabase_url, "SUPABASE_URL não configurada"
        assert settings.supabase_anon_key, "SUPABASE_ANON_KEY não configurada"
        total_leagues = len([k for k in LEAGUES_DATA.keys() if k != "default"])
        table.add_row(
            "1. Configurações (.env)",
            "[bold green]✔ OK[/bold green]",
            f"Configurado com sucesso. {total_leagues} ligas oficiais mapeadas."
        )
    except Exception as e:
        table.add_row("1. Configurações (.env)", "[bold red]✖ ERRO[/bold red]", str(e))

    # 2. Conectividade com Supabase Cloud & SQLite Local
    repo = DatabaseRepository()
    try:
        cloud_ids = await repo.fetch_cloud_settled_ids()
        local_ids = repo.get_all_settled_ids()
        table.add_row(
            "2. Banco de Dados (Dual)",
            "[bold green]✔ OK[/bold green]",
            f"Supabase Cloud: {len(cloud_ids)} mapas sincronizados | SQLite Local: {len(local_ids)} mapas."
        )
    except Exception as e:
        table.add_row("2. Banco de Dados (Dual)", "[bold red]✖ ERRO[/bold red]", f"Falha de banco: {e}")

    # 3. Feed Oficial da Riot Games
    try:
        async with AsyncRiotClient() as riot_client:
            matches = await riot_client.fetch_schedule_matches()
            live_games = sum(len([g for g in m.games if g.state == "inProgress"]) for m in matches)
            completed = sum(1 for m in matches if m.is_completed)
            table.add_row(
                "3. Feed Riot Games",
                "[bold green]✔ OK[/bold green]",
                f"Conectado. {len(matches)} confrontos na agenda ({completed} concluídos, {live_games} mapa(s) ao vivo)."
            )
    except Exception as e:
        table.add_row("3. Feed Riot Games", "[bold red]✖ ERRO[/bold red]", f"Erro na Riot: {e}")

    # 4. Zero-Doubt Gate & Compilador de Handicap
    try:
        mock_window = {
            "frames": [
                {"rfc460Timestamp": "2026-08-25T14:00:00.000Z", "gameState": "in_game", "blueTeam": {"totalGold": 2500, "totalKills": 0, "towers": 0}, "redTeam": {"totalGold": 2500, "totalKills": 0, "towers": 0}},
                {"rfc460Timestamp": "2026-08-25T14:32:00.000Z", "gameState": "complete", "blueTeam": {"code": "PNG", "totalGold": 65000, "totalKills": 18, "towers": 9, "dragons": ["fire"]}, "redTeam": {"code": "VKS", "totalGold": 52000, "totalKills": 8, "towers": 2, "dragons": []}}
            ]
        }
        dossier = SettlementCompiler.compile_from_window_and_details(
            window_data=mock_window,
            league_meta={"league_slug": "cblol", "league_name": "CBLOL", "team_blue_code": "PNG", "team_red_code": "VKS"}
        )
        assert dossier is not None, "Falha na compilação do dossiê"
        assert "PNG até -9.5" in dossier.handicap_green_line, "Cálculo de handicap incorreto"
        table.add_row(
            "4. Zero-Doubt & Handicap",
            "[bold green]✔ OK[/bold green]",
            f"Compilação matemática validada. Linha de Green: '{dossier.handicap_green_line}'."
        )
    except Exception as e:
        table.add_row("4. Zero-Doubt & Handicap", "[bold red]✖ ERRO[/bold red]", f"Erro na auditoria: {e}")

    # 5. Discord Formatter & Webhook
    try:
        ansi = DiscordFormatter.build_ansi_dossier(dossier)
        assert "```ansi" in ansi and "🏆 VENCEDOR:" in ansi, "Falha na formatação ANSI"
        webhook = get_league_webhook("cblol")
        has_webhook = bool(webhook and "discord.com" in webhook)
        table.add_row(
            "5. Discord Webhooks",
            "[bold green]✔ OK[/bold green]" if has_webhook else "[bold yellow]⚠ PARCIAL[/bold yellow]",
            f"Layout ANSI formatado perfeitamente. Webhook CBLOL: {'Conectado' if has_webhook else 'Ausente'}."
        )
    except Exception as e:
        table.add_row("5. Discord Webhooks", "[bold red]✖ ERRO[/bold red]", str(e))

    console.print(table)

    if "--ping-discord" in sys.argv:
        console.print("\n[bold yellow]📡 Disparando card de teste para o Discord...[/bold yellow]")
        from discord.dispatcher import DiscordDispatcher
        disp = DiscordDispatcher()
        res = await disp.dispatch_map_dossier(dossier)
        if res.get("sent"):
            console.print(f"[bold green]✔ Card de teste enviado com sucesso para {res.get('channel')}![/bold green]")
        else:
            console.print(f"[bold red]✖ Falha ao enviar para o Discord: {res.get('error') or res.get('reason')}[/bold red]")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
    try:
        input("\n👉 Pressione ENTER para fechar a janela...")
    except (EOFError, KeyboardInterrupt):
        pass


