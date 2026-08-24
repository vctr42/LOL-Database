# 🎮 LOL-Database & Data Lake

> **Motor Autônomo de Liquidação de Apostas, Telemetria Oficial da Riot Games & Data Lake de Esports**

![Netlify Status](https://img.shields.io/badge/Netlify-Serverless%2024%2F7-00C7B7?logo=netlify)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL%20Data%20Lake-3ECF8E?logo=supabase)
![Riot Games](https://img.shields.io/badge/Riot%20Games-Official%20In--Game%20Clock-EB0029)
![Discord](https://img.shields.io/badge/Discord-YAML%20Formatted-5865F2?logo=discord)

---

## 🎯 Visão Geral

O **LOL-Database** é um sistema desacoplado, resiliente e autônomo projetado para auditar e liquidar instantaneamente mercados de apostas de League of Legends profissional (CBLOL, LCK, LPL, LEC, LCS, Worlds, MSI) no segundo exato em que o Nexus é destruído.

### 🛡️ Pilares Fundamentais (Diretrizes do `LICOES.md`)

1. **In-Game Clock Oficial Estrito:** A duração da partida é calculada com precisão de milissegundos utilizando exclusivamente o relógio de jogo do servidor da Riot (`00:00` até o frame de término), imune a pausas técnicas de palco, *chronobreaks* e atrasos de transmissão.
2. **Zero-Doubt Verification Gate:** Qualquer inconsistência de dados (ouro zerado, ausência de frame final, vencedor incerto ou telemetria incompleta) bloqueia imediatamente o envio do relatório.
3. **Data Lake Estruturado:** Persistência de 100% dos dados coletivos e individuais dos 10 jogadores de cada mapa no Supabase (PostgreSQL) com suporte a fallback SQLite local.
4. **Layout Monospaçado em YAML:** Relatórios padronizados para o Discord em blocos ````yaml```` com sintaxe harmonizada para coloração perfeita (rótulos em azul e números destacados).
5. **Arquitetura Cloud & Serverless 24/7:** Execução contínua sem depender de computador local ligado, utilizando Netlify Scheduled Functions.

---

## 📂 Estrutura do Projeto

```
LIVE BET CORE/
├── netlify.toml              # Configuração de Serverless, Headers e Cron 24/7
├── package.json              # Dependências Node.js (Netlify Functions / Supabase)
├── requirements.txt          # Dependências Python (Pydantic, Pytest, Requests)
├── supabase_schema.sql       # Schema DDL do Data Lake para o Supabase
├── .env.example              # Modelo de variáveis de ambiente
│
├── config/
│   ├── settings.py           # Leitura centralizada de variáveis de ambiente
│   └── league_channels.json  # Mapeamento de canais/webhooks por Liga
│
├── core/
│   ├── riot_feed.py          # Cliente de telemetria da Riot Games & In-Game Clock
│   ├── audit_gate.py         # Zero-Doubt Verification Gate
│   ├── settlement.py         # Compilador de liquidação de mercados & handicap .5
│   └── database.py           # Persistência híbrida Supabase / SQLite
│
├── discord/
│   ├── embeds.py             # Construtor do bloco monospaçado YAML
│   └── router.py             # Roteador multi-canais por liga
│
├── analytics/
│   └── h2h_engine.py         # Motor analítico Head-to-Head e tendências
│
├── public/                   # Dashboard Web Moderno (Dark Mode Esports)
│   ├── index.html            # Monitor ao vivo e histórico de liquidações
│   ├── h2h.html              # Comparador direto de times (H2H)
│   ├── telemetry.html        # Telemetria individual dos 10 jogadores
│   ├── css/style.css
│   └── js/
│
├── netlify/functions/        # Funções Serverless & Scheduled Cron
│   ├── scan_matches.js       # Varredura agendada 24/7
│   ├── api_settlements.js    # API REST de relatórios
│   └── api_h2h.js            # API REST de H2H
│
└── tests/                    # Suíte de Testes Automatizados
    ├── mock_data.py
    ├── test_in_game_clock.py
    ├── test_audit_gate.py
    ├── test_settlement.py
    ├── test_discord_format.py
    ├── test_database.py
    └── test_h2h_engine.py
```

---

## 🚀 Como Executar Localmente

### 1. Instalação de Dependências

```bash
# Dependências Python
pip install -r requirements.txt

# Dependências Node.js
npm install
```

### 2. Rodar a Suíte de Testes Automatizados

```bash
pytest -v
```

### 3. Iniciar o Dashboard Web Local

```bash
npm start
```
Acesse `http://localhost:8888` no seu navegador.

---

## 🗄️ Configuração do Supabase (Data Lake)

1. Crie um novo projeto no [Supabase](https://supabase.com).
2. Abra o **SQL Editor** no painel do Supabase.
3. Cole e execute o conteúdo do arquivo [`supabase_schema.sql`](supabase_schema.sql).
4. No Netlify ou no arquivo `.env`, preencha as credenciais:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`

---

## ☁️ Deploy no Netlify

1. Faça o push do repositório para o GitHub:
   ```bash
   git init
   git add .
   git commit -m "feat: lol-database initial release"
   git remote add origin https://github.com/vctr42/LOL-Database.git
   git push -u origin main
   ```
2. No Netlify, vincule o repositório `LOL-Database`.
3. Configure as variáveis de ambiente no painel do Netlify (`Site configuration > Environment variables`).
4. O deploy será realizado e as Netlify Functions estarão ativas para monitoramento 24/7!
