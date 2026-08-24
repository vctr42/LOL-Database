---
name: skill-manager
description: Cria novas skills do projeto no formato Agent Skills (SKILL.md) e organiza a biblioteca de skills existente — evita descriptions sobrepostas, aplica convenção de nomenclatura e mantém um índice atualizado. Use sempre que o usuário pedir para criar uma skill nova, transformar um workflow repetido em skill, revisar/organizar as skills do projeto, checar se duas skills estão competindo pelo mesmo gatilho, ou listar o que já existe em .agents/skills/.
---

# Skill Manager

Meta-skill para criar e manter organizada a biblioteca de skills deste projeto (`.agents/skills/`). Tem duas frentes: **criar** skills novas corretamente, e **organizar/ordenar** as que já existem.

## Como as skills funcionam no Antigravity (contexto rápido)

- Cada skill é uma pasta em `.agents/skills/<nome-da-skill>/` com um `SKILL.md` obrigatório.
- O `SKILL.md` tem um frontmatter YAML (`name` e `description`) seguido de instruções em markdown.
- No início da conversa, o agente só vê `name` + `description` de cada skill (carregamento leve). Só quando uma tarefa parece bater com a `description`, o agente lê o corpo inteiro do `SKILL.md`.
- Por isso, **a `description` é o mecanismo de gatilho**: se ela for vaga ou genérica demais, a skill nunca vai ser usada — ou vai disparar errado, competindo com outra.

## Parte 1 — Criando uma skill nova

Quando o usuário pedir uma skill nova (ou você perceber, na conversa, um workflow repetitivo que merece virar uma):

1. **Entreviste rapidamente** (pule perguntas cuja resposta já esteja óbvia pelo contexto):
   - O que a skill deve fazer, exatamente?
   - Quando ela deve disparar? Que frases/situações do usuário indicam isso?
   - Qual o formato de entrada/saída esperado?
   - Existe algum script, template ou exemplo que já usamos na conversa e que dá pra reaproveitar?

2. **Escolha um nome em kebab-case**, curto e específico (ex: `deploy-staging`, `gerar-relatorio-semanal`), evitando nomes genéricos como `helper` ou `utils`.

3. **Antes de escrever, rode a checagem de sobreposição** (ver Parte 2 → "Checar sobreposição") pra garantir que a description da skill nova não vai competir com uma já existente.

4. **Escreva a description seguindo estas regras:**
   - Terceira pessoa, direto ao ponto.
   - Inclua O QUE a skill faz E QUANDO usar — gatilhos explícitos, com frases realistas que o usuário digitaria.
   - Erre para o lado de ser "insistente" (pushy): é mais comum uma skill nunca disparar por description tímida do que disparar demais. Ex.: em vez de "Formata mensagens de commit", prefira "Formata mensagens de commit seguindo Conventional Commits. Use sempre que o usuário for commitar, pedir revisão de mensagem de commit, ou mencionar git commit."

5. **Escreva o corpo do `SKILL.md`** com o passo a passo. Mantenha abaixo de ~500 linhas — se estiver passando disso, quebre o conteúdo extra em `references/algum-topico.md` e aponte pra lá dentro do corpo principal.

6. **Estruture a pasta** conforme necessário:
   ```
   .agents/skills/<nome-da-skill>/
   ├── SKILL.md          (obrigatório)
   ├── scripts/           (scripts que a skill executa)
   ├── references/         (documentação extra, carregada só quando precisa)
   └── resources/          (templates, assets usados na saída)
   ```
   Use `resources/template-skill.md` (desta skill) como ponto de partida.

7. **Salve em** `.agents/skills/<nome-da-skill>/SKILL.md` (escopo do projeto — não vaza pros outros projetos). Só use o escopo global (`~/.gemini/config/skills/`) se for algo útil em qualquer projeto, não só nesse.

8. **Atualize o índice** (`.agents/skills/INDEX.md`) com a skill nova — ver Parte 2.

9. **Teste**: abra uma conversa nova e digite uma frase natural que deveria disparar a skill. Se não disparar, a `description` provavelmente precisa ficar mais específica/pushy.

## Parte 2 — Organizando e ordenando as skills existentes

### Manter o índice

Mantenha um arquivo `.agents/skills/INDEX.md` (use `resources/indice-template.md` como base) listando, pra cada skill: nome, categoria, resumo em uma linha e a description completa. Isso dá visão geral sem precisar abrir pasta por pasta.

Sempre que criar, editar ou remover uma skill, atualize esse índice no mesmo passo — ele é a fonte de verdade da organização do projeto.

### Convenção de nomenclatura por categoria

Prefixe o nome da skill pela categoria, pra ficar fácil escanear `.agents/skills/` visualmente e evitar colisão conceitual. Sugestão de ponto de partida (adapte ao projeto):

- `test-*` → testes e validação
- `deploy-*` → deploy e infraestrutura
- `data-*` → manipulação/análise de dados
- `docs-*` → documentação e relatórios

### Checar sobreposição

Antes de criar uma skill nova, ou periodicamente para auditoria:

1. Rode `python3 scripts/listar_skills.py` a partir da raiz do projeto — ele varre `.agents/skills/`, extrai nome + description de cada `SKILL.md`, e sinaliza pares com alta similaridade de palavras-chave na description.
2. Se aparecer sobreposição:
   - Se as duas skills fazem essencialmente a mesma coisa → sugira consolidar em uma só.
   - Se fazem coisas diferentes mas o gatilho é parecido → reescreva as descriptions pra deixá-las mutuamente exclusivas (ex: uma foca em "gerar", a outra em "revisar").

### Podar skills obsoletas

De tempos em tempos (ou quando o usuário pedir pra "organizar as skills"), pergunte se alguma skill do índice não é mais usada. Toda skill soma na lista que o agente vê no início de cada conversa — skills mortas só poluem esse contexto. Sugira arquivar (mover pra `.agents/skills/_arquivadas/`) em vez de deletar direto, caso o usuário queira recuperar depois.

## Checklist rápido

- [ ] Nome em kebab-case, com prefixo de categoria
- [ ] Description em 3ª pessoa, com gatilhos explícitos e um pouco "pushy"
- [ ] Corpo com passo a passo claro, abaixo de ~500 linhas
- [ ] Sem sobreposição significativa com skills existentes (rodei `listar_skills.py`)
- [ ] Índice (`INDEX.md`) atualizado
- [ ] Testado com uma frase natural em conversa nova
