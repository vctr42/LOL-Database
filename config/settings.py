import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent

class AppSettings(BaseSettings):
    # Banco de Dados
    db_mode: str = Field(default="supabase", alias="DB_MODE")
    sqlite_db_path: str = Field(default="data/live_bet_core.db", alias="SQLITE_DB_PATH")
    supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
    supabase_anon_key: Optional[str] = Field(default=None, alias="SUPABASE_ANON_KEY")

    # Discord Notificações
    enable_discord_notifications: bool = Field(default=True, alias="ENABLE_DISCORD_NOTIFICATIONS")
    discord_webhook_default: Optional[str] = Field(default=None, alias="DISCORD_WEBHOOK_DEFAULT")
    discord_webhook_cblol: Optional[str] = Field(default=None, alias="DISCORD_WEBHOOK_CBLOL")
    discord_webhook_circuito_desafiante: Optional[str] = Field(default=None, alias="DISCORD_WEBHOOK_CIRCUITO_DESAFIANTE")
    discord_webhook_lck: Optional[str] = Field(default=None, alias="DISCORD_WEBHOOK_LCK")
    discord_webhook_lck_cl: Optional[str] = Field(default=None, alias="DISCORD_WEBHOOK_LCK_CL")
    discord_webhook_lpl: Optional[str] = Field(default=None, alias="DISCORD_WEBHOOK_LPL")
    discord_webhook_lcp: Optional[str] = Field(default=None, alias="DISCORD_WEBHOOK_LCP")
    discord_webhook_lrn: Optional[str] = Field(default=None, alias="DISCORD_WEBHOOK_LRN")
    discord_webhook_prime_league: Optional[str] = Field(default=None, alias="DISCORD_WEBHOOK_PRIME_LEAGUE")
    discord_webhook_rift_legends: Optional[str] = Field(default=None, alias="DISCORD_WEBHOOK_RIFT_LEGENDS")
    discord_webhook_nacl: Optional[str] = Field(default=None, alias="DISCORD_WEBHOOK_NACL")

    # Monitoramento
    riot_locale: str = Field(default="pt-BR", alias="RIOT_LOCALE")
    monitor_interval_seconds: int = Field(default=10, alias="MONITOR_INTERVAL_SECONDS")
    auto_settle_live: bool = Field(default=True, alias="AUTO_SETTLE_LIVE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = AppSettings()

def load_league_metadata() -> Dict[str, Any]:
    """Carrega o arquivo leagues.json e constrói índice invertido por slug e alias."""
    leagues_file = BASE_DIR / "config" / "leagues.json"
    if not leagues_file.exists():
        return {}
    with open(leagues_file, "r", encoding="utf-8") as f:
        return json.load(f)

LEAGUES_DATA = load_league_metadata()

# Dicionário de normalização de slugs por alias
SLUG_ALIASES: Dict[str, str] = {}
for canonical_slug, data in LEAGUES_DATA.items():
    SLUG_ALIASES[canonical_slug.lower()] = canonical_slug
    for alias in data.get("aliases", []):
        SLUG_ALIASES[alias.lower()] = canonical_slug

def normalize_league_slug(raw_slug: Optional[str]) -> str:
    """Mapeia qualquer variação oficial de slug da Riot para o slug canônico."""
    if not raw_slug:
        return "default"
    clean = raw_slug.strip().lower().replace("_", "-")
    
    if clean in SLUG_ALIASES:
        return SLUG_ALIASES[clean]
        
    for alias, canonical in SLUG_ALIASES.items():
        if alias in clean:
            return canonical
            
    return "default"

def get_league_config(raw_slug: Optional[str]) -> Dict[str, Any]:
    """Retorna metadados completos da liga a partir de qualquer slug ou alias."""
    canonical = normalize_league_slug(raw_slug)
    config = LEAGUES_DATA.get(canonical, LEAGUES_DATA.get("default", {}))
    return config

def get_league_webhook(raw_slug: Optional[str]) -> Optional[str]:
    """Retorna o webhook URL correspondente configurado no .env."""
    config = get_league_config(raw_slug)
    env_var_name = config.get("env_webhook")
    if not env_var_name:
        return settings.discord_webhook_default
        
    val = getattr(settings, env_var_name.lower(), None)
    return val or settings.discord_webhook_default
