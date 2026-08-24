#!/usr/bin/env python3
"""
LoL Settlement Hub - Executável CLI Principal
Permite disparar varredura, auditar partidas e gerar dossiês de liquidação sob demanda.
"""

import sys
import os
import json
import argparse

# Configurar stdout para UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core.riot_feed import RiotFeedClient
from core.audit_gate import AuditGate
from core.settlement import SettlementCompiler
from core.database import DatabaseManager
from discord.embeds import DiscordFormatter
from discord.router import DiscordRouter
from tests.mock_data import get_valid_cblol_window_payload

def run_demo():
    print("=" * 65)
    print("🎮 LoL Settlement Hub • Auditoria & Liquidação Oficial")
    print("=" * 65)
    
    print("\n[1/4] Carregando telemetria bruta da Riot CDN...")
    payload = get_valid_cblol_window_payload()
    league_meta = {
        "league_slug": "cblol",
        "league_name": "CBLOL",
        "game_number": 1,
        "match_id": "match_demo_1001"
    }

    print("\n[2/4] Executando Zero-Doubt Verification Gate...")
    audit = AuditGate.audit_game_window(payload)
    if not audit.passed:
        print(f"❌ ZERO-DOUBT REPROVADO! Motivos: {audit.reasons}")
        sys.exit(1)
    print("✅ ZERO-DOUBT GATE: APROVADO COM 100% DE CONFIANÇA")

    print("\n[3/4] Compilando Dossiê Cirúrgico de Mercados...")
    dossier = SettlementCompiler.compile_from_window_and_details(payload, league_meta=league_meta)
    yaml_text = DiscordFormatter.build_yaml_dossier(dossier)
    print("\n--- DOSSIÊ YAML GERADO ---")
    print(yaml_text)
    print("--------------------------")

    print("\n[4/4] Persistindo no Data Lake...")
    db_mgr = DatabaseManager()
    db_mgr.save_dossier(dossier, yaml_text, raw_window=payload)
    print(f"✅ Partida {dossier.game_id} salva com sucesso no Data Lake!")

    print("\n[Discord] Despachando para canal correspondente...")
    dispatch_res = DiscordRouter.dispatch_settlement(dossier)
    print(f"📢 Status de Despacho: {dispatch_res.get('sent', False)} ({dispatch_res.get('reason') or 'Enviado'})")
    print("\n🎉 Processo concluído com sucesso!")

if __name__ == "__main__":
    run_demo()
