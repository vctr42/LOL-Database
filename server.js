// server.js - Servidor de Desenvolvimento Local & Monitor Contínuo 24/7
require("dotenv").config();
const http = require("http");
const fs = require("fs");
const path = require("path");
const url = require("url");
const { spawn } = require("child_process");

const PORT = process.env.PORT || 8888;
const PUBLIC_DIR = path.join(__dirname, "public");

const MIME_TYPES = {
  ".html": "text/html",
  ".css": "text/css",
  ".js": "text/javascript",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon"
};

// Carregar handlers das Netlify Functions
const apiSettlements = require("./netlify/functions/api_settlements.js");
const apiH2H = require("./netlify/functions/api_h2h.js");
const scanMatches = require("./netlify/functions/scan_matches.js");
const apiMonitor = require("./netlify/functions/api_monitor.js");
const apiSettleLive = require("./netlify/functions/api_settle_live.js");

const server = http.createServer(async (req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // 1. Emulação de Netlify Functions (/api/* ou /.netlify/functions/*)
  if (pathname.startsWith("/api/") || pathname.startsWith("/.netlify/functions/")) {
    const functionName = pathname.replace(/^\/(api|\.netlify\/functions)\//, "").split("/")[0];

    // Ler body para requisições POST/PUT
    let rawBody = "";
    if (req.method === "POST" || req.method === "PUT") {
      await new Promise((resolve) => {
        req.on("data", (chunk) => (rawBody += chunk));
        req.on("end", resolve);
      });
    }

    const event = {
      httpMethod: req.method,
      queryStringParameters: parsedUrl.query,
      headers: req.headers,
      path: pathname,
      body: rawBody
    };

    let handler = null;
    if (functionName === "api_settlements") handler = apiSettlements.handler;
    else if (functionName === "api_h2h") handler = apiH2H.handler;
    else if (functionName === "scan_matches") handler = scanMatches.handler;
    else if (functionName === "api_monitor") handler = apiMonitor.handler;
    else if (functionName === "api_settle_live") handler = apiSettleLive.handler;

    if (handler) {
      try {
        const response = await handler(event, {});
        res.writeHead(response.statusCode || 200, {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          ...(response.headers || {})
        });
        res.end(response.body || "");
        return;
      } catch (err) {
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: err.message }));
        return;
      }
    } else {
      res.writeHead(404, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: `Function ${functionName} não encontrada.` }));
      return;
    }
  }

  // 2. Servir Arquivos Estáticos da Pasta public/
  let filePath = path.join(PUBLIC_DIR, pathname === "/" ? "index.html" : pathname);

  if (!path.extname(filePath) && fs.existsSync(filePath + ".html")) {
    filePath = filePath + ".html";
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("404 - Página não encontrada");
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || "application/octet-stream";

    res.writeHead(200, { "Content-Type": contentType });
    fs.createReadStream(filePath).pipe(res);
  });
});

// Inicializar Monitor Contínuo Integrado em Background
function startIntegratedLiveMonitor() {
  console.log("📡 [Monitor 24/7 Integrado] Iniciando daemon de telemetria contínua...");
  const pythonCmd = process.platform === "win32" ? "python" : "python3";
  
  try {
    const monitorProcess = spawn(pythonCmd, ["live_monitor.py"], {
      stdio: ["ignore", "pipe", "pipe"],
      cwd: __dirname
    });

    monitorProcess.stdout.on("data", (data) => {
      const msg = data.toString().trim();
      if (msg) console.log(`🤖 ${msg}`);
    });

    monitorProcess.stderr.on("data", (data) => {
      const err = data.toString().trim();
      if (err) console.error(`⚠️ [Monitor Warning] ${err}`);
    });

    monitorProcess.on("close", (code) => {
      console.log(`[Monitor] Processo encerrado com código ${code}. Reiniciando em 5s...`);
      setTimeout(startIntegratedLiveMonitor, 5000);
    });
  } catch (err) {
    console.error(`[Monitor Error] Falha ao iniciar daemon: ${err.message}`);
  }
}

server.listen(PORT, () => {
  console.log("=================================================");
  console.log(`🚀 LOL-Database • Servidor & Monitor 24/7 Ativo!`);
  console.log(`🌐 Dashboard:  http://localhost:${PORT}`);
  console.log(`⚔️  H2H:        http://localhost:${PORT}/h2h`);
  console.log(`👤 Telemetria: http://localhost:${PORT}/telemetry`);
  console.log(`⚡ API:        http://localhost:${PORT}/api/api_settlements`);
  console.log("=================================================");
  
  // Iniciar monitor integrado
  startIntegratedLiveMonitor();
});
