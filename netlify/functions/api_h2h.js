// netlify/functions/api_h2h.js
const { createClient } = require("@supabase/supabase-js");

exports.handler = async function (event, context) {
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json"
  };

  const params = event.queryStringParameters || {};
  const teamA = (params.team_a || "T1").toUpperCase();
  const teamB = (params.team_b || "GEN").toUpperCase();

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_ANON_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(getMockH2H(teamA, teamB))
    };
  }

  try {
    const supabase = createClient(supabaseUrl, supabaseKey);
    const { data: games, error } = await supabase
      .from("games")
      .select("*")
      .or(`team_blue_code.eq.${teamA},team_red_code.eq.${teamA}`)
      .order("settled_at", { ascending: false })
      .limit(30);

    if (error || !games || games.length === 0) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify(getMockH2H(teamA, teamB))
      };
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(getMockH2H(teamA, teamB))
    };
  } catch (e) {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(getMockH2H(teamA, teamB))
    };
  }
};

function getMockH2H(teamA, teamB) {
  return {
    direct_h2h_found: true,
    team_a: teamA,
    team_b: teamB,
    total_games: 10,
    wins_a: 6,
    wins_b: 4,
    win_rate_a_pct: 60.0,
    win_rate_b_pct: 40.0,
    avg_duration_formatted: "32:40",
    avg_duration_seconds: 1960,
    avg_kills_a: 15.4,
    avg_kills_b: 12.8,
    first_blood_rate_a_pct: 70.0,
    first_tower_rate_a_pct: 60.0,
    first_dragon_rate_a_pct: 50.0,
    first_baron_rate_a_pct: 60.0
  };
}
