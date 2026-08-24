// netlify/functions/api_h2h.js
// REGRA INCONTESTÁVEL: 100% DADOS REAIS - ZERO DADOS FICTÍCIOS
const { createClient } = require("@supabase/supabase-js");

exports.handler = async function (event, context) {
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json"
  };

  const params = event.queryStringParameters || {};
  const teamA = (params.team_a || "").toUpperCase().trim();
  const teamB = (params.team_b || "").toUpperCase().trim();

  if (!teamA || !teamB) {
    return {
      statusCode: 400,
      headers,
      body: JSON.stringify({ error: "Parâmetros team_a e team_b são obrigatórios." })
    };
  }

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_ANON_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ direct_h2h_found: false, team_a: teamA, team_b: teamB, total_games: 0, recent_games: [] })
    };
  }

  try {
    const supabase = createClient(supabaseUrl, supabaseKey);
    const { data: games, error } = await supabase
      .from("games")
      .select("*")
      .order("settled_at", { ascending: false })
      .limit(50);

    if (error || !games || games.length === 0) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({ direct_h2h_found: false, team_a: teamA, team_b: teamB, total_games: 0, recent_games: [] })
      };
    }

    // Filtrar jogos onde ambos participaram
    const h2hGames = games.filter(g => 
      ((g.winner_code === teamA && g.loser_code === teamB) || (g.winner_code === teamB && g.loser_code === teamA))
    );

    if (h2hGames.length === 0) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({ direct_h2h_found: false, team_a: teamA, team_b: teamB, total_games: 0, recent_games: [] })
      };
    }

    const winsA = h2hGames.filter(g => g.winner_code === teamA).length;
    const winsB = h2hGames.length - winsA;
    const totalSec = h2hGames.reduce((acc, g) => acc + (g.duration_seconds || 0), 0);
    const avgSec = Math.floor(totalSec / h2hGames.length);
    const avgFmt = `${String(Math.floor(avgSec / 60)).padStart(2, '0')}:${String(avgSec % 60).padStart(2, '0')}`;

    const fbA = h2hGames.filter(g => (g.first_blood_team || "").toUpperCase() === teamA).length;
    const ftA = h2hGames.filter(g => (g.first_tower_team || "").toUpperCase() === teamA).length;
    const fdA = h2hGames.filter(g => (g.first_dragon_team || "").toUpperCase() === teamA).length;
    const fbaronA = h2hGames.filter(g => (g.first_baron_team || "").toUpperCase() === teamA).length;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        direct_h2h_found: true,
        team_a: teamA,
        team_b: teamB,
        total_games: h2hGames.length,
        wins_a: winsA,
        wins_b: winsB,
        win_rate_a_pct: Number(((winsA / h2hGames.length) * 100).toFixed(1)),
        win_rate_b_pct: Number(((winsB / h2hGames.length) * 100).toFixed(1)),
        avg_duration_formatted: avgFmt,
        avg_duration_seconds: avgSec,
        first_blood_rate_a_pct: Number(((fbA / h2hGames.length) * 100).toFixed(1)),
        first_tower_rate_a_pct: Number(((ftA / h2hGames.length) * 100).toFixed(1)),
        first_dragon_rate_a_pct: Number(((fdA / h2hGames.length) * 100).toFixed(1)),
        first_baron_rate_a_pct: Number(((fbaronA / h2hGames.length) * 100).toFixed(1)),
        recent_games: h2hGames.slice(0, 10)
      })
    };
  } catch (e) {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ direct_h2h_found: false, team_a: teamA, team_b: teamB, total_games: 0, recent_games: [] })
    };
  }
};
