// netlify/functions/scan_matches.js
// ENDPOINT PASSIVO DE CONSULTA DA AGENDA OFICIAL DA RIOT GAMES (SEM DISPARO AUTOMÁTICO EM LOTE)
const { createClient } = require("@supabase/supabase-js");

exports.handler = async function (event, context) {
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json"
  };

  try {
    const response = await fetch("https://lolesports.com/pt-BR/schedule", {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"
      }
    });

    if (!response.ok) {
      return { statusCode: 200, headers, body: JSON.stringify({ message: "Schedule indisponível temporariamente", matches: [] }) };
    }

    const html = await response.text();
    const eventMatchRegex = /\{"__typename":"EventMatch".*?"matchTeams":\[.*?\]\}/g;
    const matchesFound = [];
    let chunk;

    while ((chunk = eventMatchRegex.exec(html)) !== null) {
      try {
        const text = chunk[0];
        const stateMatch = text.match(/"state":"([^"]+)"/);
        const eventState = stateMatch ? stateMatch[1] : "unstarted";

        const idMatch = text.match(/"id":"(\d+)"/);
        const eventId = idMatch ? idMatch[1] : "";

        const leagueNameMatch = text.match(/"league":\{"__typename":"League"[^}]*?"name":"([^"]+)"/);
        const leagueSlugMatch = text.match(/"league":\{"__typename":"League"[^}]*?"slug":"([^"]+)"/);
        const leagueName = leagueNameMatch ? leagueNameMatch[1] : "CBLOL";
        let leagueSlug = leagueSlugMatch ? leagueSlugMatch[1].replace("_", "-").toLowerCase() : "cblol";

        if (leagueSlug.includes("cblol")) leagueSlug = "cblol";
        else if (leagueSlug.includes("prime") || leagueSlug.includes("prm")) leagueSlug = "prime-league";
        else if (leagueSlug.includes("rift") || leagueSlug.includes("legends")) leagueSlug = "rift-legends";
        else if (leagueSlug.includes("norte") || leagueSlug.includes("lrn") || leagueSlug.includes("north") || leagueSlug.includes("south")) leagueSlug = "lrn";
        else if (leagueSlug.includes("desafiante") || leagueSlug.includes("academy") || leagueSlug === "cd") leagueSlug = "circuito-desafiante";
        else if (leagueSlug.includes("challengers") || leagueSlug.includes("lck-cl")) leagueSlug = "lck-challengers";

        const teamMatches = [...text.matchAll(/\{"__typename":"MatchTeam"[^}]*?"name":"([^"]+)"[^}]*?"code":"([^"]+)"[^}]*?"result":\{"__typename":"TeamResult","gameWins":(\d+)/g)];

        if (teamMatches.length >= 2) {
          const t1Name = teamMatches[0][1];
          const t1Code = teamMatches[0][2];
          const t1Wins = parseInt(teamMatches[0][3], 10);

          const t2Name = teamMatches[1][1];
          const t2Code = teamMatches[1][2];
          const t2Wins = parseInt(teamMatches[1][3], 10);

          matchesFound.push({
            eventId,
            eventState,
            leagueName,
            leagueSlug,
            teamBlue: { name: t1Name, code: t1Code, wins: t1Wins },
            teamRed: { name: t2Name, code: t2Code, wins: t2Wins },
            isCompleted: (eventState === "completed" || (t1Wins + t2Wins) > 0)
          });
        }
      } catch (err) {
        continue;
      }
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        status: "success",
        total_events: matchesFound.length,
        matches: matchesFound.slice(0, 10),
        timestamp: new Date().toISOString()
      })
    };
  } catch (error) {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ status: "error", message: error.message, matches: [] })
    };
  }
};
