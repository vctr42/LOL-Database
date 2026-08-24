// public/js/h2h.js

document.addEventListener("DOMContentLoaded", () => {
  const teamAInput = document.getElementById("teamAInput");
  const teamBInput = document.getElementById("teamBInput");
  const btnCompare = document.getElementById("btnCompare");

  const nameTeamA = document.getElementById("nameTeamA");
  const winsTeamA = document.getElementById("winsTeamA");
  const winRateTeamA = document.getElementById("winRateTeamA");
  const killsTeamA = document.getElementById("killsTeamA");
  const fbRateTeamA = document.getElementById("fbRateTeamA");
  const ftRateTeamA = document.getElementById("ftRateTeamA");
  const fdRateTeamA = document.getElementById("fdRateTeamA");

  const nameTeamB = document.getElementById("nameTeamB");
  const winsTeamB = document.getElementById("winsTeamB");
  const winRateTeamB = document.getElementById("winRateTeamB");
  const killsTeamB = document.getElementById("killsTeamB");
  const fbRateTeamB = document.getElementById("fbRateTeamB");
  const ftRateTeamB = document.getElementById("ftRateTeamB");
  const fdRateTeamB = document.getElementById("fdRateTeamB");

  const h2hAvgDuration = document.getElementById("h2hAvgDuration");
  const h2hTableBody = document.getElementById("h2hTableBody");

  btnCompare.addEventListener("click", () => {
    executeH2H();
  });

  async function executeH2H() {
    const teamA = (teamAInput.value || "T1").trim().toUpperCase();
    const teamB = (teamBInput.value || "GEN").trim().toUpperCase();

    nameTeamA.textContent = teamA;
    nameTeamB.textContent = teamB;

    try {
      const resp = await fetch(`/api/api_h2h?team_a=${teamA}&team_b=${teamB}`);
      if (resp.ok) {
        const data = await resp.json();
        renderH2H(data, teamA, teamB);
      } else {
        renderMockH2H(teamA, teamB);
      }
    } catch (e) {
      renderMockH2H(teamA, teamB);
    }
  }

  function renderH2H(data, teamA, teamB) {
    if (data.direct_h2h_found) {
      winsTeamA.textContent = `${data.wins_a} vitórias`;
      winRateTeamA.textContent = `${data.win_rate_a_pct}%`;
      killsTeamA.textContent = `${data.avg_kills_a} / mapa`;
      fbRateTeamA.textContent = `${data.first_blood_rate_a_pct}%`;
      ftRateTeamA.textContent = `${data.first_tower_rate_a_pct}%`;
      fdRateTeamA.textContent = `${data.first_dragon_rate_a_pct}%`;

      winsTeamB.textContent = `${data.wins_b} vitórias`;
      winRateTeamB.textContent = `${data.win_rate_b_pct}%`;
      killsTeamB.textContent = `${data.avg_kills_b} / mapa`;
      fbRateTeamB.textContent = `${data.first_blood_rate_b_pct}%`;
      ftRateTeamB.textContent = `${data.first_tower_rate_b_pct}%`;
      fdRateTeamB.textContent = `${data.first_dragon_rate_b_pct}%`;

      h2hAvgDuration.textContent = `Duração Média: ${data.avg_duration_formatted || "33:40"}`;
    } else {
      renderMockH2H(teamA, teamB);
    }
  }

  function renderMockH2H(teamA, teamB) {
    winsTeamA.textContent = "6 vitórias";
    winRateTeamA.textContent = "60.0%";
    killsTeamA.textContent = "15.4 / mapa";
    fbRateTeamA.textContent = "70.0%";
    ftRateTeamA.textContent = "60.0%";
    fdRateTeamA.textContent = "50.0%";

    winsTeamB.textContent = "4 vitórias";
    winRateTeamB.textContent = "40.0%";
    killsTeamB.textContent = "12.8 / mapa";
    fbRateTeamB.textContent = "30.0%";
    ftRateTeamB.textContent = "40.0%";
    fdRateTeamB.textContent = "50.0%";

    h2hAvgDuration.textContent = "Duração Média: 32:20";

    h2hTableBody.innerHTML = `
      <tr>
        <td><strong>[LCK] ${teamA} vs ${teamB} — MAPA 3</strong></td>
        <td><span class="green-highlight">${teamA}</span></td>
        <td>31:45</td>
        <td>18 x 11</td>
        <td>${teamA}</td>
        <td>${teamA}</td>
        <td>${teamA} até -6.5</td>
      </tr>
      <tr>
        <td><strong>[LCK] ${teamA} vs ${teamB} — MAPA 2</strong></td>
        <td><span class="green-highlight">${teamB}</span></td>
        <td>35:10</td>
        <td>11 x 18</td>
        <td>${teamA}</td>
        <td>${teamB}</td>
        <td>${teamB} até -6.5</td>
      </tr>
      <tr>
        <td><strong>[LCK] ${teamA} vs ${teamB} — MAPA 1</strong></td>
        <td><span class="green-highlight">${teamA}</span></td>
        <td>29:50</td>
        <td>16 x 8</td>
        <td>${teamA}</td>
        <td>${teamA}</td>
        <td>${teamA} até -7.5</td>
      </tr>
    `;
  }

  // Executar busca inicial
  executeH2H();
});
