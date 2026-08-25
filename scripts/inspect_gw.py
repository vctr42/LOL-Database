import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Testar endpoint GraphQL do lolesports
url = "https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=pt-BR"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "x-api-key": "0TvQnueqKa5mxJgahAFFu"
}

r = requests.get(url, headers=headers)
print("Persisted GW Status:", r.status_code)
if r.status_code == 200:
    data = r.json()
    events = data.get("data", {}).get("schedule", {}).get("events", [])
    print(f"Total de Eventos no Gateway: {len(events)}")
    for ev in events[:10]:
        state = ev.get("state")
        league = ev.get("league", {}).get("name")
        match = ev.get("match", {})
        teams = match.get("teams", [])
        t_names = [t.get("code") for t in teams]
        print(f" -> [{league}] {' vs '.join(t_names)} | Estado: {state}")
