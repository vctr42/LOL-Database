import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Carregar arquivo .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Base de Dados
DB_MODE = os.getenv("DB_MODE", "sqlite").lower() # "sqlite" ou "supabase"
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "data" / "settlement_data.db"))
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Riot Esports API
RIOT_API_KEY = os.getenv("RIOT_API_KEY", "")
RIOT_LOCALE = os.getenv("RIOT_LOCALE", "pt-BR")

# Discord Webhooks
DISCORD_WEBHOOK_DEFAULT = os.getenv("DISCORD_WEBHOOK_DEFAULT", "")
ENABLE_DISCORD_NOTIFICATIONS = os.getenv("ENABLE_DISCORD_NOTIFICATIONS", "false").lower() in ("true", "1", "yes")

# Carregar mapeamento de canais por liga
LEAGUE_CONFIG_PATH = BASE_DIR / "config" / "league_channels.json"
LEAGUE_CONFIG = {}
if LEAGUE_CONFIG_PATH.exists():
    try:
        with open(LEAGUE_CONFIG_PATH, "r", encoding="utf-8") as f:
            LEAGUE_CONFIG = json.load(f)
    except Exception:
        LEAGUE_CONFIG = {}

def get_league_webhook(league_slug: str) -> str:
    """Retorna o webhook configurado para a liga ou o webhook default."""
    slug = (league_slug or "").lower().strip()
    league_info = LEAGUE_CONFIG.get(slug, LEAGUE_CONFIG.get("default", {}))
    env_var = league_info.get("env_webhook", "DISCORD_WEBHOOK_DEFAULT")
    webhook = os.getenv(env_var, "")
    if not webhook:
        webhook = DISCORD_WEBHOOK_DEFAULT
    return webhook
