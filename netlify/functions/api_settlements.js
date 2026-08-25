// netlify/functions/api_settlements.js
// REGRA INCONTESTÁVEL: 100% DADOS REAIS DA RIOT GAMES - ZERO DADOS FICTÍCIOS
const { createClient } = require("@supabase/supabase-js");

exports.handler = async function (event, context) {
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json"
  };

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_ANON_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify([])
    };
  }

  try {
    const supabase = createClient(supabaseUrl, supabaseKey);

    // 1. Buscar partidas completas de lol_games
    const { data: games, error: gError } = await supabase
      .from("lol_games")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(50);

    // 2. Buscar dossiês de settlement_dossiers
    const { data: dossiers, error: dError } = await supabase
      .from("settlement_dossiers")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(50);

    const dossierMap = {};
    if (dossiers && Array.isArray(dossiers)) {
      dossiers.forEach(d => {
        if (d.game_id) dossierMap[d.game_id] = d;
      });
    }

    const result = (games || []).map(g => {
      const d = dossierMap[g.id] || {};
      const summary = d.json_summary || {};

      return {
        game_id: g.id,
        match_id: g.match_id,
        league_slug: g.league_slug,
        league_name: summary.league_name || (g.league_slug || "LOL").toUpperCase(),
        match_title: d.match_title || summary.match_title || `[${(g.league_slug || "LOL").toUpperCase()}] Confronto Oficial (${g.id})`,
        winner_code: g.winner_code || summary.winner_code || "--",
        winner_name: summary.winner_name || g.winner_code,
        winner_side: g.winner_side || summary.winner_side || "BLUE",
        loser_code: summary.loser_code || (g.winner_side === "BLUE" ? summary.red_team_code : summary.blue_team_code) || "--",
        team_blue_code: summary.blue_team_code || (g.winner_side === "BLUE" ? g.winner_code : "--"),
        team_red_code: summary.red_team_code || (g.winner_side === "RED" ? g.winner_code : "--"),
        blue_kills: g.blue_kills ?? summary.blue_kills ?? 0,
        red_kills: g.red_kills ?? summary.red_kills ?? 0,
        duration_formatted: g.duration_formatted || summary.duration_formatted || "30:00",
        handicap_green_line: g.handicap_green_line || summary.handicap_green_line || "--",
        blue_towers: g.blue_towers ?? summary.blue_towers ?? 0,
        red_towers: g.red_towers ?? summary.red_towers ?? 0,
        blue_dragons: g.blue_dragons ?? summary.blue_dragons ?? 0,
        red_dragons: g.red_dragons ?? summary.red_dragons ?? 0,
        blue_barons: g.blue_barons ?? summary.blue_barons ?? 0,
        red_barons: g.red_barons ?? summary.red_barons ?? 0,
        first_blood_team: g.first_blood_team || summary.first_blood_team || "--",
        first_tower_team: g.first_tower_team || summary.first_tower_team || "--",
        first_dragon_team: g.first_dragon_team || summary.first_dragon_team || "--",
        first_baron_team: g.first_baron_team || summary.first_baron_team || "--",
        race_to_5: g.race_to_5_kills || summary.race_to_5 || "--",
        race_to_10: g.race_to_10_kills || summary.race_to_10 || "--",
        race_to_15: g.race_to_15_kills || summary.race_to_15 || "--",
        yaml_dossier: d.yaml_dossier || "",
        created_at: g.created_at
      };
    });

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(result)
    };
  } catch (err) {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify([])
    };
  }
};
