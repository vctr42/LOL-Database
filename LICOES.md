# 🧭 LIÇÕES APRENDIDAS & GUIA CONCEITUAL PARA O REBUILD
> **Projeto:** Motor de Liquidação de Apostas, Telemetria Oficial & Data Lake de Esports  
> **Data de Consolidação:** Agosto de 2026  
> **Propósito:** Documento de referência conceitual definitiva para reconstruir o sistema do zero em um workspace limpo, preservando todo o conhecimento acumulado e evitando armadilhas passadas.

---

## 1. 🎯 OBJETIVO (Visão Madura e Definitiva)

O projeto **NÃO** é uma calculadora de probabilidades em tempo real complexa, nem um terminal de trading poluído de gráficos.

### A Visão Madura:
> **Um Sistema Autônomo 24/7 de Telemetria Oficial, Auditoria Rigorosa de Liquidação de Apostas e Data Lake Estatístico de League of Legends Profissional.**

O sistema tem três papéis fundamentais:
1. **Auditoria & Liquidação Imediata:** Monitorar ininterruptamente todas as ligas mundiais (CBLOL, LCK, LPL, LEC, LCS, etc.) e, no segundo em que o Nexus for destruído, compilar e auditar um **Dossiê de Liquidação de Apostas** cirúrgico, sem margem para dúvidas.
2. **Roteamento Segmentado:** Entregar o dossiê automaticamente no Discord, direcionado para o canal e bot temático exclusivo de cada liga.
3. **Data Lake Persistente:** Armazenar 100% dos dados coletivos e individuais dos 10 jogadores de cada mapa em um banco de dados estruturado na nuvem, servindo como base histórica para análises de confronto direto (H2H) e tendências estatísticas pré-jogo.

---

## 2. 📋 REQUISITOS ESSENCIAIS (O que o Rebuild DEVE ter)

1. **Duração Baseada Estritamente no In-Game Clock Oficial:**
   * A duração do jogo deve ser **exclusivamente o cronômetro do servidor da Riot** (de `00:00` quando os campeões nascem até a destruição do Nexus).
   * O cálculo deve ser imune a pausas técnicas no palco, *chronobreaks* e atrasos de transmissão de vídeo da live (*broadcast delay*).
2. **Política de Confiança Zero (*Zero-Doubt Verification Gate*):**
   * Se houver qualquer divergência de abates, ouro zerado, vencedor incerto ou partida incompleta, o envio deve ser **bloqueado**. Antes não enviar nada do que enviar um dado incorreto para a planilha do apostador.
3. **Identificação Explícita do Mapa na Série:**
   * Todo título de relatório deve conter a liga, os times e o número exato do mapa (`[LCS] SEN vs FLY — MAPA 1`).
4. **Mercados de Apostas Padronizados para o Apostador:**
   * **Moneyline:** Vencedor oficial do mapa e lado do mapa (Azul / Vermelho).
   * **Kills & Handicap Fracionário:** Saldo real de abates e linhas fracionárias exatas de GREEN (`.5`), identificando a margem do favorito (`-`) e do azarão (`+`).
   * **Totais de Objetivos:** Torres, Dragões, Barões, Arautos e Inibidores de forma compacta e direta.
   * **Firsts & Corridas de Abates:** `First Tower`, `First Dragon`, `First Herald`, `First Baron`, `First Blood`, `Corrida 5 Kills`, `Corrida 10 Kills` e `Corrida 15 Kills`.
5. **Roteamento Multi-Canais por Liga no Discord:**
   * Cada liga com seu próprio canal (`#cblol`, `#lck`, etc.) e identidade visual (avatar/nome do bot correspondente).
6. **Banco de Dados Universal (Nuvem + Local):**
   * Persistência de metadados, placares, 10 jogadores individuais (KDA, CS, Gold, Dano, KP%, Itens, Runas) e eventos temporais.
   * Compatível com **PostgreSQL em Nuvem (Supabase/Neon)** para produção e **SQLite** para testes locais.
7. **Execução Autônoma 24/7 sem Dependência de Computador Ligado:**
   * Arquitetura pronta para deploy em nuvem (Serverless / Scheduled Cron Functions no Netlify ou container Docker contínuo).
8. **Política Incontestável de Dados 100% Reais & Zero Mocks/Fictícios:**
   * É terminantemente proibido exibir ou manter qualquer dado simulado, fictício ou de demonstração no frontend ou na API. Toda e qualquer informação deve ser 100% real, auditada e originada diretamente da telemetria da Riot Games. Se não houver dados, o sistema deve apresentar estado vazio limpo e transparente.

---

## 3. 💎 O QUE MANTER (Decisões e Abordagens Validadas)

* **Feed Oficial da Riot Games como Fonte Primária e Soberana:**
  * Os endpoints de `details` e `window` da Riot Games são **gratuitos, ilimitados, sem limites de requisição e contêm o dado oficial bruto** utilizado pelas próprias casas de aposta.
* **Layout Monospaçado em Blocos YAML no Discord:**
  * O uso de codeblocks ````yaml```` entrega o alinhamento visual perfeito entre colunas, números e rótulos em qualquer dispositivo (celular e desktop).
* **Sintaxe Harmonizada de Chaves (Uniformidade Visual):**
  * Nomes de chaves limpos sem parênteses (ex: `First Blood:`, `First Tower:`) garantem que o parser de sintaxe do Discord pinte todos os rótulos de **azul** e todos os valores de **verde/laranja**, sem quebras de cor aleatórias.
* **Armazenamento de Telemetria de Jogadores Individuais:**
  * Guardar dano aos campeões, participação em abates e itens de todos os 10 jogadores cria um ativo de dados valioso para criar modelos de previsão futuros.
* **Conexão Direta via MCP (Model Context Protocol):**
  * Utilizar conectores MCP para provisionar projetos, gerenciar variáveis de ambiente e auditar status de deploys em nuvem elimina tarefas manuais repetitivas.

---

## 4. ⚠️ O QUE EVITAR (Erros, Becos sem Saída e Armadilhas)

Esta é a seção mais crítica para o sucesso do rebuild.

### ❌ 1. Estimativas e Heurísticas por Ouro para Calcular Tempo
* **O Erro:** Tentar adivinhar a duração da partida dividindo o ouro acumulado das equipes por uma constante média.
* **Por que falhou:** Partidas lentas/passivas e partidas extremamente agressivas acumulam ouro em taxas completamente distintas. Essa estimativa gerou distorções absurdas de **2 a 4 minutos** de erro em relação ao cronômetro real.
* **A Solução:** Usar exclusivamente a diferença temporal entre o timestamp de inicialização oficial (`00:00` no frame inicial) e o frame de destruição do Nexus.

### ❌ 2. Dependência de APIs Terceiras com Limites Rígidos (Cotas Gratuitas)
* **O Erro:** Apoiar a arquitetura primária em APIs comerciais que limitam requisições (ex: 500 requisições/mês).
* **Por que falhou:** Em menos de 2 horas de monitoramento contínuo, a cota estoura e o sistema para de funcionar no meio de uma rodada importante.
* **A Solução:** Ingestão direta na CDN da Riot Games, que é aberta e ilimitada.

### ❌ 3. Medição de Tempo pelo Relógio de Parede Bruto (UTC Simples)
* **O Erro:** Fazer a subtração simples entre a criação da sala e a desconexão do socket.
* **Por que falhou:** Se uma partida tiver 15 minutos de pausa técnica por problema no palco, o relógio UTC continua correndo, mas o jogo fica congelado. O tempo calculado dava 15 minutos a mais do que o resultado oficial que a casa de aposta considerou.
* **A Solução:** Capturar apenas os ticks do motor de jogo que representam tempo efetivo de jogo.

### ❌ 4. Mistura de Conceitos de Trading em Tempo Real com Liquidação Pós-Jogo
* **O Erro:** Tentar construir no mesmo script uma interface de streaming com latência de milissegundos para apostar durante a partida e um bot de geração de relatório pós-jogo.
* **Por que falhou:** Criou um monólito inchado, difícil de debugar, cheio de websockets complexos e threads concorrentes desnecessárias para quem só precisa da liquidação do resultado.
* **A Solução:** Desacoplar completamente. O motor de liquidação e auditoria deve ser um serviço independente, focado em precisão e persistência.

### ❌ 5. Acoplamento de Banco de Dados Exclusivamente Local em Arquitetura Serverless
* **O Erro:** Gravar dados em arquivo SQLite local dentro de uma plataforma *serverless* (como Netlify Functions).
* **Por que falhou:** Ambientes *serverless* são efêmeros (*stateless*). O arquivo em disco é descartado após a execução da função, perdendo o histórico.
* **A Solução:** Arquitetura preparada desde o primeiro dia para receber uma string `DATABASE_URL` conectada a um PostgreSQL em nuvem (Supabase ou Neon), mantendo SQLite apenas como alternativa de desenvolvimento local.

### ❌ 6. Poluição Textual nos Cards de Aposta
* **O Erro:** Incluir textos como `(OVER / UNDER)`, `(O/U)` ou cálculos complexos de EV dentro do relatório de liquidação.
* **Por que falhou:** Dificulta a leitura rápida do apostador que só quer bater o olho e marcar Green/Red na planilha.
* **A Solução:** Mostrar apenas os números brutos e a linha fracionária de Green direta (`SEN até -15.5 | FLY a partir de +16.5`).

---

## 5. 🔍 O QUE MOTIVOU O REFAZER (Diagnóstico Honesto)

1. **Crescimento Orgânico sem Arquitetura Inicial (Débito Técnico):**
   * O projeto começou como um script simples de monitoramento, evoluiu para um terminal com odds, depois adicionou bots de Telegram e Discord, e finalmente virou um motor de liquidação. Essa sobreposição de ideias gerou arquivos mortos, scripts duplicados (`.bat`, `.vbs`), múltiplos bancos SQLite e portas concorrentes.
2. **Complexidade Excessiva para uma Necessidade Clara:**
   * Havia centenas de linhas de código dedicadas a features secundárias (gráficos de ouro, estimativas de probabilidade de vitória em tempo real) que não eram utilizadas no fluxo real de trabalho do apostador.
3. **Mudança para Paradigma Cloud 24/7:**
   * A necessidade de rodar 24/7 sem depender de um computador Windows local exige uma base de código limpa, desacoplada, pronta para rodar em serverless ou container, com configuração limpa via variáveis de ambiente.

---

## 📐 Estrutura Ideal Recomendada para o Novo Workspace

```
live-bet-core/
├── netlify.toml              # Orquestração Serverless & Cron 24/7
├── requirements.txt          # Dependências mínimas essenciais
├── .env.example              # Modelo limpo de variáveis de ambiente
├── README.md                 # Documentação e instruções de deploy
│
├── config/
│   ├── settings.py           # Leitura centralizada de variáveis
│   └── league_channels.json  # Mapeamento de Webhooks por Liga
│
├── core/
│   ├── riot_feed.py          # Cliente de telemetria direta da Riot
│   ├── audit_gate.py         # Zero-Doubt Verification Gate
│   ├── settlement.py         # Compilador do Dossiê de Liquidação
│   └── database.py           # Persistência Cloud Postgres / SQLite
│
├── discord/
│   ├── router.py             # Despacho inteligente por canal da Liga
│   └── embeds.py             # Construtor dos blocos visuais em YAML
│
├── analytics/
│   └── h2h_engine.py         # Consultas H2H e estatísticas históricas
│
├── public/                   # Dashboard Web estático e responsivo
│   ├── index.html            # Histórico de liquidação
│   ├── h2h.html              # Comparador direto de times
│   ├── app.js
│   └── styles.css
│
└── netlify/functions/
    └── scan_matches.js       # Função agendada para monitoramento contínuo
```

---

> 💡 **Regra de Ouro para o Novo Projeto:**  
> *"Mantenha o código enxuto, priorize a fidelidade absoluta dos dados sobre a velocidade de entrega, e construa cada módulo como um bloco independente e testável."*
