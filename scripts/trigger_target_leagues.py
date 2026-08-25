import sys
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / ".env")

from live_monitor import LiveGameMonitor
from core.riot_schedule_parser import RiotScheduleParser

monitor = LiveGameMonitor()
matches = RiotScheduleParser.fetch_official_matches()

# Filtrar confrontos de Circuito Desafiante, Prime League e LRN
target_slugs = ["circuito-desafiante", "prime-league", "lrn", "lck-challengers", "cblol", "rift-legends"]
target_matches = [m for m in matches if m.get("league_slug") in target_slugs and m.get("is_completed")]

print(f"Total de confrontos finalizados encontrados para as ligas alvo: {len(target_matches)}")

for m in target_matches:
    t_blue = m["team_blue"]["code"]
    t_red = m["team_red"]["code"]
    l_name = m["league_name"]
    l_slug = m["league_slug"]
    print(f"\n⚡ Liquidando confronto: {t_blue} vs {t_red} [{l_name} ({l_slug})]...")
    monitor.settle_match_event(m)

print("\n✔ Todas as ligas foram processadas com sucesso!")
