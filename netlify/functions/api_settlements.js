// netlify/functions/api_settlements.js
// REGRA INCONTESTÁVEL: 100% DADOS REAIS - ZERO DADOS FICTÍCIOS
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
    const { data, error } = await supabase
      .from("settlement_dossiers")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(50);

    if (error || !data) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify([])
      };
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(data)
    };
  } catch (err) {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify([])
    };
  }
};
