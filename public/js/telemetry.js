// public/js/telemetry.js

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
      const resp = await fetch("/api/api_settlements");
      if (resp.ok) {
        gamesList = await resp.json();
      } else {
        gamesList = getSampleGames();
      }
    } catch (e) {
      gamesList = getSampleGames();
    }
    populateSelect();
  }

  function populateSelect() {
    gameSelect.innerHTML = gamesList.map(g => `
      <option value="${g.game_id}">${g.match_title || g.game_id}</option>
    `).join("");

    if (gamesList.length > 0) {
      loadGameTelemetry(gamesList[0].game_id);
    }

    gameSelect.addEventListener("change", (e) => {
      loadGameTelemetry(e.target.value);
    });
  }

  async function loadGameTelemetry(gameId) {
    const selected = gamesList.find(g => g.game_id === gameId) || gamesList[0];
    telemetryMapTitle.textContent = selected.match_title || "Telemetria do Mapa";

    const blueCode = selected.team_blue_code || "BLUE";
    const redCode = selected.team_red_code || "RED";

    blueTeamHeader.textContent = `🔵 LADO AZUL (${blueCode})`;
    redTeamHeader.textContent = `🔴 LADO VERMELHO (${redCode})`;

    const participants = getSampleParticipants(blueCode, redCode);
    renderTables(participants);
  }

  function renderTables(participants) {
    const blueParts = participants.filter(p => p.team_side === "BLUE");
    const redParts = participants.filter(p => p.team_side === "RED");

    const renderRows = (list) => list.map(p => `
      <tr>
        <td><strong style="color: var(--accent-cyan);">${p.role}</strong></td>
        <td style="font-weight: 700;">${p.player_name}</td>
        <td>${p.champion_name}</td>
        <td><span style="font-family: var(--font-mono);">${p.kills}/${p.deaths}/${p.assists}</span> <small style="color: var(--accent-gold);">(${p.kda_ratio})</small></td>
        <td>${p.cs}</td>
        <td>${p.gold.toLocaleString()}</td>
        <td><strong style="color: var(--accent-green);">${p.damage_to_champions.toLocaleString()}</strong></td>
        <td>${p.kill_participation_pct}%</td>
        <td>${p.gold_share_pct}%</td>
      </tr>
    `).join("");

    blueTableBody.innerHTML = renderRows(blueParts);
    redTableBody.innerHTML = renderRows(redParts);
  }

  function getSampleGames() {
    return [
      {
        game_id: "1001",
        match_title: "[CBLOL] PNG vs LLL — MAPA 1",
        team_blue_code: "PNG",
        team_red_code: "LLL"
      },
      {
        game_id: "1002",
        match_title: "[LCK] T1 vs GEN — MAPA 1",
        team_blue_code: "T1",
        team_red_code: "GEN"
      }
    ];
  }

  function getSampleParticipants(blueCode, redCode) {
    return [
      // BLUE
      { role: "TOP", player_name: "Wizer", champion_name: "K'Sante", team_side: "BLUE", kills: 3, deaths: 1, assists: 8, kda_ratio: 11.0, cs: 280, gold: 13500, damage_to_champions: 18400, kill_participation_pct: 57.9, gold_share_pct: 21.5 },
      { role: "JUNGLE", player_name: "CarioK", champion_name: "Sejuani", team_side: "BLUE", kills: 2, deaths: 2, assists: 12, kda_ratio: 7.0, cs: 190, gold: 11200, damage_to_champions: 9800, kill_participation_pct: 73.7, gold_share_pct: 17.8 },
      { role: "MID", player_name: "Dynquedo", champion_name: "Azir", team_side: "BLUE", kills: 7, deaths: 1, assists: 6, kda_ratio: 13.0, cs: 320, gold: 16800, damage_to_champions: 28900, kill_participation_pct: 68.4, gold_share_pct: 26.7 },
      { role: "ADC", player_name: "TitaN", champion_name: "Varus", team_side: "BLUE", kills: 6, deaths: 1, assists: 9, kda_ratio: 15.0, cs: 310, gold: 15900, damage_to_champions: 26400, kill_participation_pct: 78.9, gold_share_pct: 25.3 },
      { role: "SUPPORT", player_name: "Kuri", champion_name: "Nautilus", team_side: "BLUE", kills: 1, deaths: 2, assists: 14, kda_ratio: 7.5, cs: 45, gold: 8200, damage_to_champions: 5200, kill_participation_pct: 78.9, gold_share_pct: 13.0 },
      // RED
      { role: "TOP", player_name: "Robo", champion_name: "Renekton", team_side: "RED", kills: 2, deaths: 4, assists: 2, kda_ratio: 1.0, cs: 260, gold: 11800, damage_to_champions: 14200, kill_participation_pct: 57.1, gold_share_pct: 23.6 },
      { role: "JUNGLE", player_name: "Croc", champion_name: "Vi", team_side: "RED", kills: 1, deaths: 4, assists: 4, kda_ratio: 1.25, cs: 175, gold: 9600, damage_to_champions: 7400, kill_participation_pct: 71.4, gold_share_pct: 19.2 },
      { role: "MID", player_name: "Tinowns", champion_name: "Orianna", team_side: "RED", kills: 3, deaths: 3, assists: 2, kda_ratio: 1.67, cs: 290, gold: 13400, damage_to_champions: 21100, kill_participation_pct: 71.4, gold_share_pct: 26.8 },
      { role: "ADC", player_name: "Route", champion_name: "Kalista", team_side: "RED", kills: 1, deaths: 4, assists: 3, kda_ratio: 1.0, cs: 275, gold: 12100, damage_to_champions: 16500, kill_participation_pct: 57.1, gold_share_pct: 24.2 },
      { role: "SUPPORT", player_name: "RedBert", champion_name: "Rell", team_side: "RED", kills: 0, deaths: 4, assists: 5, kda_ratio: 1.25, cs: 38, gold: 6900, damage_to_champions: 3900, kill_participation_pct: 71.4, gold_share_pct: 13.8 }
    ];
  }

  init();
});
