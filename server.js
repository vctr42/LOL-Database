// server.js - Servidor de Desenvolvimento Local com Emulação das Netlify Functions
require("dotenv").config();
const http = require("http");
const fs = require("fs");
const path = require("path");
const url = require("url");

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

const server = http.createServer(async (req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // 1. Emulação de Netlify Functions (/api/* ou /.netlify/functions/*)
  if (pathname.startsWith("/api/") || pathname.startsWith("/.netlify/functions/")) {
    const functionName = pathname.replace(/^\/(api|\.netlify\/functions)\//, "").split("/")[0];

    const event = {
      httpMethod: req.method,
      queryStringParameters: parsedUrl.query,
      headers: req.headers,
      path: pathname,
      body: null
    };

    let handler = null;
    if (functionName === "api_settlements") handler = apiSettlements.handler;
    else if (functionName === "api_h2h") handler = apiH2H.handler;
    else if (functionName === "scan_matches") handler = scanMatches.handler;

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

  // Se não tiver extensão, tentar .html (ex: /h2h -> /h2h.html)
  if (!path.extname(filePath) && fs.existsSync(filePath + ".html")) {
    filePath = filePath + ".html";
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      // Fallback para index.html ou 404
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

server.listen(PORT, () => {
  console.log("=================================================");
  console.log(`🚀 Servidor Local LOL-Database iniciado!`);
  console.log(`🌐 Dashboard:  http://localhost:${PORT}`);
  console.log(`⚔️  H2H:        http://localhost:${PORT}/h2h`);
  console.log(`👤 Telemetria: http://localhost:${PORT}/telemetry`);
  console.log(`⚡ API:        http://localhost:${PORT}/api/api_settlements`);
  console.log("=================================================");
});
