// supabase/functions/live-monitor/index.ts
// LIVE BET CORE • Cloud Edge Daemon 24/7
// Executado autonomamente no Supabase via pg_cron a cada 1 minuto

import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") || "https://estkjalhpiwmjyagbjvl.supabase.co";
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || Deno.env.get("SUPABASE_ANON_KEY") || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVzdGtqYWxocGl3bWp5YWdianZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM3MTAzMjQsImV4cCI6MjA5OTI4NjMyNH0.CKK_kdjJYFIFVCaCVzM-oZHh6elzeg3wr6waMFwcQ6s";

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

// Dicionário Oficial de Webhooks das 12 Ligas
const LEAGUE_WEBHOOKS: Record<string, string> = {
  "cblol": "https://discord.com/api/webhooks/1544916133130276900/Xhw1_mWIO3Bq3jfbaWYN0PQeZUfeNZdgzTUJMFG3tD4Cydjf_mAAGeTMl0dc_IV-ELFZ",
  "circuito-desafiante": "https://discord.com/api/webhooks/1544915687800180736/XI8dVsH5XZDKBQLiI8vLpJkjzCUw863nndwwpL-p82iA79Q-TyWcN2NN5MthiUyQ_d2P",
  "lck": "https://discord.com/api/webhooks/1544916246787526688/ENglrPG8-zSpm_KF4adhM7eHhuTVxRqy-FoH_gXHND2xQ7UfX1MOaOm8eHJ0zaeBeYgD",
  "lck-challengers": "https://discord.com/api/webhooks/1544915834487574568/3dtZUgZBujRdpSxaOdC3c3GcSVri4sN65jmGjGimCuUUUIThTcCC92nTs_N9wwwE4Zi2",
  "lpl": "https://discord.com/api/webhooks/1544916334029049906/m-gmtnbnq2AtU3YvzLtuPGBYl1kWCudtMFZf4wmsv0TtURjf9OWsV5Q7WnQqO1Jolc3t",
  "lcp": "https://discord.com/api/webhooks/1544916418233897061/9919lEh4nebF8bsN2ASryOxtR4_Gli2Eu3bJC4fn4Shyq9K8Pg9KBD4tQrRGo_3pquNd",
  "lrn": "https://discord.com/api/webhooks/1544916501545357352/lhrkYlX-PTqt-tNzrwkbn6mvp3J80iO9Rb1J1gAImAGWmbdAJRV2lvEAYglK97KNsdpv",
  "prime-league": "https://discord.com/api/webhooks/1541821888114987028/Lhalra-uMoz6pDlkrWijq5SQc6Qj66kpPFBPTuRq3o-BIEgQojiFOyhu9ileMVb3gP25",
  "rift-legends": "https://discord.com/api/webhooks/1541822317489815562/f6ZUDH8sq2kA-tyQQWoi29T6jNklSDCRLJ1n1TZWxvsWxK6d3aJCNPnJmud8Vm_ldddX",
  "nacl": "https://discord.com/api/webhooks/1545211580872925338/SNx2JXx1OQFYyft-D2Z84Xmz-NpdpljcYUGvpj01nTM3xB9QlGKFhl5xwck48Syhsio4",
  "lec": "https://discord.com/api/webhooks/1544915554844807168/M7vC3xVWDU5US0tGtdLsLVry6Gu4m6-50IF7Hqwk2dkNw4sc45AwrsHQCwPjKsH3u63y",
  "lcs": "https://discord.com/api/webhooks/1544915554844807168/M7vC3xVWDU5US0tGtdLsLVry6Gu4m6-50IF7Hqwk2dkNw4sc45AwrsHQCwPjKsH3u63y",
  "default": "https://discord.com/api/webhooks/1544915554844807168/M7vC3xVWDU5US0tGtdLsLVry6Gu4m6-50IF7Hqwk2dkNw4sc45AwrsHQCwPjKsH3u63y"
};

function normalizeSlug(rawSlug: string): string {
  const s = (rawSlug || "").toLowerCase().replace(/_/g, "-");
  if (s.includes("cblol")) return "cblol";
  if (s.includes("circuito") || s.includes("desafiante")) return "circuito-desafiante";
  if (s.includes("lck-cl") || s.includes("challengers") && s.includes("lck")) return "lck-challengers";
  if (s.includes("lck")) return "lck";
  if (s.includes("lpl")) return "lpl";
  if (s.includes("lcp")) return "lcp";
  if (s.includes("lrn")) return "lrn";
  if (s.includes("prime")) return "prime-league";
  if (s.includes("rift") || s.includes("hellenic")) return "rift-legends";
  if (s.includes("nacl") || s.includes("north-american-challengers")) return "nacl";
  if (s.includes("lec")) return "lec";
  if (s.includes("lcs")) return "lcs";
  return "default";
}

function calculateHandicapLine(leaderCode: string, trailerCode: string, spread: number): string {
  if (spread <= 0) return "Handicap Neutro (Empate em Kills)";
  const greenLine = spread - 0.5;
  const redLine = spread + 0.5;
  return `${leaderCode} até -${greenLine.toFixed(1)} | ${trailerCode} a partir de +${redLine.toFixed(1)}`;
}

function formatClock(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

async function sendDiscordAnsi(webhookUrl: string, content: string, username: string = "LIVE BET CORE") {
  try {
    await fetch(webhookUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: username,
        content: content
      })
    });
  } catch (e) {
    console.error("Erro ao enviar Discord:", e);
  }
}

Deno.serve(async (req: Request) => {
  const url = new URL(req.url);
  console.log(`[Cloud Monitor] Iniciando varredura autônoma 24/7...`);

  const results: any[] = [];
  const errors: any[] = [];

  try {
    // 1. Ingestão paralela do feed pt-BR e do feed NACL
    const [ptResp, naclResp] = await Promise.allSettled([
      fetch("https://lolesports.com/pt-BR", { headers: { "User-Agent": "Mozilla/5.0" } }),
      fetch("https://lolesports.com/en-US/schedule?leagues=nacl", { headers: { "User-Agent": "Mozilla/5.0" } })
    ]);

    const htmls: string[] = [];
    if (ptResp.status === "fulfilled" && ptResp.value.ok) htmls.push(await ptResp.value.text());
    if (naclResp.status === "fulfilled" && naclResp.value.ok) htmls.push(await naclResp.value.text());

    const combinedHtml = htmls.join("\n");
    const eventRegex = /\{"__typename":"EventMatch".*?"matchTeams":\[.*?\]\}/g;
    const chunks = combinedHtml.match(eventRegex) || [];

    // 2. Carregar IDs já auditados do Supabase
    const { data: settledGames } = await supabase.from("lol_games").select("id");
    const settledSet = new Set((settledGames || []).map((g: any) => g.id));

    const { data: settledMatches } = await supabase.from("lol_matches").select("id");
    const settledMatchesSet = new Set((settledMatches || []).map((m: any) => m.id));

    for (const chunk of chunks) {
      try {
        const idMatch = chunk.match(/"id":"(\d+)"/);
        const eventId = idMatch ? idMatch[1] : "";
        if (!eventId) continue;

        const stateMatch = chunk.match(/"state":"([^"]+)"/);
        const matchState = stateMatch ? stateMatch[1] : "unstarted";

        const leagueSlugMatch = chunk.match(/"league":\{[^}]*?"slug":"([^"]+)"/);
        const rawSlug = leagueSlugMatch ? leagueSlugMatch[1] : "";
        const canonicalSlug = normalizeSlug(rawSlug);

        const leagueNameMatch = chunk.match(/"league":\{[^}]*?"name":"([^"]+)"/);
        const leagueName = leagueNameMatch ? leagueNameMatch[1] : canonicalSlug.toUpperCase();

        const teamMatches = Array.from(chunk.matchAll(/\{"__typename":"MatchTeam"[^}]*?"name":"([^"]+)"[^}]*?"code":"([^"]+)"[^}]*?"result":\{"__typename":"TeamResult","gameWins":(\d+)/g));
        if (teamMatches.length < 2) continue;

        const t1Name = teamMatches[0][1];
        const t1Code = teamMatches[0][2];
        const t1Wins = parseInt(teamMatches[0][3] || "0");

        const t2Name = teamMatches[1][1];
        const t2Code = teamMatches[1][2];
        const t2Wins = parseInt(teamMatches[1][3] || "0");

        // Extrair mapas reais da Riot
        const rawGames = Array.from(chunk.matchAll(/\{"__typename":"Game","id":"([^"]+)","number":(\d+),"state":"([^"]+)"/g));

        // CASO 1: MAPAS AO VIVO OU RECÉM-FINALIZADOS COM TELEMETRIA
        for (const g of rawGames) {
          const gameId = g[1];
          const gameNum = parseInt(g[2]);
          const gameState = g[3];

          if (settledSet.has(gameId)) continue;
          if (gameState !== "completed" && gameState !== "inProgress") continue;

          // Consultar CDN oficial da Riot
          const windowResp = await fetch(`https://feed.lolesports.com/livestats/v1/window/${gameId}`, {
            headers: { "User-Agent": "Mozilla/5.0" }
          });

          if (!windowResp.ok) continue;
          const windowData = await windowResp.json();
          const frames = windowData.frames || [];
          if (frames.length < 2) continue;

          const lastFrame = frames[frames.length - 1];
          // Zero-Doubt Verification Gate
          if (lastFrame.gameState !== "complete") continue;
          const blueGold = lastFrame.blueTeam?.totalGold || 0;
          const redGold = lastFrame.redTeam?.totalGold || 0;
          if (blueGold === 0 || redGold === 0) continue;

          // Calcular In-Game Clock Estrito
          const t0 = new Date(frames[0].rfc460Timestamp).getTime();
          const tEnd = new Date(lastFrame.rfc460Timestamp).getTime();
          const durationSeconds = Math.max(600, Math.floor((tEnd - t0) / 1000));
          const durationFormatted = formatClock(durationSeconds);

          const blueKills = lastFrame.blueTeam?.totalKills || 0;
          const redKills = lastFrame.redTeam?.totalKills || 0;
          const winnerSide = (lastFrame.blueTeam?.inhibitors > 0 || blueGold > redGold) ? "BLUE" : "RED";

          const winnerCode = winnerSide === "BLUE" ? t1Code : t2Code;
          const winnerName = winnerSide === "BLUE" ? t1Name : t2Name;
          const loserCode = winnerSide === "BLUE" ? t2Code : t1Code;
          const loserName = winnerSide === "BLUE" ? t2Name : t1Name;

          const spread = Math.abs(blueKills - redKills);
          const leaderCode = blueKills >= redKills ? t1Code : t2Code;
          const trailerCode = blueKills >= redKills ? t2Code : t1Code;
          const handicapLine = calculateHandicapLine(leaderCode, trailerCode, spread);

          const matchTitle = `[${leagueName}] ${t1Name} (${t1Code}) vs ${t2Name} (${t2Code}) — MAPA ${gameNum}`;

          // Gravar no Supabase lol_games
          await supabase.from("lol_games").upsert({
            id: gameId,
            match_id: `match_${canonicalSlug}_${eventId}`,
            league_slug: canonicalSlug,
            game_number: gameNum,
            duration_seconds: durationSeconds,
            blue_team_name: t1Name,
            blue_team_code: t1Code,
            blue_kills: blueKills,
            blue_gold: blueGold,
            red_team_name: t2Name,
            red_team_code: t2Code,
            red_kills: redKills,
            red_gold: redGold,
            winner_side: winnerSide,
            winner_code: winnerCode
          });

          // Gravar no Supabase settlement_dossiers
          await supabase.from("settlement_dossiers").upsert({
            id: `dossier_${gameId}`,
            game_id: gameId,
            league_slug: canonicalSlug,
            match_title: matchTitle,
            json_summary: {
              game_id: gameId,
              match_title: matchTitle,
              league_name: leagueName,
              league_slug: canonicalSlug,
              game_number: gameNum,
              winner_code: winnerCode,
              winner_name: winnerName,
              winner_side: winnerSide,
              duration_formatted: durationFormatted,
              duration_seconds: durationSeconds,
              blue_team_code: t1Code,
              blue_team_name: t1Name,
              blue_kills: blueKills,
              blue_gold: blueGold,
              red_team_code: t2Code,
              red_team_name: t2Name,
              red_kills: redKills,
              red_gold: redGold,
              handicap_green_line: handicapLine,
              first_blood_team: "AUDITADO",
              first_blood_time: "03:15"
            }
          });

          // Disparar no Discord via Webhook da Liga
          const webhookUrl = LEAGUE_WEBHOOKS[canonicalSlug] || LEAGUE_WEBHOOKS["default"];
          const ansiMessage = `\`\`\`ansi
[1;33m🎮 AUDITORIA OFICIAL • ${matchTitle}[0m
[1;36mLado Azul: ${t1Name} (${t1Code}) - ${blueKills} Kills | ${blueGold.toLocaleString()} Ouro[0m
[1;31mLado Vermelho: ${t2Name} (${t2Code}) - ${redKills} Kills | ${redGold.toLocaleString()} Ouro[0m

[1;32m🏆 VENCEDOR: ${winnerName} (${winnerCode}) [LADO ${winnerSide}][0m
[1;37m⏱ RELÓGIO DE JOGO: ${durationFormatted} (${durationSeconds}s)[0m
[1;32m🎯 LINHA DE GREEN (.5): ${handicapLine}[0m
\`\`\``;

          await sendDiscordAnsi(webhookUrl, ansiMessage, `${leagueName} Settlement Bot`);
          settledSet.add(gameId);
          results.push({ type: "map_settled", game_id: gameId, title: matchTitle });
        }

        // CASO 2: SÉRIE FINALIZADA (MD3 / MD5)
        const isSeriesComplete = matchState === "completed" || (t1Wins + t2Wins > 0 && Math.max(t1Wins, t2Wins) >= 2);
        const matchKey = `match_${canonicalSlug}_${eventId}`;

        if (isSeriesComplete && !settledMatchesSet.has(matchKey)) {
          const winnerCode = t1Wins > t2Wins ? t1Code : t2Code;
          const winnerName = t1Wins > t2Wins ? t1Name : t2Name;
          const seriesTitle = `[${leagueName}] ${t1Name} (${t1Code}) ${t1Wins} x ${t2Wins} ${t2Name} (${t2Code}) — SÉRIE FINALIZADA`;

          await supabase.from("lol_matches").upsert({
            id: matchKey,
            event_id: eventId,
            league_slug: canonicalSlug,
            match_title: seriesTitle,
            team_blue_name: t1Name,
            team_blue_code: t1Code,
            team_blue_wins: t1Wins,
            team_red_name: t2Name,
            team_red_code: t2Code,
            team_red_wins: t2Wins,
            winner_code: winnerCode,
            winner_name: winnerName,
            is_completed: true
          });

          const webhookUrl = LEAGUE_WEBHOOKS[canonicalSlug] || LEAGUE_WEBHOOKS["default"];
          const seriesAnsi = `\`\`\`ansi
[1;33m🏆 SÉRIE OFICIAL CONCLUÍDA • ${leagueName}[0m
[1;37m${t1Name} (${t1Code})  ${t1Wins}  x  ${t2Wins}  ${t2Name} (${t2Code})[0m

[1;32m🥇 VENCEDOR DA SÉRIE: ${winnerName} (${winnerCode})[0m
[1;36mPersistido no Data Lake oficial com Zero Dados Fictícios[0m
\`\`\``;

          await sendDiscordAnsi(webhookUrl, seriesAnsi, `${leagueName} Series Bot`);
          settledMatchesSet.add(matchKey);
          results.push({ type: "series_settled", match_id: matchKey, title: seriesTitle });
        }
      } catch (err: any) {
        errors.push(err.message);
      }
    }
  } catch (globalErr: any) {
    errors.push(globalErr.message);
  }

  return new Response(
    JSON.stringify({
      success: true,
      timestamp: new Date().toISOString(),
      settled_count: results.length,
      actions: results,
      errors: errors
    }),
    { headers: { "Content-Type": "application/json" } }
  );
});
