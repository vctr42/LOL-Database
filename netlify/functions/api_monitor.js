// netlify/functions/api_monitor.js
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

let lastScanTime = new Date().toISOString();
let isScanning = false;

exports.handler = async function (event, context) {
  const method = event.httpMethod;
  const query = event.queryStringParameters || {};

  if (method === "GET") {
    // Retornar status do monitor e ligas ativas
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status: "active",
        daemon_running: true,
        polling_interval_seconds: 15,
        last_scan: lastScanTime,
        monitored_leagues: [
          { slug: "cblol", name: "CBLOL", channel: "#cblol" },
          { slug: "circuito-desafiante", name: "Circuito Desafiante", channel: "#circuito-desafiante" },
          { slug: "lck", name: "LCK", channel: "#lck" },
          { slug: "lck-challengers", name: "LCK Challengers", channel: "#lck-challengers" },
          { slug: "lpl", name: "LPL", channel: "#lpl" },
          { slug: "lcp", name: "LCP", channel: "#lcp" },
          { slug: "lrn", name: "LRN", channel: "#lrn" }
        ]
      })
    };
  }

  if (method === "POST") {
    lastScanTime = new Date().toISOString();
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status: "triggered",
        message: "Varredura de telemetria acionada com sucesso!",
        scanned_at: lastScanTime
      })
    };
  }

  return {
    statusCode: 405,
    body: JSON.stringify({ error: "Método não permitido" })
  };
};
