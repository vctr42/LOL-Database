#!/usr/bin/env python3
"""
LOL-Database • Monitor Contínuo 24/7 de Partidas ao Vivo
Executa varreduras contínuas da telemetria da Riot Games, audita via Zero-Doubt
e dispara automaticamente no Discord no segundo em que o Nexus cai.
"""

import sys
import os
import time
import requests
from typing import Dict, Any, Set

# Configurar stdout para UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core.riot_feed import RiotFeedClient
from core.audit_gate import AuditGate
from core.settlement import SettlementCompiler
from core.database import DatabaseManager
from discord.embeds import DiscordFormatter
from discord.router import DiscordRouter
from core.riot_schedule_parser import RiotScheduleParser

class LiveGameMonitor:
    def __init__(self, interval_seconds: int = 15):
        self.interval = interval_seconds
        self.client = RiotFeedClient()
        self.db = DatabaseManager()
        self.processed_games: Set[str] = set()
        self._load_settled_games()

    def _load_settled_games(self):
        """Carrega IDs de mapas já liquidados para não duplicar."""
        try:
            settled = self.db.get_recent_settlements(limit=100)
            for s in settled:
                if "game_id" in s:
                    self.processed_games.add(str(s["game_id"]))
            print(f"[LiveMonitor] {len(self.processed_games)} mapas já liquidados no Data Lake.")
        except Exception as e:
            print(f"[LiveMonitor] Aviso ao carregar histórico: {e}")

    def settle_game(self, game_id: str, league_slug: str, league_name: str, game_number: int = 1, raw_window: Dict[str, Any] = None):
        """Executa auditoria e liquidação de um mapa finalizado."""
        if str(game_id) in self.processed_games:
            return

        print(f"\n⚡ [LIQUIDAÇÃO IDENTIFICADA] Auditando Mapa {game_number} ({game_id}) de [{league_name}]...")
        
        if not raw_window:
            raw_window = self.client.get_window(game_id)

        if "error" in raw_window:
            print(f"❌ Erro ao obter window da Riot CDN para {game_id}: {raw_window['error']}")
            return

        # 1. Zero-Doubt Gate
        audit = AuditGate.audit_game_window(raw_window)
        if not audit.passed:
            print(f"🛡️ Mapa {game_id} bloqueado pelo Zero-Doubt Gate: {audit.reasons}")
            return

        league_meta = {
            "league_slug": league_slug.lower(),
            "league_name": league_name.upper(),
            "game_number": game_number,
            "match_id": f"match_{league_slug}_{game_id}"
        }

        # 2. Compilar Dossiê
        dossier = SettlementCompiler.compile_from_window_and_details(raw_window, league_meta=league_meta)
        if not dossier:
            return

        yaml_text = DiscordFormatter.build_yaml_dossier(dossier)

        # 3. Salvar no Supabase & SQLite
        self.db.save_dossier(dossier, yaml_text, raw_window=raw_window)
        self.processed_games.add(str(game_id))

        # 4. Despachar no Discord
        res = DiscordRouter.dispatch_settlement(dossier)
        if res.get("sent"):
            print(f"🚀 [DISCORD ENVIADO] Dossiê publicado com sucesso em {res.get('channel')}!")
        else:
            print(f"⚠️ Erro ao despachar no Discord: {res.get('error') or res.get('reason')}")

    def start_polling(self):
        print("=" * 70)
        print("🚀 LOL-Database • MONITOR CONTÍNUO 24/7 ATIVO")
        print(f"⏱️  Intervalo de Varredura: {self.interval}s | Monitorando Ligas Oficiais...")
        print("=" * 70)

        while True:
            try:
                # 1. Buscar partidas reais agendadas e ao vivo
                matches = RiotScheduleParser.fetch_official_matches()
                if matches:
                    print(f"[{time.strftime('%H:%M:%S')}] {len(matches)} confrontos oficiais monitorados na Riot.")

                time.sleep(self.interval)
            except KeyboardInterrupt:
                print("\n🛑 Monitor finalizado pelo usuário.")
                break
            except Exception as e:
                print(f"⚠️ Erro no loop de monitoramento: {e}")
                time.sleep(self.interval)

if __name__ == "__main__":
    monitor = LiveGameMonitor(interval_seconds=15)
    monitor.start_polling()
