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

# Liquidar GAM vs MVK da LCP
lcp_matches = [m for m in completed if m.get("league_slug") == "lcp"]
for m in lcp_matches:
    print(f"\n⚡ Liquidando confronto LCP: {m['team_blue']['code']} vs {m['team_red']['code']}...")
    monitor.settle_match_event(m)

print("\n✔ Teste de inserção LCP concluído!")
