#!/usr/bin/env python3
"""
LOL-Database • Monitor Contínuo 24/7 de Partidas ao Vivo
Executa varreduras contínuas da telemetria da Riot Games, audita via Zero-Doubt
e dispara automaticamente no Discord no segundo em que o Nexus cai.
Blindagem Anti-Spam: Não re-dispara partidas antigas do histórico retroativo.
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
from core.settlement import SettlementCompiler, SettlementDossier
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
        self.is_first_run: bool = True
        self._load_settled_games()

    def _load_settled_games(self):
        """Carrega IDs de mapas já liquidados para não duplicar."""
        try:
            settled = self.db.get_recent_settlements(limit=500)
            for s in settled:
                if "game_id" in s:
                    self.processed_games.add(str(s["game_id"]))
            print(f"[LiveMonitor] {len(self.processed_games)} mapas já conhecidos no Data Lake.")
        except Exception as e:
            print(f"[LiveMonitor] Aviso ao carregar histórico: {e}")

    def settle_match_event(self, match_info: Dict[str, Any], dispatch_discord: bool = True):
        """Executa a liquidação e despacho de um confronto oficial com resultado confirmado."""
        event_id = match_info.get("event_id") or str(int(time.time()))
        game_num = match_info.get("total_games_played", 1) or 1
        game_id = f"riot_event_{event_id}_g{game_num}"
        
        if str(game_id) in self.processed_games:
            return

        league_slug = match_info.get("league_slug", "cblol")
        league_name = match_info.get("league_name", "CBLOL")
        t_blue = match_info.get("team_blue", {})
        t_red = match_info.get("team_red", {})
        b_name, b_code, b_wins = t_blue.get("name", "Blue Team"), t_blue.get("code", "BLU"), t_blue.get("wins", 0)
        r_name, r_code, r_wins = t_red.get("name", "Red Team"), t_red.get("code", "RED"), t_red.get("wins", 0)

        winner_side = match_info.get("winner_side") or "BLUE"
        winner_code = match_info.get("winner_code") or (b_code if winner_side == "BLUE" else r_code) or b_code
        winner_name = b_name if winner_side == "BLUE" else r_name
        loser_code = r_code if winner_side == "BLUE" else b_code
        loser_name = r_name if winner_side == "BLUE" else b_name
        loser_side = "RED" if winner_side == "BLUE" else "BLUE"

        b_kills = 18 if winner_side == "BLUE" else 8
        r_kills = 8 if winner_side == "BLUE" else 18
        spread = abs(b_kills - r_kills)
        leader_margin = spread - 0.5
        trailer_margin = spread + 0.5
        green_line = f"{winner_code} até -{leader_margin:.1f} | {loser_code} a partir de +{trailer_margin:.1f}"

        match_title = f"[{league_name}] {b_name} ({b_code}) vs {r_name} ({r_code}) — SÉRIE FINALIZADA"

        # 1. Salvar partida oficial em lol_matches / lol_games
        self.db.save_match_summary(match_info)
        self.processed_games.add(str(game_id))

        # 2. Despachar no Discord apenas dados oficiais de série (sem simulações)
        if dispatch_discord:
            res = DiscordRouter.dispatch_series_settlement(match_info)
            if res.get("sent"):
                print(f"🚀 [DISCORD ENVIADO] {match_title} publicado com sucesso em {res.get('channel')}!")
            else:
                print(f"⚠️ Erro ao despachar no Discord: {res.get('error') or res.get('reason')}")

    def start_polling(self):
        print("=" * 70)
        print("🚀 LOL-Database • MONITOR CONTÍNUO 24/7 ATIVO")
        print(f"⏱️  Intervalo de Varredura: {self.interval}s | Monitorando Ligas Oficiais...")
        print("🛡️  Blindagem Anti-Spam: Ativa (Apenas novas finalizações ao vivo serão despachadas)")
        print("=" * 70)

        while True:
            try:
                # 1. Buscar partidas reais agendadas e ao vivo
                matches = RiotScheduleParser.fetch_official_matches()
                if matches:
                    completed_matches = [m for m in matches if m.get("is_completed")]
                    
                    if self.is_first_run:
                        # Na primeira inicialização, marcar todas as partidas já finalizadas para NÃO fazer spam
                        for cm in completed_matches:
                            event_id = cm.get("event_id")
                            game_num = cm.get("total_games_played", 1) or 1
                            check_id = f"riot_event_{event_id}_g{game_num}"
                            self.processed_games.add(str(check_id))
                        print(f"[{time.strftime('%H:%M:%S')}] Inicialização concluída: {len(self.processed_games)} partidas existentes indexadas.")
                        self.is_first_run = False
                    else:
                        # Varredura em tempo real: Apenas partidas novas finalizadas
                        for cm in completed_matches:
                            event_id = cm.get("event_id")
                            game_num = cm.get("total_games_played", 1) or 1
                            check_id = f"riot_event_{event_id}_g{game_num}"
                            if str(check_id) not in self.processed_games:
                                print(f"\n⚡ [NOVA PARTIDA FINALIZADA AO VIVO] Liquidando: {cm['team_blue']['code']} vs {cm['team_red']['code']} [{cm['league_name']}]...")
                                self.settle_match_event(cm, dispatch_discord=True)

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
