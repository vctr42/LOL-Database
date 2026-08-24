// public/js/h2h.js
// REGRA INCONTESTÁVEL: 100% DADOS REAIS - ZERO DADOS FICTÍCIOS

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
    const teamA = (teamAInput.value || "").trim().toUpperCase();
    const teamB = (teamBInput.value || "").trim().toUpperCase();

    if (!teamA || !teamB) {
      alert("Por favor, digite a sigla de duas equipes para comparar.");
      return;
    }

    nameTeamA.textContent = teamA;
    nameTeamB.textContent = teamB;

    try {
      const resp = await fetch(`/api/api_h2h?team_a=${encodeURIComponent(teamA)}&team_b=${encodeURIComponent(teamB)}`);
      if (resp.ok) {
        const data = await resp.json();
        renderH2H(data, teamA, teamB);
      } else {
        renderEmptyH2H(teamA, teamB);
      }
    } catch (e) {
      renderEmptyH2H(teamA, teamB);
    }
  }

  function renderH2H(data, teamA, teamB) {
    if (data && data.direct_h2h_found && data.total_games > 0) {
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

      h2hAvgDuration.textContent = `Duração Média Real: ${data.avg_duration_formatted || "--:--"}`;

      if (data.recent_games && data.recent_games.length > 0) {
        h2hTableBody.innerHTML = data.recent_games.map(g => `
          <tr>
            <td><strong>${g.match_title || `Mapa ${g.game_number || 1}`}</strong></td>
            <td><span class="green-highlight">${g.winner_code || "--"}</span></td>
            <td>${g.duration_formatted || "--:--"}</td>
            <td>${g.blue_kills ?? 0} x ${g.red_kills ?? 0}</td>
            <td>${g.first_blood_team || "--"}</td>
            <td>${g.first_tower_team || "--"}</td>
            <td>${g.handicap_green_line || "--"}</td>
          </tr>
        `).join("");
      } else {
        h2hTableBody.innerHTML = `
          <tr>
            <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">
              Nenhum mapa individual detalhado encontrado para este confronto no Data Lake.
            </td>
          </tr>
        `;
      }
    } else {
      renderEmptyH2H(teamA, teamB);
    }
  }

  function renderEmptyH2H(teamA, teamB) {
    winsTeamA.textContent = "0 vitórias";
    winRateTeamA.textContent = "0.0%";
    killsTeamA.textContent = "--";
    fbRateTeamA.textContent = "--";
    ftRateTeamA.textContent = "--";
    fdRateTeamA.textContent = "--";

    winsTeamB.textContent = "0 vitórias";
    winRateTeamB.textContent = "0.0%";
    killsTeamB.textContent = "--";
    fbRateTeamB.textContent = "--";
    ftRateTeamB.textContent = "--";
    fdRateTeamB.textContent = "--";

    h2hAvgDuration.textContent = "Duração Média: Sem registros";

    h2hTableBody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2rem;">
          Nenhum confronto direto oficial registrado no Data Lake entre ${teamA} e ${teamB}.
        </td>
      </tr>
    `;
  }
});
