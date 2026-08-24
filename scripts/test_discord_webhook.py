#!/usr/bin/env python3
"""
Script utilitário para testar o envio de Webhook no Discord.
Uso: python scripts/test_discord_webhook.py [URL_DO_WEBHOOK] [LIGA]
"""

import sys
import os
import requests

# Ajustar path raiz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configurar encoding UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config.settings import DISCORD_WEBHOOK_DEFAULT, get_league_webhook, LEAGUE_CONFIG
from core.settlement import SettlementDossier
from discord.embeds import DiscordFormatter

def send_test_notification(webhook_url: str, league_slug: str = "cblol"):
    print("=" * 60)
    print("📢 Testando Disparo de Webhook no Discord")
    print("=" * 60)
    print(f"🔗 URL: {webhook_url[:35]}...{webhook_url[-10:] if len(webhook_url) > 45 else ''}")
    print(f"🏆 Liga: {league_slug.upper()}")

    # Criar Dossiê de Teste Estruturado
    dossier = SettlementDossier(
        game_id="test_live_01",
        match_id="match_test_01",
        league_slug=league_slug.lower(),
        league_name=league_slug.upper(),
        match_title=f"[{league_slug.upper()}] TESTE DE CONECTIVIDADE — MAPA 1",
        game_number=1,
        winner_code="TIME AZUL",
        winner_side="BLUE",
        loser_code="TIME VERMELHO",
        loser_side="RED",
        duration_seconds=1845,
        duration_formatted="30:45",
        blue_kills=18,
        red_kills=9,
        kill_leader_code="TIME AZUL",
        kill_spread=9,
        handicap_green_line="TIME AZUL até -8.5 | TIME VERMELHO a partir de +9.5",
        blue_towers=8,
        red_towers=2,
        blue_dragons=3,
        red_dragons=1,
        blue_barons=1,
        red_barons=0,
        blue_heralds=1,
        red_heralds=0,
        blue_inhibitors=1,
        red_inhibitors=0,
        first_blood_team="TIME AZUL",
        first_blood_time="02:50",
        first_tower_team="TIME AZUL",
        first_tower_time="13:10",
        first_dragon_team="TIME AZUL",
        first_dragon_time="06:40",
        first_herald_team="TIME AZUL",
        first_herald_time="08:20",
        first_baron_team="TIME AZUL",
        first_baron_time="21:15",
        race_to_5="TIME AZUL (07:30)",
        race_to_10="TIME AZUL (16:40)",
        race_to_15="TIME AZUL (24:10)",
        audit_passed=True,
        participants=[]
    )

    league_info = LEAGUE_CONFIG.get(league_slug.lower(), LEAGUE_CONFIG.get("default", {}))
    payload = DiscordFormatter.build_discord_payload(dossier, league_info)

    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        if resp.status_code in (200, 204):
            print("\n✅ SUCESSO! A mensagem foi enviada com sucesso ao seu canal do Discord!")
            print(f"Status HTTP: {resp.status_code}")
        else:
            print(f"\n❌ Erro ao enviar: Status HTTP {resp.status_code}")
            print(f"Resposta Discord: {resp.text}")
    except Exception as e:
        print(f"\n❌ Falha na conexão com o Discord: {e}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else None
    league = sys.argv[2] if len(sys.argv) > 2 else "cblol"

    if not url:
        url = DISCORD_WEBHOOK_DEFAULT or get_league_webhook(league)

    if not url:
        print("❌ Nenhuma URL de Webhook fornecida ou encontrada no .env!")
        print("Uso: python scripts/test_discord_webhook.py <URL_DO_WEBHOOK> [cblol|lck|lpl|lec|lcs]")
        sys.exit(1)

    send_test_notification(url, league)
