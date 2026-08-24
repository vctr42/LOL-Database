// public/js/app.js

document.addEventListener("DOMContentLoaded", () => {
  let currentLeague = "all";
  let settlementsData = [];

  const liveGrid = document.getElementById("liveGrid");
  const settlementsTableBody = document.getElementById("settlementsTableBody");
  const dossierModal = document.getElementById("dossierModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalYamlContent = document.getElementById("modalYamlContent");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const btnCopyYaml = document.getElementById("btnCopyYaml");
  const btnRefresh = document.getElementById("btnRefresh");
  const leagueChips = document.querySelectorAll(".chip");

  // Fechar Modal
  btnCloseModal.addEventListener("click", () => {
    dossierModal.classList.remove("active");
  });

  dossierModal.addEventListener("click", (e) => {
    if (e.target === dossierModal) {
      dossierModal.classList.remove("active");
    }
  });

  // Copiar YAML
  btnCopyYaml.addEventListener("click", () => {
    navigator.clipboard.writeText(modalYamlContent.textContent);
    const originalText = btnCopyYaml.textContent;
    btnCopyYaml.textContent = "✅ Copiado!";
    setTimeout(() => {
      btnCopyYaml.textContent = originalText;
    }, 2000);
  });

  // Filtro por Liga
  leagueChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      leagueChips.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      currentLeague = chip.dataset.league;
      renderSettlements();
      renderLiveCards();
    });
  });

  // Botão de Refresh
  btnRefresh.addEventListener("click", () => {
    loadData();
  });

  async function loadData() {
    try {
      const response = await fetch("/api/api_settlements");
      if (response.ok) {
        settlementsData = await response.json();
      } else {
        settlementsData = getSampleData();
      }
    } catch (err) {
      settlementsData = getSampleData();
    }
    renderSettlements();
    renderLiveCards();
  }

  function renderLiveCards() {
    const filtered = currentLeague === "all" 
      ? settlementsData 
      : settlementsData.filter(s => (s.league_slug || "").toLowerCase() === currentLeague);

    if (!filtered || filtered.length === 0) {
      liveGrid.innerHTML = `
        <div class="card" style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
          Nenhuma partida recente encontrada para a liga selecionada.
        </div>
      `;
      return;
    }

    liveGrid.innerHTML = filtered.slice(0, 3).map(item => {
      const isBlueWin = item.winner_side === "BLUE";
      const blueScore = item.blue_kills ?? 0;
      const redScore = item.red_kills ?? 0;
      const blueTeam = item.team_blue_code || "BLUE";
      const redTeam = item.team_red_code || "RED";

      return `
        <div class="card">
          <div class="card-header">
            <span class="card-league">${item.league_name || item.league_slug || "LEAGUE"}</span>
            <span class="card-time">⏱️ In-Game: ${item.duration_formatted || "00:00"}</span>
          </div>
          <div class="match-vs">
            <div class="team ${isBlueWin ? 'winner' : ''}">
              <span class="team-code">${blueTeam}</span>
              <span class="team-score">${blueScore}</span>
            </div>
            <div class="vs-divider">VS</div>
            <div class="team ${!isBlueWin ? 'winner' : ''}">
              <span class="team-code">${redTeam}</span>
              <span class="team-score">${redScore}</span>
            </div>
          </div>
          <div class="card-details">
            <div class="detail-row">
              <span class="detail-label">Vencedor Oficial:</span>
              <span class="detail-value green-highlight">${item.winner_code || "--"}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Handicap Green:</span>
              <span class="detail-value">${item.handicap_green_line || "--"}</span>
            </div>
            <div style="margin-top: 0.5rem;">
              <button class="btn btn-primary" style="width: 100%;" onclick="window.viewDossier('${item.game_id}')">
                📄 Ver Dossiê YAML
              </button>
            </div>
          </div>
        </div>
      `;
    }).join("");
  }

  function renderSettlements() {
    const filtered = currentLeague === "all" 
      ? settlementsData 
      : settlementsData.filter(s => (s.league_slug || "").toLowerCase() === currentLeague);

    if (!filtered || filtered.length === 0) {
      settlementsTableBody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2rem;">
            Nenhum dossiê de liquidação encontrado.
          </td>
        </tr>
      `;
      return;
    }

    settlementsTableBody.innerHTML = filtered.map(item => `
      <tr>
        <td style="font-weight: 700;">${item.match_title || item.game_id}</td>
        <td><span class="card-league">${(item.league_slug || "LOL").toUpperCase()}</span></td>
        <td><span class="green-highlight">${item.winner_code || "--"}</span></td>
        <td><span style="font-family: var(--font-mono);">${item.duration_formatted || "00:00"}</span></td>
        <td><span style="font-weight: 700;">${item.blue_kills ?? 0} x ${item.red_kills ?? 0}</span></td>
        <td><span style="font-size: 0.85rem; color: var(--accent-cyan);">${item.handicap_green_line || "--"}</span></td>
        <td>
          <button class="btn" onclick="window.viewDossier('${item.game_id}')">
            📋 Dossiê
          </button>
        </td>
      </tr>
    `).join("");
  }

  window.viewDossier = (gameId) => {
    const item = settlementsData.find(s => s.game_id === gameId);
    if (!item) return;
    modalTitle.textContent = item.match_title || `Dossiê ${item.game_id}`;
    modalYamlContent.textContent = item.yaml_dossier || "YAML não disponível.";
    dossierModal.classList.add("active");
  };

  function getSampleData() {
    return [
      {
        id: "dossier_1001",
        game_id: "1001",
        match_id: "match_1001",
        league_slug: "cblol",
        league_name: "CBLOL",
        match_title: "[CBLOL] PNG vs LLL — MAPA 1",
        team_blue_code: "PNG",
        team_red_code: "LLL",
        winner_code: "PNG",
        winner_side: "BLUE",
        duration_formatted: "32:45",
        blue_kills: 19,
        red_kills: 7,
        handicap_green_line: "PNG até -11.5 | LLL a partir de +12.5",
        yaml_dossier: "```yaml\nRelatorio: \"[CBLOL] PNG vs LLL — MAPA 1\"\nLiga: \"CBLOL\"\nStatus: \"LIQUIDADO E AUDITADO\"\nDuracao Oficial: \"32:45\"\n\n# --- MONEYLINE & VENCEDOR ---\nVencedor: \"PNG (BLUE)\"\nDerrotado: \"LLL (RED)\"\n\n# --- PLACAR DE ABATES & HANDICAP ---\nPlacar Abates: \"19 x 7\"\nLider Abates: \"PNG (+12)\"\nLinha Fracionaria: \"PNG até -11.5 | LLL a partir de +12.5\"\n\n# --- TOTAIS DE OBJETIVOS (AZUL vs VERMELHO) ---\nTorres: \"9 x 2\"\nDragoes: \"4 x 1\"\nBaroes: \"2 x 0\"\nArautos: \"1 x 1\"\nInibidores: \"2 x 0\"\n\n# --- FIRSTS & CORRIDAS DE ABATES ---\nFirst Blood: \"PNG (03:12)\"\nFirst Tower: \"PNG (14:20)\"\nFirst Dragon: \"PNG (07:45)\"\nFirst Herald: \"LLL (09:10)\"\nFirst Baron: \"PNG (22:30)\"\nCorrida 5 Kills: \"PNG (08:40)\"\nCorrida 10 Kills: \"PNG (18:15)\"\nCorrida 15 Kills: \"PNG (27:02)\"\n\n# --- AUDITORIA ZERO-DOUBT ---\nZero Doubt Gate: \"APROVADO (100% CONFIANCA)\"\n```"
      },
      {
        id: "dossier_1002",
        game_id: "1002",
        match_id: "match_1002",
        league_slug: "lck",
        league_name: "LCK",
        match_title: "[LCK] T1 vs GEN — MAPA 1",
        team_blue_code: "T1",
        team_red_code: "GEN",
        winner_code: "GEN",
        winner_side: "RED",
        duration_formatted: "35:10",
        blue_kills: 11,
        red_kills: 18,
        handicap_green_line: "GEN até -6.5 | T1 a partir de +7.5",
        yaml_dossier: "```yaml\nRelatorio: \"[LCK] T1 vs GEN — MAPA 1\"\nLiga: \"LCK\"\nStatus: \"LIQUIDADO E AUDITADO\"\nDuracao Oficial: \"35:10\"\n\n# --- MONEYLINE & VENCEDOR ---\nVencedor: \"GEN (RED)\"\nDerrotado: \"T1 (BLUE)\"\n\n# --- PLACAR DE ABATES & HANDICAP ---\nPlacar Abates: \"11 x 18\"\nLider Abates: \"GEN (+7)\"\nLinha Fracionaria: \"GEN até -6.5 | T1 a partir de +7.5\"\n\n# --- TOTAIS DE OBJETIVOS (AZUL vs VERMELHO) ---\nTorres: \"3 x 10\"\nDragoes: \"2 x 4\"\nBaroes: \"0 x 2\"\nArautos: \"1 x 0\"\nInibidores: \"0 x 2\"\n\n# --- FIRSTS & CORRIDAS DE ABATES ---\nFirst Blood: \"T1 (04:05)\"\nFirst Tower: \"GEN (13:50)\"\nFirst Dragon: \"GEN (06:30)\"\nFirst Herald: \"T1 (08:45)\"\nFirst Baron: \"GEN (24:10)\"\nCorrida 5 Kills: \"GEN (11:20)\"\nCorrida 10 Kills: \"GEN (21:40)\"\nCorrida 15 Kills: \"GEN (29:50)\"\n\n# --- AUDITORIA ZERO-DOUBT ---\nZero Doubt Gate: \"APROVADO (100% CONFIANCA)\"\n```"
      },
      {
        id: "dossier_1003",
        game_id: "1003",
        match_id: "match_1003",
        league_slug: "lcs",
        league_name: "LCS",
        match_title: "[LCS] FLY vs TL — MAPA 2",
        team_blue_code: "FLY",
        team_red_code: "TL",
        winner_code: "FLY",
        winner_side: "BLUE",
        duration_formatted: "28:15",
        blue_kills: 21,
        red_kills: 6,
        handicap_green_line: "FLY até -14.5 | TL a partir de +15.5",
        yaml_dossier: "```yaml\nRelatorio: \"[LCS] FLY vs TL — MAPA 2\"\nLiga: \"LCS\"\nStatus: \"LIQUIDADO E AUDITADO\"\nDuracao Oficial: \"28:15\"\n\n# --- MONEYLINE & VENCEDOR ---\nVencedor: \"FLY (BLUE)\"\nDerrotado: \"TL (RED)\"\n\n# --- PLACAR DE ABATES & HANDICAP ---\nPlacar Abates: \"21 x 6\"\nLider Abates: \"FLY (+15)\"\nLinha Fracionaria: \"FLY até -14.5 | TL a partir de +15.5\"\n\n# --- TOTAIS DE OBJETIVOS (AZUL vs VERMELHO) ---\nTorres: \"11 x 1\"\nDragoes: \"4 x 0\"\nBaroes: \"1 x 0\"\nArautos: \"1 x 0\"\nInibidores: \"3 x 0\"\n\n# --- FIRSTS & CORRIDAS DE ABATES ---\nFirst Blood: \"FLY (02:40)\"\nFirst Tower: \"FLY (11:30)\"\nFirst Dragon: \"FLY (05:50)\"\nFirst Herald: \"FLY (08:15)\"\nFirst Baron: \"FLY (21:05)\"\nCorrida 5 Kills: \"FLY (07:10)\"\nCorrida 10 Kills: \"FLY (14:30)\"\nCorrida 15 Kills: \"FLY (22:15)\"\n\n# --- AUDITORIA ZERO-DOUBT ---\nZero Doubt Gate: \"APROVADO (100% CONFIANCA)\"\n```"
      }
    ];
  }

  loadData();
});
