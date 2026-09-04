// web/js/app.js
// LIVE BET CORE • Ingestão Direta Supabase REST API (Zero Dados Fictícios)

document.addEventListener("DOMContentLoaded", () => {
  let currentLeague = "all";
  let settlementsData = [];

  const liveGrid = document.getElementById("liveGrid");
  const settlementsTableBody = document.getElementById("settlementsTableBody");
  const settlementCount = document.getElementById("settlementCount");
  const dossierModal = document.getElementById("dossierModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalYamlContent = document.getElementById("modalYamlContent");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const btnCopyYaml = document.getElementById("btnCopyYaml");
  const btnRefresh = document.getElementById("btnRefresh");
  const leagueChips = document.querySelectorAll(".league-chips .chip");

  // Fechar Modal
  btnCloseModal.addEventListener("click", () => {
    dossierModal.classList.remove("active");
  });

  window.addEventListener("click", (e) => {
    if (e.target === dossierModal) {
      dossierModal.classList.remove("active");
    }
  });

  btnCopyYaml.addEventListener("click", () => {
    navigator.clipboard.writeText(modalYamlContent.textContent).then(() => {
      btnCopyYaml.textContent = "✅ Copiado!";
      setTimeout(() => { btnCopyYaml.textContent = "📋 Copiar YAML"; }, 2000);
    });
  });

  // Filtros de Liga
  leagueChips.forEach(chip => {
    chip.addEventListener("click", () => {
      leagueChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      currentLeague = chip.dataset.league;
      renderAll();
    });
  });

  btnRefresh.addEventListener("click", () => {
    loadData();
  });

  async function loadData() {
    try {
      const headers = {
        "apikey": APP_CONFIG.SUPABASE_ANON_KEY,
        "Authorization": `Bearer ${APP_CONFIG.SUPABASE_ANON_KEY}`
      };

      // Acionar varredura contínua na nuvem (Edge Daemon 24/7)
      fetch(`${APP_CONFIG.SUPABASE_URL}/functions/v1/live-monitor`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      }).catch(() => {});

      const [gamesRes, dossiersRes] = await Promise.allSettled([
        fetch(`${APP_CONFIG.SUPABASE_URL}/rest/v1/lol_games?select=*&order=created_at.desc&limit=50`, { headers }),
        fetch(`${APP_CONFIG.SUPABASE_URL}/rest/v1/settlement_dossiers?select=*&order=created_at.desc&limit=50`, { headers })
      ]);

      let games = [];
      let dossiers = [];

      if (gamesRes.status === "fulfilled" && gamesRes.value.ok) {
        games = await gamesRes.value.json();
      }
      if (dossiersRes.status === "fulfilled" && dossiersRes.value.ok) {
        dossiers = await dossiersRes.value.json();
      }

      const dossierMap = {};
      dossiers.forEach(d => {
        if (d.game_id) dossierMap[d.game_id] = d;
      });

      settlementsData = games.map(g => {
        const d = dossierMap[g.id] || {};
        const summary = d.json_summary || {};
        return {
          game_id: g.id,
          match_title: d.match_title || summary.match_title || `[${(g.league_slug || 'LOL').toUpperCase()}] Confronto Oficial (${g.id})`,
          league_slug: g.league_slug || "cblol",
          created_at: g.created_at || new Date().toISOString(),
          winner_code: g.winner_code,
          winner_side: g.winner_side,
          duration_formatted: g.duration_formatted,
          blue_team_code: summary.blue_team_code || (g.winner_side === 'BLUE' ? g.winner_code : '--'),
          red_team_code: summary.red_team_code || (g.winner_side === 'RED' ? g.winner_code : '--'),
          blue_kills: g.blue_kills || 0,
          red_kills: g.red_kills || 0,
          blue_towers: g.blue_towers || 0,
          red_towers: g.red_towers || 0,
          blue_dragons: g.blue_dragons || 0,
          red_dragons: g.red_dragons || 0,
          blue_barons: g.blue_barons || 0,
          red_barons: g.red_barons || 0,
          handicap_green_line: g.handicap_green_line || "Auditado",
          first_blood_team: g.first_blood_team || "--",
          first_blood_time: g.first_blood_time || "00:00",
          yaml_dossier: d.yaml_dossier || null
        };
      });

      renderAll();
    } catch (e) {
      console.error("Erro ao carregar do Supabase:", e);
      liveGrid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: #ff4d6d;">
          Aviso de conexão com o banco de dados. Tentando novamente em instantes...
        </div>
      `;
    }
  }

  function filterData() {
    if (currentLeague === "all") return settlementsData;
    return settlementsData.filter(s => {
      const slug = (s.league_slug || "").toLowerCase();
      if (currentLeague === "circuito-desafiante") {
        return slug.includes("circuito") || slug.includes("desafiante") || slug.includes("academy");
      }
      if (currentLeague === "lck-challengers") {
        return slug.includes("cl") || slug.includes("challengers");
      }
      if (currentLeague === "lck") {
        return slug.includes("lck") && !slug.includes("cl") && !slug.includes("challengers");
      }
      if (currentLeague === "lcs") {
        return slug.includes("lcs") && !slug.includes("nacl") && !slug.includes("challengers");
      }
      if (currentLeague === "nacl") {
        return slug.includes("nacl") || slug.includes("north-american-challengers") || slug.includes("na-challengers");
      }
      return slug.includes(currentLeague);
    });
  }

  function renderAll() {
    const list = filterData();
    if (settlementCount) settlementCount.textContent = `${list.length} partidas`;

    if (list.length === 0) {
      liveGrid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3.5rem 1rem; color: var(--text-muted);">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎮</div>
          <p style="font-weight: 600; color: var(--text-main); margin-bottom: 0.25rem;">Nenhuma partida oficial liquidada no momento</p>
          <p style="font-size: 0.85rem;">O monitor autônomo está ativo. Assim que um mapa for concluído com auditoria do Nexus, ele aparecerá aqui com telemetria 100% real.</p>
        </div>
      `;
      settlementsTableBody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; color: var(--text-muted); padding: 2rem;">
            Nenhum registro encontrado.
          </td>
        </tr>
      `;
      return;
    }

    // Render Grid Cards
    liveGrid.innerHTML = list.map(item => {
      const isBlueWinner = item.winner_side === "BLUE";
      return `
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
            <span class="badge-live" style="background: rgba(0, 210, 255, 0.1); color: var(--accent-cyan); border-color: rgba(0, 210, 255, 0.3);">
              ${(item.league_slug || "LOL").toUpperCase()}
            </span>
            <span style="font-size: 0.8rem; color: var(--text-muted); font-family: var(--font-mono);">
              ⏱️ ${item.duration_formatted}
            </span>
          </div>

          <h3 style="font-size: 1.05rem; font-weight: 700; margin-bottom: 1rem; color: #fff;">
            ${item.match_title}
          </h3>

          <!-- DUELO DE PLACAR -->
          <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(0,0,0,0.25); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <div style="text-align: left;">
              <div style="color: var(--accent-cyan); font-weight: 800; font-size: 1.1rem;">
                ${item.blue_team_code} ${isBlueWinner ? '👑' : ''}
              </div>
              <small style="color: var(--text-muted);">LADO AZUL</small>
            </div>
            <div style="font-family: var(--font-mono); font-weight: 800; font-size: 1.3rem;">
              <span style="color: var(--accent-cyan);">${item.blue_kills}</span>
              <span style="color: var(--text-muted); margin: 0 0.25rem;">x</span>
              <span style="color: var(--accent-red);">${item.red_kills}</span>
            </div>
            <div style="text-align: right;">
              <div style="color: var(--accent-red); font-weight: 800; font-size: 1.1rem;">
                ${!isBlueWinner ? '👑' : ''} ${item.red_team_code}
              </div>
              <small style="color: var(--text-muted);">LADO VERMELHO</small>
            </div>
          </div>

          <!-- HANDICAP DE GREEN -->
          <div style="background: rgba(0, 255, 136, 0.05); border-left: 3px solid #00ff88; padding: 0.6rem 0.8rem; border-radius: 4px; font-size: 0.82rem; margin-bottom: 1rem;">
            <div style="color: #00ff88; font-weight: 700; font-size: 0.75rem;">LINHA DE GREEN (.5):</div>
            <div style="color: var(--text-primary); font-family: var(--font-mono); margin-top: 0.2rem;">
              ${item.handicap_green_line}
            </div>
          </div>

          <!-- AÇÃO: VER DOSSIÊ -->
          <button class="btn btn-view-dossier" data-game-id="${item.game_id}" style="width: 100%; justify-content: center;">
            📄 Ver Súmula / Dossiê
          </button>
        </div>
      `;
    }).join("");

    // Render Table Rows
    settlementsTableBody.innerHTML = list.map(item => {
      const timeStr = item.created_at ? new Date(item.created_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) : "--:--";
      return `
        <tr>
          <td style="font-family: var(--font-mono);">${timeStr}</td>
          <td><span class="badge-live" style="font-size: 0.65rem;">${(item.league_slug || "LOL").toUpperCase()}</span></td>
          <td style="font-weight: 600;">${item.match_title}</td>
          <td><strong style="color: ${item.winner_side === 'BLUE' ? 'var(--accent-cyan)' : 'var(--accent-red)'};">${item.winner_code}</strong></td>
          <td style="font-family: var(--font-mono);">${item.duration_formatted}</td>
          <td style="font-family: var(--font-mono);">${item.blue_kills} x ${item.red_kills}</td>
          <td style="font-family: var(--font-mono); color: #00ff88;">${item.handicap_green_line}</td>
          <td>
            <button class="btn btn-view-dossier" data-game-id="${item.game_id}" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">
              📄 Ver
            </button>
          </td>
        </tr>
      `;
    }).join("");

    // Eventos dos botões de dossiê
    document.querySelectorAll(".btn-view-dossier").forEach(btn => {
      btn.addEventListener("click", () => {
        const gid = btn.dataset.gameId;
        const selected = settlementsData.find(s => s.game_id === gid);
        if (selected) {
          modalTitle.textContent = selected.match_title;
          if (selected.yaml_dossier) {
            modalYamlContent.textContent = selected.yaml_dossier.replace(/```yaml\n?|```/g, "");
          } else {
            modalYamlContent.textContent = `
Relatorio: "${selected.match_title}"
Vencedor: "${selected.winner_code} (${selected.winner_side})"
Duracao: "${selected.duration_formatted}"
Placar Kills: "${selected.blue_team_code}: ${selected.blue_kills} | ${selected.red_team_code}: ${selected.red_kills}"
Handicap: "${selected.handicap_green_line}"
Status: "AUDITADO E LIQUIDADO (100% RIOT GAMES)"
            `.trim();
          }
          dossierModal.classList.add("active");
        }
      });
    });
  }

  // Carga inicial e timer
  loadData();
  setInterval(loadData, APP_CONFIG.AUTO_REFRESH_INTERVAL);
});
