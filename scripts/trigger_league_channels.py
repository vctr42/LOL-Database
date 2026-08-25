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
completed = [m for m in matches if m.get('is_completed')]

# Filtrar partidas de LPL, LCK e LCP
selected = [m for m in completed if m.get("league_slug") in ["lpl", "lck", "lcp", "prime-league", "rift-legends", "cblol", "lrn"]]
print(f"Confrontos encontrados nas ligas principais: {len(selected)}")

for m in selected[:3]:
    t_blue = m["team_blue"]["code"]
    t_red = m["team_red"]["code"]
    l_name = m["league_name"]
    print(f"\n⚡ Liquidando confronto oficial de {l_name}: {t_blue} vs {t_red}...")
    monitor.settle_match_event(m)

print("\n✔ Teste de canais concluído com sucesso!")
