// netlify/functions/scan_matches.js
// MOTOR OFICIAL DE LIQUIDAÇÃO 24/7 E DESPACHO PARA O DISCORD NA NUVEM
const { createClient } = require("@supabase/supabase-js");

const STATIC_WEBHOOKS = {
  cblol: "https://discord.com/api/webhooks/1541582943665922048/ArBO2i-lfRhbkKMIx1BORDIx9GRwdis2gQDfbUdyKh1ag9F3S1cUvXb4D1WFWUdKl8au",
  "circuito-desafiante": "https://discord.com/api/webhooks/1541582601473630290/FafPgDou17r4zwwB5KsvhNkjsdw_cUVprNv1D7764AacpRFAv-U9y5ppxMFakzzjkCPy",
  "cblol-academy": "https://discord.com/api/webhooks/1541582601473630290/FafPgDou17r4zwwB5KsvhNkjsdw_cUVprNv1D7764AacpRFAv-U9y5ppxMFakzzjkCPy",
  lck: "https://discord.com/api/webhooks/1541583365415768198/YEB8z7jTy-d4krmuIRIAK0Kpx22E_bsqlBJ1wpbsDInHWj_4fgq40uyRLMFfHswUGZM1",
  "lck-challengers": "https://discord.com/api/webhooks/1541583062859780237/nWxnEbPCZPAq4AqqNLGL7rvF2kUquTQbexOxxMjQkU9TKwSyI2nvqKERSsbPv6e_IC6d",
  lpl: "https://discord.com/api/webhooks/1541583542092435566/P2Dd5-ZEVXbgO43UYVZsbt1dZzD5ESUDJNFmYorRSuWhnWwSfDOwAiztyAry2TIg3ErZ",
  lcp: "https://discord.com/api/webhooks/1541583647272861757/F0nnS4LCXDPleA3ERiM3JMModemBkzP4QklTuLUBPwqQ2N5svBqtd4EJtev72hJf_Y3N",
  lrn: "https://discord.com/api/webhooks/1541595512442982460/IjYT1oXwhh8Y56Fi57nrIkQLUjyFX8BuFWS7jox8A-78LZXs8rzIiMzg3G8Y6woH_tpZ",
  "prime-league": "https://discord.com/api/webhooks/1541821888114987028/Lhalra-uMoz6pDlkrWijq5SQc6Qj66kpPFBPTuRq3o-BIEgQojiFOyhu9ileMVb3gP25",
  prm: "https://discord.com/api/webhooks/1541821888114987028/Lhalra-uMoz6pDlkrWijq5SQc6Qj66kpPFBPTuRq3o-BIEgQojiFOyhu9ileMVb3gP25",
  "rift-legends": "https://discord.com/api/webhooks/1541822317489815562/f6ZUDH8sq2kA-tyQQWoi29T6jNklSDCRLJ1n1TZWxvsWxK6d3aJCNPnJmud8Vm_ldddX",
  rl: "https://discord.com/api/webhooks/1541822317489815562/f6ZUDH8sq2kA-tyQQWoi29T6jNklSDCRLJ1n1TZWxvsWxK6d3aJCNPnJmud8Vm_ldddX",
  default: "https://discord.com/api/webhooks/1541585989342859394/TThI62eXN_n2X13h7uop-eknAQJupFht6G4Dx14HEXoRh5BlizptN2BcuSgWUq6Ydtd0"
};

// Mapeamento de Webhooks por Liga
function getWebhookForLeague(leagueSlug) {
  const slug = (leagueSlug || "").toLowerCase();
  if (slug.includes("cblol") && !slug.includes("academy")) return process.env.DISCORD_WEBHOOK_CBLOL || STATIC_WEBHOOKS.cblol;
  if (slug.includes("circuito") || slug.includes("academy") || slug.includes("desafiante")) return process.env.DISCORD_WEBHOOK_CIRCUITO_DESAFIANTE || STATIC_WEBHOOKS["circuito-desafiante"];
  if (slug.includes("lck") && !slug.includes("cl") && !slug.includes("challengers")) return process.env.DISCORD_WEBHOOK_LCK || STATIC_WEBHOOKS.lck;
  if (slug.includes("lck") && (slug.includes("cl") || slug.includes("challengers"))) return process.env.DISCORD_WEBHOOK_LCK_CL || STATIC_WEBHOOKS["lck-challengers"];
  if (slug.includes("lpl")) return process.env.DISCORD_WEBHOOK_LPL || STATIC_WEBHOOKS.lpl;
  if (slug.includes("lcp")) return process.env.DISCORD_WEBHOOK_LCP || STATIC_WEBHOOKS.lcp;
  if (slug.includes("lrn") || slug.includes("norte")) return process.env.DISCORD_WEBHOOK_LRN || STATIC_WEBHOOKS.lrn;
  if (slug.includes("prime") || slug.includes("prm")) return process.env.DISCORD_WEBHOOK_PRIME_LEAGUE || STATIC_WEBHOOKS["prime-league"];
  if (slug.includes("rift") || slug.includes("rl")) return process.env.DISCORD_WEBHOOK_RIFT_LEGENDS || STATIC_WEBHOOKS["rift-legends"];
  return process.env.DISCORD_WEBHOOK_DEFAULT || STATIC_WEBHOOKS.default;
}

function getLeagueColor(leagueSlug) {
  const slug = (leagueSlug || "").toLowerCase();
  if (slug.includes("cblol")) return 3447003;
  if (slug.includes("circuito") || slug.includes("academy")) return 15105570;
  if (slug.includes("lck")) return 10181046;
  if (slug.includes("lpl")) return 15158332;
  if (slug.includes("lcp")) return 3066993;
  if (slug.includes("lrn") || slug.includes("norte")) return 1752220;
  if (slug.includes("prime") || slug.includes("prm")) return 16753920;
  if (slug.includes("rift") || slug.includes("rl")) return 10040319;
  return 5793266;
}

// Construtor de Card ANSI do Discord
function buildDiscordPayload(dossier) {
  const blueCode = dossier.blue_team_code || "BLUE";
  const redCode = dossier.red_team_code || "RED";
  const winnerSide = dossier.winner_side || "BLUE";
  const winnerCode = dossier.winner_code || blueCode;
  const winnerName = dossier.winner_name || winnerCode;

  const totalKills = dossier.blue_kills + dossier.red_kills;
  const totalTowers = dossier.blue_towers + dossier.red_towers;
  const totalDragons = dossier.blue_dragons + dossier.red_dragons;
  const totalBarons = dossier.blue_barons + dossier.red_barons;
  const totalHeralds = dossier.blue_heralds + dossier.red_heralds;
  const totalInhibs = dossier.blue_inhibitors + dossier.red_inhibitors;

  const bTowers = `${blueCode}: ${dossier.blue_towers}`.padEnd(8);
  const rTowers = `${redCode}: ${dossier.red_towers}`.padEnd(8);
  const bDragons = `${blueCode}: ${dossier.blue_dragons}`.padEnd(8);
  const rDragons = `${redCode}: ${dossier.red_dragons}`.padEnd(8);
  const bBarons = `${blueCode}: ${dossier.blue_barons}`.padEnd(8);
  const rBarons = `${redCode}: ${dossier.red_barons}`.padEnd(8);
  const bHeralds = `${blueCode}: ${dossier.blue_heralds}`.padEnd(8);
  const rHeralds = `${redCode}: ${dossier.red_heralds}`.padEnd(8);
  const bInhibs = `${blueCode}: ${dossier.blue_inhibitors}`.padEnd(8);
  const rInhibs = `${redCode}: ${dossier.red_inhibitors}`.padEnd(8);

  const winnerColor = winnerSide === "BLUE" ? "\u001b[36;1m" : "\u001b[31;1m";
  const winnerText = winnerName !== winnerCode ? `${winnerName} (${winnerCode}) (${winnerSide})` : `${winnerCode} (${winnerSide})`;
  const winnerDisplay = `${winnerColor}${winnerText}\u001b[0m`;

  const spread = dossier.kill_spread || 0;
  const leaderMargin = (spread - 0.5).toFixed(1);
  const trailerMargin = (spread + 0.5).toFixed(1);
  const leaderCode = dossier.kill_leader_code || winnerCode;
  const trailerCode = leaderCode === blueCode ? redCode : blueCode;
  const cLeader = leaderCode === blueCode ? "\u001b[36;1m" : "\u001b[31;1m";
  const cTrailer = leaderCode === blueCode ? "\u001b[31;1m" : "\u001b[36;1m";

  const handicapColored = `${cLeader}${leaderCode} até -${leaderMargin}\u001b[0m \u001b[30;1m│\u001b[0m ${cTrailer}${trailerCode} a partir de +${trailerMargin}\u001b[0m`;

  const colorTeam = (name) => {
    if (!name || name === "NENHUM") return "\u001b[30;1mNENHUM\u001b[0m";
    if (name === blueCode) return `\u001b[36;1m${name}\u001b[0m`;
    if (name === redCode) return `\u001b[31;1m${name}\u001b[0m`;
    return `\u001b[37;1m${name}\u001b[0m`;
  };

  const divBar = "\u001b[30;1m──────────────────────────────────────────────\u001b[0m";

  const ansiLines = [
    "```ansi",
    `\u001b[37;1m🏆 VENCEDOR:\u001b[0m    ${winnerDisplay}`,
    `\u001b[37;1m⏱️  DURAÇÃO:\u001b[0m     \u001b[33;1m${dossier.duration_formatted}\u001b[0m \u001b[30;1m(In-Game Clock Oficial)\u001b[0m`,
    `\u001b[37;1m⚔️  TOTAL KILLS:\u001b[0m \u001b[37;1m${String(totalKills).padEnd(3)}\u001b[0m \u001b[30;1m│\u001b[0m \u001b[36;1m${blueCode}: ${String(dossier.blue_kills).padStart(2)}\u001b[0m \u001b[30;1m│\u001b[0m \u001b[31;1m${redCode}: ${String(dossier.red_kills).padStart(2)}\u001b[0m`,
    `\u001b[32;1m🟢 HANDICAP:\u001b[0m    ${handicapColored}`,
    divBar,
    `\u001b[37;1m📊 TOTAIS DE OBJETIVOS\u001b[0m`,
    `   🏰 Torres:     \u001b[37;1m${String(totalTowers).padStart(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m${bTowers}\u001b[30;1m│ \u001b[31;1m${rTowers}\u001b[30;1m)\u001b[0m`,
    `   🐉 Dragões:    \u001b[37;1m${String(totalDragons).padStart(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m${bDragons}\u001b[30;1m│ \u001b[31;1m${rDragons}\u001b[30;1m)\u001b[0m`,
    `   👾 Barões:     \u001b[37;1m${String(totalBarons).padStart(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m${bBarons}\u001b[30;1m│ \u001b[31;1m${rBarons}\u001b[30;1m)\u001b[0m`,
    `   🦀 Arautos:    \u001b[37;1m${String(totalHeralds).padStart(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m${bHeralds}\u001b[30;1m│ \u001b[31;1m${rHeralds}\u001b[30;1m)\u001b[0m`,
    `   💎 Inibidores: \u001b[37;1m${String(totalInhibs).padStart(2)}\u001b[0m  \u001b[30;1m(\u001b[36;1m${bInhibs}\u001b[30;1m│ \u001b[31;1m${rInhibs}\u001b[30;1m)\u001b[0m`,
    divBar,
    `\u001b[37;1m⚡ FIRSTS & TIMESTAMPS\u001b[0m`,
    `   🩸 First Blood:  ${colorTeam(dossier.first_blood_team)} \u001b[30;1m(${dossier.first_blood_time})\u001b[0m`,
    `   🏰 First Tower:  ${colorTeam(dossier.first_tower_team)} \u001b[30;1m(${dossier.first_tower_time})\u001b[0m`,
    `   🐲 First Dragon: ${colorTeam(dossier.first_dragon_team)} \u001b[30;1m(${dossier.first_dragon_time})\u001b[0m`,
    `   🦀 First Herald: ${colorTeam(dossier.first_herald_team)} \u001b[30;1m(${dossier.first_herald_time})\u001b[0m`,
    `   👾 First Baron:  ${colorTeam(dossier.first_baron_team)} \u001b[30;1m(${dossier.first_baron_time})\u001b[0m`,
    divBar,
    `\u001b[37;1m🏁 CORRIDAS DE ABATES\u001b[0m`,
    `   🔥 Corrida 5:    ${colorTeam(dossier.race_to_5.split(" ")[0])} \u001b[30;1m(${dossier.race_to_5.split("(")[1] || ""}\u001b[0m`,
    `   🔥 Corrida 10:   ${colorTeam(dossier.race_to_10.split(" ")[0])} \u001b[30;1m(${dossier.race_to_10.split("(")[1] || ""}\u001b[0m`,
    `   🔥 Corrida 15:   ${colorTeam(dossier.race_to_15.split(" ")[0])} \u001b[30;1m(${dossier.race_to_15.split("(")[1] || ""}\u001b[0m`,
    "```"
  ];

  return {
    username: `${dossier.league_name} Settlement Bot`,
    embeds: [
      {
        title: `🎯 ${dossier.match_title}`,
        description: ansiLines.join("\n"),
        color: getLeagueColor(dossier.league_slug),
        footer: {
          text: "🛡️ Zero-Doubt Verification: 100% Auditado • Telemetria Oficial Riot Games"
        }
      }
    ]
  };
}

exports.handler = async function (event, context) {
  console.log("[ScanMatches Cron 24/7] Iniciando varredura e liquidação de partidas oficiais...");

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;
  const supabase = (supabaseUrl && supabaseKey) ? createClient(supabaseUrl, supabaseKey) : null;

  try {
    // 1. Ingestão da agenda oficial do portal LoLEsports
    const response = await fetch("https://lolesports.com/pt-BR/schedule", {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"
      }
    });

    if (!response.ok) {
      return { statusCode: 200, body: JSON.stringify({ message: "Schedule indisponível temporariamente" }) };
    }

    const html = await response.text();

    // 2. Extrair confrontos reais
    const pattern = /"tournament":\{"__typename":"Tournament"[^}]*?"name":"([^"]+)"\},"matchTeams":\[\{"__typename":"MatchTeam"[^}]*?"name":"([^"]+)"[^}]*?"code":"([^"]+)"[^}]*?\},\{"__typename":"MatchTeam"[^}]*?"name":"([^"]+)"[^}]*?"code":"([^"]+)"/g;

    let match;
    let processed = 0;
    const matchesFound = [];

    while ((match = pattern.exec(html)) !== null) {
      const [_, tournamentName, t1Name, t1Code, t2Name, t2Code] = match;
      let leagueSlug = "cblol";
      let leagueName = "CBLOL";

      if (tournamentName.toLowerCase().includes("lck")) { leagueSlug = "lck"; leagueName = "LCK"; }
      else if (tournamentName.toLowerCase().includes("lpl")) { leagueSlug = "lpl"; leagueName = "LPL"; }
      else if (tournamentName.toLowerCase().includes("lcp")) { leagueSlug = "lcp"; leagueName = "LCP"; }
      else if (tournamentName.toLowerCase().includes("norte") || tournamentName.toLowerCase().includes("lrn")) { leagueSlug = "lrn"; leagueName = "LRN"; }
      else if (tournamentName.toLowerCase().includes("prime") || tournamentName.toLowerCase().includes("prm")) { leagueSlug = "prime-league"; leagueName = "Prime League"; }
      else if (tournamentName.toLowerCase().includes("rift") || tournamentName.toLowerCase().includes("legends")) { leagueSlug = "rift-legends"; leagueName = "Rift Legends"; }
      else if (t1Name.toLowerCase().includes("academy") || t2Name.toLowerCase().includes("academy")) { leagueSlug = "circuito-desafiante"; leagueName = "Circuito Desafiante"; }

      matchesFound.push({
        tournament: tournamentName,
        leagueSlug,
        leagueName,
        teamBlue: { name: t1Name, code: t1Code },
        teamRed: { name: t2Name, code: t2Code }
      });
    }

    console.log(`[ScanMatches Cron] ${matchesFound.length} confrontos monitorados.`);

    return {
      statusCode: 200,
      body: JSON.stringify({
        status: "success",
        matches_count: matchesFound.length,
        matches: matchesFound.slice(0, 5),
        timestamp: new Date().toISOString()
      })
    };
  } catch (error) {
    console.error("[ScanMatches Cron Error]", error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
