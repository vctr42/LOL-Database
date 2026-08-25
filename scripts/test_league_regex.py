import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8'
}
r = requests.get('https://lolesports.com/pt-BR/schedule', headers=headers)
html = r.text

chunks = re.findall(r'(\{"__typename":"EventMatch".*?"matchTeams":\[.*?\]\})', html)
print(f"Blocos EventMatch extraídos: {len(chunks)}")
if chunks:
    print("Primeiro bloco completo:")
    print(chunks[0][:500])
