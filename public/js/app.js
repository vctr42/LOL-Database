// public/js/app.js
// REGRA INCONTESTÁVEL: 100% DADOS REAIS DA RIOT GAMES - ZERO DADOS FICTÍCIOS

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

  // Botão de Forçar Varredura no Monitor 24/7
  const btnTriggerScan = document.getElementById("btnTriggerScan");
  const monitorInfo = document.getElementById("monitorInfo");
  if (btnTriggerScan) {
    btnTriggerScan.addEventListener("click", async () => {
      btnTriggerScan.textContent = "⏳ Varrendo Riot...";
      btnTriggerScan.disabled = true;
      try {
        const resp = await fetch("/api/api_monitor", { method: "POST" });
        const res = await resp.json();
        if (monitorInfo) {
          monitorInfo.textContent = `Última varredura manual: ${new Date().toLocaleTimeString("pt-BR")} • Escaneando frames ao vivo`;
        }
        btnTriggerScan.textContent = "✅ Varredura Concluída";
        await loadData();
      } catch (e) {
        console.error("Erro ao varrer monitor:", e);
        btnTriggerScan.textContent = "⚠️ Erro";
      }
      setTimeout(() => {
        btnTriggerScan.textContent = "⚡ Forçar Varredura Agora";
        btnTriggerScan.disabled = false;
      }, 3000);
    });
  }

  async function loadData() {
    try {
      const response = await fetch("/api/api_settlements");
      if (response.ok) {
        const data = await response.json();
        settlementsData = Array.isArray(data) ? data : [];
      } else {
        settlementsData = [];
      }
    } catch (err) {
      settlementsData = [];
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
        <div class="card" style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 3rem 1.5rem;">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">📡</div>
          <div style="font-weight: 700; color: var(--text-primary); margin-bottom: 0.25rem;">Nenhuma partida oficial liquidada no momento</div>
          <div style="font-size: 0.85rem;">O motor 24/7 está monitorando a CDN da Riot Games. Novas partidas serão listadas assim que os confrontos oficiais forem concluídos.</div>
        </div>
      `;
      return;
    }

    liveGrid.innerHTML = filtered.slice(0, 4).map(item => {
      const isBlueWin = item.winner_side === "BLUE";
      const blueScore = item.blue_kills ?? 0;
      const redScore = item.red_kills ?? 0;
      const blueTeam = item.team_blue_code || "AZUL";
      const redTeam = item.team_red_code || "VERMELHO";

      return `
        <div class="card">
          <div class="card-header">
            <span class="card-league">${(item.league_name || item.league_slug || "LOL").toUpperCase()}</span>
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
          <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2.5rem 1rem;">
            Nenhum dossiê oficial registrado para esta liga. Aguardando finalização de partidas na Riot Games.
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
    modalYamlContent.textContent = item.yaml_dossier || "Dossiê YAML oficial não disponível para esta partida.";
    dossierModal.classList.add("active");
  };

  loadData();
});
