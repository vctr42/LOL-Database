// web/js/h2h.js
// LIVE BET CORE • Comparador Head-to-Head com Ingestão Direta do Supabase

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
      const headers = {
        "apikey": APP_CONFIG.SUPABASE_ANON_KEY,
        "Authorization": `Bearer ${APP_CONFIG.SUPABASE_ANON_KEY}`
      };

      const resp = await fetch(`${APP_CONFIG.SUPABASE_URL}/rest/v1/lol_games?select=*&limit=100`, { headers });
      
      if (resp.ok) {
        const games = await resp.json();
        const relevant = games.filter(g => {
          const w = (g.winner_code || "").toUpperCase();
          const hl = (g.handicap_green_line || "").toUpperCase();
          return (w === teamA || w === teamB || hl.includes(teamA) || hl.includes(teamB));
        });

        if (relevant.length > 0) {
          let winsA = 0, winsB = 0, totalKillsA = 0, totalKillsB = 0;
          let fbA = 0, fbB = 0, ftA = 0, ftB = 0, fdA = 0, fdB = 0;
          let totalDurationSec = 0;

          relevant.forEach(g => {
            const w = (g.winner_code || "").toUpperCase();
            if (w === teamA) winsA++;
            if (w === teamB) winsB++;
            if (g.first_blood_team === teamA) fbA++;
            if (g.first_blood_team === teamB) fbB++;
            if (g.first_tower_team === teamA) ftA++;
            if (g.first_tower_team === teamB) ftB++;
            if (g.first_dragon_team === teamA) fdA++;
            if (g.first_dragon_team === teamB) fdB++;
            
            totalKillsA += (g.winner_side === 'BLUE' && w === teamA ? g.blue_kills : g.red_kills) || 12;
            totalKillsB += (g.winner_side === 'BLUE' && w === teamB ? g.blue_kills : g.red_kills) || 12;
            totalDurationSec += g.duration_seconds || 1920;
          });

          const total = winsA + winsB || relevant.length || 1;
          const avgSec = Math.round(totalDurationSec / relevant.length);
          const avgM = Math.floor(avgSec / 60);
          const avgS = avgSec % 60;

          winsTeamA.textContent = `${winsA} vitórias`;
          winRateTeamA.textContent = `${Math.round((winsA / total) * 100)}%`;
          killsTeamA.textContent = (totalKillsA / total).toFixed(1);
          fbRateTeamA.textContent = `${Math.round((fbA / total) * 100)}%`;
          ftRateTeamA.textContent = `${Math.round((ftA / total) * 100)}%`;
          fdRateTeamA.textContent = `${Math.round((fdA / total) * 100)}%`;

          winsTeamB.textContent = `${winsB} vitórias`;
          winRateTeamB.textContent = `${Math.round((winsB / total) * 100)}%`;
          killsTeamB.textContent = (totalKillsB / total).toFixed(1);
          fbRateTeamB.textContent = `${Math.round((fbB / total) * 100)}%`;
          ftRateTeamB.textContent = `${Math.round((ftB / total) * 100)}%`;
          fdRateTeamB.textContent = `${Math.round((fdB / total) * 100)}%`;

          h2hAvgDuration.textContent = `Duração Média: ${avgM}:${avgS.toString().padStart(2, "0")}`;

          h2hTableBody.innerHTML = relevant.map(g => `
            <tr>
              <td style="font-family: var(--font-mono);">${g.created_at ? g.created_at.substring(0, 10) : "2026-08"}</td>
              <td><strong style="color: var(--accent-cyan);">${g.winner_code}</strong></td>
              <td style="font-family: var(--font-mono);">${g.duration_formatted}</td>
              <td style="font-family: var(--font-mono);">${g.blue_kills || 0} x ${g.red_kills || 0}</td>
              <td>${g.first_blood_team || "--"}</td>
              <td>${g.first_tower_team || "--"}</td>
              <td>${g.first_dragon_team || "--"}</td>
            </tr>
          `).join("");

          return;
        }
      }

      renderEmptyH2H(teamA, teamB);
    } catch (e) {
      console.error(e);
      renderEmptyH2H(teamA, teamB);
    }
  }

  function renderEmptyH2H(teamA, teamB) {
    winsTeamA.textContent = "0";
    winRateTeamA.textContent = "0%";
    killsTeamA.textContent = "--";
    fbRateTeamA.textContent = "--%";
    ftRateTeamA.textContent = "--%";
    fdRateTeamA.textContent = "--%";

    winsTeamB.textContent = "0";
    winRateTeamB.textContent = "0%";
    killsTeamB.textContent = "--";
    fbRateTeamB.textContent = "--%";
    ftRateTeamB.textContent = "--%";
    fdRateTeamB.textContent = "--%";

    h2hAvgDuration.textContent = "Duração Média: --:--";
    h2hTableBody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2rem;">
          Nenhum confronto direto registrado entre ${teamA} e ${teamB} no Data Lake.
        </td>
      </tr>
    `;
  }
});
