// netlify/functions/scan_matches.js
const { createClient } = require("@supabase/supabase-js");

exports.handler = async function (event, context) {
  console.log("[ScanMatches Cron] Iniciando varredura oficial de telemetria da Riot Games...");

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;

  try {
    // 1. Ingestão da agenda oficial via portal da Riot Games
    const response = await fetch("https://lolesports.com/pt-BR/schedule", {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"
      }
    });

    if (!response.ok) {
      console.warn("[ScanMatches Cron] Schedule portal retornou status:", response.status);
      return {
        statusCode: 200,
        body: JSON.stringify({ message: "Schedule indisponível temporariamente", status: response.status })
      };
    }

    const html = await response.text();
    
    // Expressão regular para extrair confrontos reais
    const pattern = /"tournament":\{"__typename":"Tournament"[^}]*?"name":"([^"]+)"\},"matchTeams":\[\{"__typename":"MatchTeam"[^}]*?"name":"([^"]+)"[^}]*?"code":"([^"]+)"[^}]*?\},\{"__typename":"MatchTeam"[^}]*?"name":"([^"]+)"[^}]*?"code":"([^"]+)"/g;
    
    let matchesCount = 0;
    let match;
    while ((match = pattern.exec(html)) !== null) {
      matchesCount++;
    }

    console.log(`[ScanMatches Cron] ${matchesCount} confrontos oficiais identificados.`);

    return {
      statusCode: 200,
      body: JSON.stringify({
        status: "success",
        matches_monitored: matchesCount,
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
