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

prime_matches = [m for m in matches if m.get("league_slug") == "prime-league" or "prime" in m.get("tournament", "").lower()]
print(f"Partidas da Prime League encontradas: {len(prime_matches)}")

for pm in prime_matches:
    # Se ainda não estiver marcada como completed, definimos com os dados para envio de demonstração oficial de canal
    t_blue = pm["team_blue"]["code"]
    t_red = pm["team_red"]["code"]
    print(f"\n⚡ Liquidando confronto Prime League: {t_blue} vs {t_red}...")
    monitor.settle_match_event(pm)

print("\n✔ Prime League finalizada!")
