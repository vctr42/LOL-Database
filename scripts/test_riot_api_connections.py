#!/usr/bin/env python3
"""
Script de diagnóstico e teste de conectividade das APIs da Riot Games Esports.
Testa todos os caminhos, endpoints, latência e integridade dos payloads.
"""

import sys
import os
import time
import requests
import json

# Configurar stdout para UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

class RiotAPIDiagnostic:
    HEADERS = {
        "User-Agent": "LOL-Database/1.0 (Audit & Settlement Engine; contact@lol-database.app)",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate"
    }

    ENDPOINTS = {
        "1. getLeagues (Ligas Oficiais)": {
            "url": "https://esports-api.lolesports.com/persisted/val/getLeagues",
            "params": {"hl": "pt-BR"},
            "desc": "Lista de todas as ligas mundiais (CBLOL, LCK, LPL, LEC, LCS, etc.)"
        },
        "2. getSchedule (Agenda Oficial)": {
            "url": "https://esports-api.lolesports.com/persisted/val/getSchedule",
            "params": {"hl": "pt-BR"},
            "desc": "Calendário de partidas, séries e status de transmissão"
        },
        "3. getLiveDetails (Eventos ao Vivo)": {
            "url": "https://esports-api.lolesports.com/persisted/val/getLiveDetails",
            "params": {"hl": "pt-BR"},
            "desc": "Detecção de partidas em andamento e recém-finalizadas"
        },
        "4. getTournamentsForLeague (Torneios CBLOL)": {
            "url": "https://esports-api.lolesports.com/persisted/val/getTournamentsForLeague",
            "params": {"hl": "pt-BR", "leagueId": "98767991310879774"},
            "desc": "Etapas e splits oficiais do CBLOL"
        },
        "5. LiveStats Window CDN (Telemetria Frames)": {
            "url": "https://feed.lolesports.com/livestats/v1/window/109545434567890",
            "params": {},
            "desc": "CDN de stream de frames, in-game clock e placares em tempo real"
        },
        "6. LiveStats Details CDN (Eventos Detalhados)": {
            "url": "https://feed.lolesports.com/livestats/v1/details/109545434567890",
            "params": {},
            "desc": "CDN de eventos atômicos (kills, torres, dragões e itens)"
        }
    }

    @classmethod
    def run_full_diagnostic(cls):
        print("=" * 70)
        print("🔍 DIAGNÓSTICO DE CONECTIVIDADE COM A API DA RIOT GAMES ESPORTS")
        print("=" * 70)
        
        results = []
        found_recent_games = []

        for name, cfg in cls.ENDPOINTS.items():
            url = cfg["url"]
            params = cfg["params"]
            desc = cfg["desc"]
            
            print(f"\n📡 Testando: {name}")
            print(f"   ℹ️  Descrição: {desc}")
            print(f"   🔗 URL: {url}")

            start_t = time.time()
            try:
                resp = requests.get(url, params=params, headers=cls.HEADERS, timeout=8)
                latency_ms = int((time.time() - start_t) * 1000)
                status_code = resp.status_code

                if status_code in (200, 204):
                    data = resp.json() if resp.text else {}
                    data_keys = list(data.get("data", {}).keys()) if isinstance(data, dict) and "data" in data else list(data.keys())[:5]
                    print(f"   ✅ Status: {status_code} OK (Latência: {latency_ms}ms)")
                    print(f"   📦 Estrutura Retornada: {data_keys}")
                    
                    # Se for getLeagues, contar ligas
                    if "getLeagues" in name:
                        leagues = data.get("data", {}).get("leagues", [])
                        print(f"   🏆 Total de Ligas Ativas Encontradas: {len(leagues)}")
                        cblol_found = any(l.get("slug") == "cblol-brazil" or "cblol" in l.get("slug", "") for l in leagues)
                        lck_found = any(l.get("slug") == "lck" for l in leagues)
                        print(f"      • CBLOL Presente: {'SIM ✅' if cblol_found else 'NÃO'}")
                        print(f"      • LCK Presente: {'SIM ✅' if lck_found else 'NÃO'}")

                    # Se for getSchedule, inspecionar eventos
                    if "getSchedule" in name:
                        events = data.get("data", {}).get("schedule", {}).get("events", [])
                        print(f"   📅 Eventos na Agenda: {len(events)}")
                        for evt in events[:5]:
                            match = evt.get("match", {})
                            league = evt.get("league", {})
                            if match.get("games"):
                                for g in match.get("games", []):
                                    if g.get("id"):
                                        found_recent_games.append({
                                            "league": league.get("name", "LOL"),
                                            "game_id": g.get("id"),
                                            "state": g.get("state")
                                        })

                    results.append({"name": name, "status": status_code, "latency": latency_ms, "ok": True})
                elif status_code == 404 and "LiveStats" in name:
                    # 404 em LiveStats para ID dummy significa que o servidor CDN está vivo e respondeu (rejeitando apenas o ID inexistente)
                    print(f"   ✅ CDN Ativa: Status {status_code} (Servidor da CDN online e respondendo em {latency_ms}ms)")
                    results.append({"name": name, "status": status_code, "latency": latency_ms, "ok": True, "note": "CDN Online (Rejeitou ID dummy)"})
                else:
                    print(f"   ⚠️ Status: {status_code} (Latência: {latency_ms}ms)")
                    results.append({"name": name, "status": status_code, "latency": latency_ms, "ok": False})

            except Exception as e:
                latency_ms = int((time.time() - start_t) * 1000)
                print(f"   ❌ Erro de Conexão: {e}")
                results.append({"name": name, "status": "ERROR", "latency": latency_ms, "ok": False, "error": str(e)})

        # Resumo
        print("\n" + "=" * 70)
        print("📊 RESUMO GERAL DE CONECTIVIDADE RIOT GAMES")
        print("=" * 70)
        for r in results:
            status_symbol = "✅ ONLINE" if r["ok"] else "❌ FALHA"
            print(f"{status_symbol.ljust(12)} │ {r['name'].ljust(45)} │ {str(r['status']).ljust(6)} │ {r['latency']}ms")

        print("=" * 70)
        all_ok = all(r["ok"] for r in results)
        if all_ok:
            print("🚀 TODOS OS CAMINHOS E ENDPOINTS DA RIOT GAMES ESTÃO 100% OPERACIONAIS!")
        else:
            print("⚠️ Alguns caminhos apresentaram instabilidade.")
        print("=" * 70)

if __name__ == "__main__":
    RiotAPIDiagnostic.run_full_diagnostic()
