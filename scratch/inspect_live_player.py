import requests
import re
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

print("--- Inspecionando páginas ao vivo da Riot ---")
urls = [
    "https://lolesports.com/pt-BR/live",
    "https://lolesports.com/en-US/live",
    "https://lolesports.com/pt-BR/schedule"
]

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"URL: {url} | Status: {r.status_code} | Len: {len(r.text)}")
        # Buscar qualquer padrão de live, match, gameId
        streams = re.findall(r'https?://[^\s"\'`)]+feed\.lolesports\.com[^\s"\'`)]*', r.text)
        game_matches = re.findall(r'["\']?(?:gameId|matchId|id)["\']?\s*:\s*["\']?([0-9]{10,20})["\']?', r.text)
        print(f" -> Streams feed encontradas: {streams}")
        print(f" -> IDs numéricos encontrados: {set(game_matches[:10])}")
        
        # Buscar nomes de equipes ou campeonatos
        if "circuito" in r.text.lower() or "cblol" in r.text.lower() or "lck" in r.text.lower() or "lec" in r.text.lower():
            print(" -> Encontradas referências a ligas no HTML!")
    except Exception as e:
        print(f"Erro em {url}: {e}")
