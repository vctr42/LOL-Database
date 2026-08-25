const SUPABASE_URL = "https://estkjalhpiwmjyagbjvl.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVzdGtqYWxocGl3bWp5YWdianZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAzNTA2MjQsImV4cCI6MjA1NTkyNjYyNH0.uBf9N6z_g1w6W2EeqeYjO4P2K_j5M_Q0Pz6gR1S2T3U";

document.addEventListener("DOMContentLoaded", () => {
  const gameSelect = document.getElementById("gameSelect");
  const blueTableBody = document.getElementById("blueTableBody");
  const redTableBody = document.getElementById("redTableBody");
  const blueTeamHeader = document.getElementById("blueTeamHeader");
  const redTeamHeader = document.getElementById("redTeamHeader");
  const telemetryMapTitle = document.getElementById("telemetryMapTitle");

  let gamesList = [];

  async function init() {
    try {
      const supaHeaders = { "apikey": SUPABASE_ANON_KEY, "Authorization": `Bearer ${SUPABASE_ANON_KEY}` };
      const [gamesRes, dossiersRes] = await Promise.allSettled([
        fetch(`${SUPABASE_URL}/rest/v1/lol_games?select=*&order=created_at.desc&limit=50`, { headers: supaHeaders }),
        fetch(`${SUPABASE_URL}/rest/v1/settlement_dossiers?select=*&order=created_at.desc&limit=50`, { headers: supaHeaders })
      ]);

      let games = [];
      let dossiers = [];
      if (gamesRes.status === "fulfilled" && gamesRes.value.ok) games = await gamesRes.value.json();
      if (dossiersRes.status === "fulfilled" && dossiersRes.value.ok) dossiers = await dossiersRes.value.json();

      if (games.length > 0) {
        const dossierMap = {};
        dossiers.forEach(d => { if (d.game_id) dossierMap[d.game_id] = d; });

        gamesList = games.map(g => {
          const d = dossierMap[g.id] || {};
          const summary = d.json_summary || {};
          return {
            game_id: g.id,
            match_title: d.match_title || summary.match_title || `[${(g.league_slug || 'LOL').toUpperCase()}] Confronto Oficial (${g.id})`,
            team_blue_code: summary.blue_team_code || (g.winner_side === 'BLUE' ? g.winner_code : '--'),
            team_red_code: summary.red_team_code || (g.winner_side === 'RED' ? g.winner_code : '--'),
            participants: summary.participants || []
          };
        });
      } else {
        const resp = await fetch("/api/api_settlements");
        if (resp.ok) {
          const data = await resp.json();
          gamesList = Array.isArray(data) ? data : [];
        }
      }
    } catch (e) {
      gamesList = [];
    }
    populateSelect();
  }

  function populateSelect() {
    if (gamesList.length === 0) {
      gameSelect.innerHTML = `<option value="">Nenhum mapa registrado no Data Lake</option>`;
      blueTableBody.innerHTML = `
        <tr>
          <td colspan="9" style="text-align: center; color: var(--text-muted); padding: 2rem;">
            Nenhum dado de telemetria disponível no momento. Aguardando finalização de partidas na Riot Games.
          </td>
        </tr>
      `;
      redTableBody.innerHTML = `
        <tr>
          <td colspan="9" style="text-align: center; color: var(--text-muted); padding: 2rem;">
            Nenhum dado de telemetria disponível no momento. Aguardando finalização de partidas na Riot Games.
          </td>
        </tr>
      `;
      return;
    }

    gameSelect.innerHTML = gamesList.map(g => `
      <option value="${g.game_id}">${g.match_title || g.game_id}</option>
    `).join("");

    loadGameTelemetry(gamesList[0].game_id);

    gameSelect.addEventListener("change", (e) => {
      loadGameTelemetry(e.target.value);
    });
  }

  async function loadGameTelemetry(gameId) {
    const selected = gamesList.find(g => g.game_id === gameId);
    if (!selected) return;

    telemetryMapTitle.textContent = selected.match_title || "Telemetria do Mapa";

    const blueCode = selected.team_blue_code || "LADO AZUL";
    const redCode = selected.team_red_code || "LADO VERMELHO";

    blueTeamHeader.textContent = `🔵 LADO AZUL (${blueCode})`;
    redTeamHeader.textContent = `🔴 LADO VERMELHO (${redCode})`;

    const participants = (selected.summary_obj && selected.summary_obj.participants) || selected.participants || [];
    renderTables(participants);
  }

  function renderTables(participants) {
    if (!participants || participants.length === 0) {
      const emptyRow = `
        <tr>
          <td colspan="9" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">
            Telemetria detalhada dos participantes não registrada para este mapa.
          </td>
        </tr>
      `;
      blueTableBody.innerHTML = emptyRow;
      redTableBody.innerHTML = emptyRow;
      return;
    }

    const blueParts = participants.filter(p => p.team_side === "BLUE");
    const redParts = participants.filter(p => p.team_side === "RED");

    const renderRows = (list) => list.map(p => `
      <tr>
        <td><strong style="color: var(--accent-cyan);">${p.role || "FLEX"}</strong></td>
        <td style="font-weight: 700;">${p.player_name || "Jogador"}</td>
        <td>${p.champion_name || "Campeão"}</td>
        <td><span style="font-family: var(--font-mono);">${p.kills ?? 0}/${p.deaths ?? 0}/${p.assists ?? 0}</span> <small style="color: var(--accent-gold);">(${p.kda_ratio ?? 0})</small></td>
        <td>${p.cs ?? 0}</td>
        <td>${(p.gold || 0).toLocaleString()}</td>
        <td><strong style="color: var(--accent-green);">${(p.damage_to_champions || 0).toLocaleString()}</strong></td>
        <td>${p.kill_participation_pct ?? 0}%</td>
        <td>${p.gold_share_pct ?? 0}%</td>
      </tr>
    `).join("");

    blueTableBody.innerHTML = blueParts.length > 0 ? renderRows(blueParts) : `<tr><td colspan="9" style="text-align:center; padding:1rem;">Sem dados do lado azul</td></tr>`;
    redTableBody.innerHTML = redParts.length > 0 ? renderRows(redParts) : `<tr><td colspan="9" style="text-align:center; padding:1rem;">Sem dados do lado vermelho</td></tr>`;
  }

  init();
});
