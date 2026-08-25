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

print(f"Total de confrontos oficiais finalizados identificados: {len(completed)}")

# Liquidar os confrontos reais finalizados
for cm in completed[:3]:
    t_blue = cm["team_blue"]["code"]
    t_red = cm["team_red"]["code"]
    l_name = cm["league_name"]
    print(f"\n⚡ Liquidando confronto real: {t_blue} vs {t_red} [{l_name}]...")
    monitor.settle_match_event(cm)

print("\n✔ Ciclo de liquidação e despacho finalizado com sucesso!")
