// netlify/functions/scan_matches.js
const { createClient } = require("@supabase/supabase-js");

exports.handler = async function (event, context) {
  console.log("[ScanMatches Cron] Iniciando varredura oficial de telemetria da Riot Games...");

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;
  const discordWebhookDefault = process.env.DISCORD_WEBHOOK_DEFAULT;

  try {
    // 1. Ingestão da agenda ao vivo da Riot Esports API
    const response = await fetch("https://esports-api.lolesports.com/persisted/val/getLiveDetails?hl=pt-BR", {
      headers: {
        "User-Agent": "LolSettlementHub/1.0",
        "Accept": "application/json"
      }
    });

    if (!response.ok) {
      console.warn("[ScanMatches Cron] Riot API retornou status:", response.status);
      return {
        statusCode: 200,
        body: JSON.stringify({ message: "Riot API indisponível temporariamente", status: response.status })
      };
    }

    const liveData = await response.json();
    const events = (liveData && liveData.data && liveData.data.schedule && liveData.data.schedule.events) || [];

    console.log(`[ScanMatches Cron] ${events.length} eventos inspecionados na agenda.`);

    // 2. Verificar partidas finalizadas com necessidade de auditoria
    let settledCount = 0;

    for (const evt of events) {
      if (evt.state === "completed" && evt.match && evt.match.games) {
        for (const game of evt.match.games) {
          if (game.state === "completed" && game.id) {
            // Verificar se já liquidado no Supabase
            if (supabaseUrl && supabaseKey) {
              const supabase = createClient(supabaseUrl, supabaseKey);
              const { data: existing } = await supabase
                .from("games")
                .select("id")
                .eq("id", game.id)
                .single();

              if (!existing) {
                console.log(`[ScanMatches Cron] Novo mapa identificado para liquidação: ${game.id}`);
                // Disparar ingestão de window/frames
                settledCount++;
              }
            }
          }
        }
      }
    }

    return {
      statusCode: 200,
      body: JSON.stringify({
        status: "success",
        events_scanned: events.length,
        new_settlements: settledCount,
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
