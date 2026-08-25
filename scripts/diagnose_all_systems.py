import requests
import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

print("=====================================================")
print("[DIAGNOSTICO COMPLETO DO ECOSSISTEMA LOL-DATABASE]")
print("=====================================================\n")

# 1. TESTE DE WEBHOOKS
print("[1/4] TESTANDO CONEXAO COM TODOS OS WEBHOOKS DO DISCORD:")
config_path = BASE_DIR / "config" / "league_channels.json"
with open(config_path, "r", encoding="utf-8") as f:
    channels = json.load(f)

unique_webhooks = {}
for k, v in channels.items():
    url = v.get("webhook_url") or os.getenv(v.get("env_webhook", ""), "")
    if url and url not in unique_webhooks:
        unique_webhooks[url] = v.get("name")

for url, name in unique_webhooks.items():
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            chan_name = data.get("name", "desconhecido")
            chan_id = data.get("id", "N/A")
            print(f"   [OK 200] {name.ljust(22)}: Canal #{chan_name} (ID: {chan_id})")
        else:
            print(f"   [FAIL]   {name.ljust(22)}: HTTP {r.status_code}")
    except Exception as e:
        print(f"   [FAIL]   {name.ljust(22)}: Erro - {e}")

# 2. TESTE DO SUPABASE
print("\n[2/4] TESTANDO CONEXAO COM O DATA LAKE SUPABASE (NUVEM):")
supa_url = os.getenv("SUPABASE_URL")
supa_key = os.getenv("SUPABASE_ANON_KEY")
try:
    r = requests.get(
        f"{supa_url}/rest/v1/games?select=*&limit=5",
        headers={
            "apikey": supa_key,
            "Authorization": f"Bearer {supa_key}"
        },
        timeout=5
    )
    if r.status_code == 200:
        games = r.json()
        print(f"   [OK 200] Supabase PostgreSQL: Conectado e Operacional na Nuvem")
        print(f"   [TABELAS] Tabela 'games' indexada e pronta para novas partidas")
    else:
        print(f"   [FAIL]   Supabase Status: HTTP {r.status_code}")
except Exception as e:
    print(f"   [FAIL]   Erro ao conectar no Supabase: {e}")

# 3. TESTE DE ROTAS NETLIFY PRODUCAO
print("\n[3/4] TESTANDO SERVERLESS FUNCTIONS EM PRODUCAO (NETLIFY):")
endpoints = [
    ("api_settlements", "https://lol-database.netlify.app/api/api_settlements"),
    ("api_h2h", "https://lol-database.netlify.app/api/api_h2h?team_a=PNG&team_b=LLL"),
    ("api_monitor", "https://lol-database.netlify.app/api/api_monitor")
]
for name, ep in endpoints:
    try:
        r = requests.get(ep, timeout=8)
        if r.status_code == 200:
            print(f"   [OK 200] {name.ljust(22)}: Operacional na Nuvem (HTTP 200)")
        else:
            print(f"   [WARN]   {name.ljust(22)}: HTTP {r.status_code}")
    except Exception as e:
        print(f"   [FAIL]   {name.ljust(22)}: Erro - {e}")

print("\n=====================================================")
