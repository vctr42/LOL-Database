import os
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx

from config.settings import settings, BASE_DIR
from core.models import SettlementDossier, SeriesSummary

logger = logging.getLogger("LiveBetCore.Database")

class DatabaseRepository:
    """
    Repositório Unificado de Persistência Dual (Supabase Cloud + SQLite Local).
    Oferece resiliência total: opera na nuvem com fallback e buffer local automático.
    """

    def __init__(self):
        self.sqlite_path = BASE_DIR / settings.sqlite_db_path
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self.mode = settings.db_mode.lower()
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_anon_key
        self._init_sqlite()

    def _get_sqlite_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.sqlite_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite(self):
        """Inicializa o banco de dados local SQLite com o schema padrão."""
        schema_path = BASE_DIR / "database" / "schema.sql"
        if not schema_path.exists():
            return
        
        with open(schema_path, "r", encoding="utf-8") as f:
            sql = f.read()

        # SQLite não suporta TIMESTAMP WITH TIME ZONE ou JSON nativo da mesma forma; normalizar:
        sqlite_sql = sql.replace("TIMESTAMP WITH TIME ZONE", "TIMESTAMP").replace("NUMERIC", "REAL")

        conn = self._get_sqlite_conn()
        cursor = conn.cursor()
        cursor.executescript(sqlite_sql)
        conn.commit()
        conn.close()
        logger.debug(f"SQLite local inicializado em {self.sqlite_path}")

    def _get_supabase_headers(self) -> Dict[str, str]:
        return {
            "apikey": self.supabase_key or "",
            "Authorization": f"Bearer {self.supabase_key or ''}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }

    async def save_dossier(self, dossier: SettlementDossier, yaml_text: str) -> bool:
        """Persiste o dossiê de liquidação de mapa no SQLite local e no Supabase Cloud."""
        # 1. Salvar no SQLite Local (Transação Imediata)
        try:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT OR REPLACE INTO lol_games (
                id, match_id, game_number, league_slug, patch_version,
                winner_code, winner_side, duration_seconds, duration_formatted,
                blue_kills, red_kills, blue_towers, red_towers,
                blue_dragons, red_dragons, blue_barons, red_barons,
                blue_heralds, red_heralds, blue_inhibitors, red_inhibitors,
                first_blood_team, first_blood_time, first_tower_team, first_tower_time,
                first_dragon_team, first_dragon_time, first_herald_team, first_herald_time,
                first_baron_team, first_baron_time, race_to_5_kills, race_to_10_kills,
                race_to_15_kills, kill_spread_margin, handicap_green_line, audit_passed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dossier.game_id, dossier.match_id, dossier.game_number, dossier.league_slug, dossier.patch_version,
                dossier.winner_code, dossier.winner_side, dossier.duration_seconds, dossier.duration_formatted,
                dossier.blue_kills, dossier.red_kills, dossier.blue_towers, dossier.red_towers,
                dossier.blue_dragons, dossier.red_dragons, dossier.blue_barons, dossier.red_barons,
                dossier.blue_heralds, dossier.red_heralds, dossier.blue_inhibitors, dossier.red_inhibitors,
                dossier.first_blood_team, dossier.first_blood_time, dossier.first_tower_team, dossier.first_tower_time,
                dossier.first_dragon_team, dossier.first_dragon_time, dossier.first_herald_team, dossier.first_herald_time,
                dossier.first_baron_team, dossier.first_baron_time, dossier.race_to_5, dossier.race_to_10,
                dossier.race_to_15, float(dossier.kill_spread), dossier.handicap_green_line, dossier.audit_passed
            ))

            cursor.execute("""
            INSERT OR REPLACE INTO settlement_dossiers (
                id, game_id, league_slug, match_title, yaml_dossier, json_summary
            ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"dossier_{dossier.game_id}",
                dossier.game_id,
                dossier.league_slug,
                dossier.match_title,
                yaml_text,
                json.dumps(dossier.model_dump())
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Erro ao persistir no SQLite: {e}")

        # 2. Sincronizar com Supabase Cloud
        if self.mode == "supabase" and self.supabase_url and self.supabase_key:
            try:
                headers = self._get_supabase_headers()
                async with httpx.AsyncClient(timeout=8.0) as client:
                    game_payload = {
                        "id": dossier.game_id,
                        "match_id": dossier.match_id,
                        "game_number": dossier.game_number,
                        "league_slug": dossier.league_slug,
                        "patch_version": dossier.patch_version,
                        "winner_code": dossier.winner_code,
                        "winner_side": dossier.winner_side,
                        "duration_seconds": dossier.duration_seconds,
                        "duration_formatted": dossier.duration_formatted,
                        "blue_kills": dossier.blue_kills,
                        "red_kills": dossier.red_kills,
                        "blue_towers": dossier.blue_towers,
                        "red_towers": dossier.red_towers,
                        "blue_dragons": dossier.blue_dragons,
                        "red_dragons": dossier.red_dragons,
                        "blue_barons": dossier.blue_barons,
                        "red_barons": dossier.red_barons,
                        "blue_heralds": dossier.blue_heralds,
                        "red_heralds": dossier.red_heralds,
                        "blue_inhibitors": dossier.blue_inhibitors,
                        "red_inhibitors": dossier.red_inhibitors,
                        "first_blood_team": dossier.first_blood_team,
                        "first_blood_time": dossier.first_blood_time,
                        "first_tower_team": dossier.first_tower_team,
                        "first_tower_time": dossier.first_tower_time,
                        "first_dragon_team": dossier.first_dragon_team,
                        "first_dragon_time": dossier.first_dragon_time,
                        "first_herald_team": dossier.first_herald_team,
                        "first_herald_time": dossier.first_herald_time,
                        "first_baron_team": dossier.first_baron_team,
                        "first_baron_time": dossier.first_baron_time,
                        "race_to_5_kills": dossier.race_to_5,
                        "race_to_10_kills": dossier.race_to_10,
                        "race_to_15_kills": dossier.race_to_15,
                        "kill_spread_margin": float(dossier.kill_spread),
                        "handicap_green_line": dossier.handicap_green_line,
                        "audit_passed": dossier.audit_passed
                    }
                    await client.post(f"{self.supabase_url}/rest/v1/lol_games", headers=headers, json=game_payload)

                    dossier_payload = {
                        "id": f"dossier_{dossier.game_id}",
                        "game_id": dossier.game_id,
                        "league_slug": dossier.league_slug,
                        "match_title": dossier.match_title,
                        "yaml_dossier": yaml_text,
                        "json_summary": dossier.model_dump()
                    }
                    await client.post(f"{self.supabase_url}/rest/v1/settlement_dossiers", headers=headers, json=dossier_payload)
            except Exception as e:
                logger.warning(f"Aviso de sincronização Supabase (buffer local preservado): {e}")

        return True

    async def save_series_summary(self, series: SeriesSummary) -> bool:
        """Persiste sumário oficial de série (sem telemetria fictícia)."""
        match_id = f"match_{series.league_slug}_{series.event_id}"
        
        try:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO lol_matches (
                id, league_slug, league_name, tournament_name,
                team_blue_code, team_blue_name, team_blue_wins,
                team_red_code, team_red_name, team_red_wins,
                winner_code, winner_name, best_of, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id, series.league_slug, series.league_name, series.tournament_name,
                series.team_blue_code, series.team_blue_name, series.team_blue_wins,
                series.team_red_code, series.team_red_name, series.team_red_wins,
                series.winner_code, series.winner_name, series.total_games,
                "completed" if series.is_completed else "in_progress"
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Erro ao persistir série no SQLite: {e}")

        if self.mode == "supabase" and self.supabase_url and self.supabase_key:
            try:
                headers = self._get_supabase_headers()
                async with httpx.AsyncClient(timeout=8.0) as client:
                    payload = {
                        "id": match_id,
                        "league_slug": series.league_slug,
                        "league_name": series.league_name,
                        "tournament_name": series.tournament_name,
                        "team_blue_code": series.team_blue_code,
                        "team_blue_name": series.team_blue_name,
                        "team_blue_wins": series.team_blue_wins,
                        "team_red_code": series.team_red_code,
                        "team_red_name": series.team_red_name,
                        "team_red_wins": series.team_red_wins,
                        "winner_code": series.winner_code,
                        "winner_name": series.winner_name,
                        "best_of": series.total_games,
                        "status": "completed" if series.is_completed else "in_progress"
                    }
                    await client.post(f"{self.supabase_url}/rest/v1/lol_matches", headers=headers, json=payload)
            except Exception as e:
                logger.warning(f"Aviso de sincronização série Supabase: {e}")

        return True

    def get_all_settled_ids(self) -> List[str]:
        """Obtém todos os IDs de mapas liquidados no SQLite local para inicializar o ledger."""
        try:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM lol_games")
            rows = cursor.fetchall()
            conn.close()
            return [str(r["id"]) for r in rows]
        except Exception as e:
            logger.error(f"Erro ao ler IDs do SQLite: {e}")
            return []

    async def fetch_cloud_settled_ids(self) -> List[str]:
        """Obtém todos os IDs de mapas liquidados diretamente do Supabase Cloud."""
        if not (self.supabase_url and self.supabase_key):
            return self.get_all_settled_ids()

        try:
            headers = {"apikey": self.supabase_key, "Authorization": f"Bearer {self.supabase_key}"}
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(f"{self.supabase_url}/rest/v1/lol_games?select=id", headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return [str(item["id"]) for item in data if "id" in item]
        except Exception as e:
            logger.warning(f"Falha ao consultar Supabase para IDs: {e}")
            
        return self.get_all_settled_ids()
