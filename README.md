# 🎮 LIVE BET CORE • Telemetria Oficial & Liquidação de Apostas

> **Motor Autônomo 24/7 de Telemetria Oficial da Riot Games, Auditoria Rigorosa de Liquidação de Apostas (Tier 1 & Tier 2 Mundial) e Data Lake Estatístico.**

---

## 💎 Princípios Fundamentais

1. **Regra de Ouro Incontestável (Zero Synthetic Data):**
   * Nenhuma métrica é estimada ou simulada.
   * O in-game clock é extraído diretamente dos frames da CDN oficial da Riot Games, sendo imune a pausas de transmissão ou problemas no palco.
   * Se os frames da CDN não estiverem disponíveis, apenas a súmula oficial de placar de mapas da série é emitida.
2. **Zero-Doubt Verification Gate:**
   * Qualquer inconsistência de integridade (ouro zerado, partida incompleta, duração inferior a 10 minutos) bloqueia o despacho imediatamente.
3. **Persistência Dual e Resiliente:**
   * Supabase PostgreSQL na nuvem para análises remotas e painel web.
   * SQLite local com buffer atômico para garantir funcionamento contínuo mesmo com oscilações de rede.
4. **Despacho Multi-Canais Inteligente no Discord:**
   * Formatação ANSI nativa com cores semânticas para o Lado Azul, Lado Vermelho e Linha de Green (.5).
   * Roteamento para o canal e bot exclusivo de cada liga (CBLOL, Circuito Desafiante, LCK, LCK Challengers, LPL, LEC, LCS, LCP, LRN, Prime League, Rift Legends).

---

## 🏗️ Estrutura do Projeto

```
LIVE BET CORE/
├── config/
│   ├── settings.py          # Configurações tipadas Pydantic
│   └── leagues.json         # Metadados de canais, cores e webhooks
│
├── core/
│   ├── models.py            # Modelos de dados Pydantic v2
│   ├── client.py            # Cliente assíncrono HTTPX para Riot CDN/Schedule
│   ├── audit.py             # Zero-Doubt Verification Gate
│   ├── compiler.py          # Compilador de Liquidação & Handicap (.5)
│   └── tracker.py           # Ledger de idempotência e ciclo de vida
│
├── database/
│   ├── repository.py        # Repositório unificado Supabase + SQLite
│   └── schema.sql           # DDL das tabelas
│
├── discord/
│   ├── formatters.py        # Formatador de cards ANSI e blocos YAML
│   └── dispatcher.py        # Despachante assíncrono com rate-limiting
│
├── web/                     # Frontend SPA estático pronto para GitHub Pages
│   ├── index.html           # Dashboard com cards de duelos e tabela
│   ├── h2h.html             # Comparador Head-to-Head
│   ├── telemetry.html       # Visualizador dos 10 jogadores
│   ├── css/style.css        # Tema dark esportivo
│   └── js/                  # Controladores consumindo Supabase REST API
│
├── tests/                   # Suíte de testes unitários (100% de aprovação)
│
├── run_monitor.py           # Daemon principal 24/7
├── requirements.txt         # Dependências modernas
└── .env                     # Variáveis de ambiente com chaves reais
```

---

## 🚀 Como Executar

### 1. Instalar Dependências
```powershell
pip install -r requirements.txt
```

### 2. Rodar a Suíte de Testes
```powershell
pytest tests -v
```

### 3. Iniciar o Monitor Autônomo 24/7
```powershell
python run_monitor.py
```

### 4. Acessar o Dashboard Web
O frontend pode ser aberto diretamente no navegador ou hospedado no GitHub Pages:
- Abrir `web/index.html`
- Acessar Comparador H2H em `web/h2h.html`
- Inspecionar telemetria dos jogadores em `web/telemetry.html`
