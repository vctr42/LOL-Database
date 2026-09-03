import requests
import json

game_ids = [
    '105590002183914470', '105590002183914468', '105590002183914466',
    '105590002183914467', '105590002183914472', '105590002183914471',
    '105590002183914465', '105590002181424095', '105590002183914469', '105590002183914464'
]

print("--- Testando IDs na CDN da Riot Games ---")
for gid in game_ids:
    url = f"https://feed.lolesports.com/livestats/v1/window/{gid}"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        print(f"GameID: {gid} | Status: {r.status_code} | Len: {len(r.text)}")
        if r.status_code == 200:
            data = r.json()
            frames = data.get("frames", [])
            print(f" -> SUCESSO! Frames: {len(frames)} | GameState: {data.get('gameState')}")
            if frames:
                last_f = frames[-1]
                print(f"    Blue: {last_f.get('blueTeam', {}).get('code')} ({last_f.get('blueTeam', {}).get('totalKills')} kills) vs Red: {last_f.get('redTeam', {}).get('code')} ({last_f.get('redTeam', {}).get('totalKills')} kills)")
    except Exception as e:
        print(f"Erro em {gid}: {e}")
