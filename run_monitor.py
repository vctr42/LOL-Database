#!/usr/bin/env python3
"""
==============================================================================
LIVE BET CORE • Motor Autônomo 24/7 de Telemetria e Liquidação de Apostas
==============================================================================
Arquitetura Assíncrona de Alta Fidelidade:
  - Ingestão contínua da CDN e Schedule Oficial da Riot Games
  - Zero-Doubt Verification Gate (100% Confiabilidade • Zero Dados Fictícios)
  - Despacho Multi-Canais Segmentado no Discord (Layout ANSI Padronizado)
  - Persistência Dual: Supabase Cloud PostgreSQL + Buffer Local SQLite
"""

import sys
import asyncio
import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Configurar stdout para UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config.settings import settings, LEAGUES_DATA
from core.client import AsyncRiotClient
from core.tracker import SettlementLedger
from core.compiler import SettlementCompiler
from database.repository import DatabaseRepository
from discord.dispatcher import DiscordDispatcher

console = Console()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
# Silenciar logs ruidosos de polling HTTP do httpx/httpcore
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger("LiveBetCore.Daemon")

class LiveBetDaemon:
    """Orquestrador principal 24/7 do Live Bet Core."""

    def __init__(self):
        self.repo = DatabaseRepository()
        self.ledger = SettlementLedger()
        self.dispatcher = DiscordDispatcher()
        self._running = False
        self._cycle_count = 0

    async def start(self):
        self._running = True
        self._print_startup_banner()

        # 1. Carregar Histórico do Data Lake (Bootstrap de Idempotência)
        cloud_ids = await self.repo.fetch_cloud_settled_ids()
        self.ledger.preload_from_database(cloud_ids)

        # 2. Inicializar Cliente Assíncrono da Riot Games
        async with AsyncRiotClient() as riot_client:
            # 3. Varredura Inicial de Blindagem Anti-Spam (Indexar o que já terminou)
            logger.info("Executando blindagem anti-spam de inicialização...")
            initial_matches = await riot_client.fetch_schedule_matches()
            for m in initial_matches:
                event_key = f"{m.league_slug}_{m.event_id}"
                self.ledger.register_known_event(event_key)
                if m.is_completed:
                    for g in m.games:
                        self.ledger.register_settled_id(g.game_id)
                    self.ledger.register_settled_id(f"riot_event_{m.event_id}")

            self.ledger.finish_bootstrap()

            # 4. Loop de Monitoramento Contínuo
            while self._running:
                try:
                    await self._scan_cycle(riot_client)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Erro no ciclo de monitoramento: {e}", exc_info=True)

                await asyncio.sleep(settings.monitor_interval_seconds)

        logger.info("LIVE BET CORE finalizado com sucesso.")

    async def _scan_cycle(self, riot_client: AsyncRiotClient):
        """Executa um ciclo completo de varredura e liquidação cirúrgica."""
        self._cycle_count += 1
        matches = await riot_client.fetch_schedule_matches()
        if not matches:
            return

        live_maps_count = 0

        for match in matches:
            event_key = f"{match.league_slug}_{match.event_id}"

            # Caso 1: Monitoramento de mapas reais com stream ativo (inProgress ou recém-finalizados)
            for game_ref in match.games:
                # Se o mapa não começou ou não precisa ser jogado, ignorar consulta CDN
                if game_ref.state not in ("inProgress", "completed"):
                    continue

                if self.ledger.is_settled(game_ref.game_id):
                    continue

                if game_ref.state == "inProgress":
                    live_maps_count += 1

                # Consultar stream de telemetria apenas para mapas elegíveis
                window_data = await riot_client.get_window(game_ref.game_id)
                if window_data and "frames" in window_data and len(window_data["frames"]) > 1:
                    details_data = await riot_client.get_details(game_ref.game_id)
                    
                    league_meta = {
                        "game_id": game_ref.game_id,
                        "match_id": f"match_{match.league_slug}_{match.event_id}",
                        "league_slug": match.league_slug,
                        "league_name": match.league_name,
                        "game_number": game_ref.number,
                        "team_blue_name": match.team_blue_name,
                        "team_blue_code": match.team_blue_code,
                        "team_red_name": match.team_red_name,
                        "team_red_code": match.team_red_code,
                        "winner_side": match.winner_side
                    }

                    # Compilar estritamente via Zero-Doubt Verification Gate
                    dossier = SettlementCompiler.compile_from_window_and_details(
                        window_data=window_data,
                        details_data=details_data,
                        league_meta=league_meta
                    )

                    if dossier:
                        logger.info(f"⚡ [MAPA AUDITADO] Liquidando: {dossier.match_title}...")
                        from discord.formatters import DiscordFormatter
                        yaml_text = DiscordFormatter.build_yaml_dossier(dossier)
                        
                        # Salvar no Data Lake
                        await self.repo.save_dossier(dossier, yaml_text)
                        
                        # Despachar no Discord
                        await self.dispatcher.dispatch_map_dossier(dossier)
                        
                        # Registrar no ledger
                        self.ledger.register_settled_id(game_ref.game_id)

            # Caso 2: Nova Série Oficial Concluída que ainda não foi registrada
            if match.is_completed and not self.ledger.is_known_event(event_key):
                logger.info(f"🏆 [SÉRIE CONCLUÍDA] {match.match_title} ({match.winner_code} Venceu)")
                await self.repo.save_series_summary(match)
                await self.dispatcher.dispatch_series_summary(match)
                self.ledger.register_known_event(event_key)

        # Log periódico a cada 6 ciclos (a cada ~1 minuto)
        if self._cycle_count % 6 == 1:
            logger.info(f"Varredura em execução: {len(matches)} confrontos na agenda • {live_maps_count} mapa(s) ao vivo • {self.ledger.total_settled} mapas liquidados no Data Lake")

    def stop(self):
        self._running = False

    def _print_startup_banner(self):
        banner_table = Table(show_header=False, box=None, padding=(0, 2))
        banner_table.add_row("[bold cyan]Banco de Dados:[/bold cyan]", f"[green]{settings.db_mode.upper()}[/green] (PostgreSQL Supabase + SQLite)")
        banner_table.add_row("[bold cyan]Notificações Discord:[/bold cyan]", f"[green]{'ATIVAS' if settings.enable_discord_notifications else 'DESATIVADAS'}[/green]")
        banner_table.add_row("[bold cyan]Ligas Monitoradas:[/bold cyan]", ", ".join([cfg["name"] for cfg in LEAGUES_DATA.values() if cfg["name"] != "Geral"]))
        banner_table.add_row("[bold cyan]Intervalo de Varredura:[/bold cyan]", f"[yellow]{settings.monitor_interval_seconds} segundos[/yellow]")

        console.print(Panel(
            banner_table,
            title="[bold green]🎮 LIVE BET CORE • TELEMETRIA & LIQUIDAÇÃO 24/7[/bold green]",
            subtitle="[dim]Zero Synthetic Data • In-Game Clock Estrito • Data Lake[/dim]",
            border_style="bright_blue"
        ))

async def main():
    daemon = LiveBetDaemon()
    try:
        await daemon.start()
    except (KeyboardInterrupt, SystemExit):
        daemon.stop()

if __name__ == "__main__":
    asyncio.run(main())
