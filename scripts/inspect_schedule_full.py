import requests
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8'
}
r = requests.get('https://lolesports.com/pt-BR/schedule', headers=headers)
html = r.text

print(f"HTML Baixado: {len(html)} bytes")

# Extrair todos os blocos de eventos
# Padrão de bloco de evento com liga, torneio, times e jogos
pattern = r'\{"__typename":"EventMatch","id":"(\d+)",.*?"startTime":"([^"]+)",.*?"state":"([^"]+)",.*?"league":\{"__typename":"League",.*?"name":"([^"]+)",.*?"slug":"([^"]+)"\}.*?"match":\{"__typename":"Match","id":"(\d+)",.*?"state":"([^"]+)",.*?"teams":\[\{"__typename":"MatchTeam","name":"([^"]+)","code":"([^"]+)".*?"result":\{"__typename":"TeamResult","gameWins":(\d+).*?\},\{"__typename":"MatchTeam","name":"([^"]+)","code":"([^"]+)".*?"result":\{"__typename":"TeamResult","gameWins":(\d+)'

matches = re.findall(pattern, html)
print(f"Total de Partidas Completas Extraídas: {len(matches)}")

for m in matches[:15]:
    event_id, start_time, ev_state, league_name, league_slug, match_id, match_state, t1_name, t1_code, t1_wins, t2_name, t2_code, t2_wins = m
    print(f"[{league_name} - {league_slug}] {t1_name} ({t1_code}) [{t1_wins}] vs [{t2_wins}] {t2_name} ({t2_code}) | Estado: {match_state} | MatchID: {match_id}")
