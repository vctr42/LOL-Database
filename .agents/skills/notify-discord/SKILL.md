---
name: notify-discord
description: Gerencia, configura e testa os webhooks e canais temáticos do Discord por Liga (CBLOL, LCK, LPL, LEC, LCS, Worlds, MSI) no LOL-Database. Use sempre que o usuário quiser configurar um novo canal/webhook no Discord, testar o disparo de dossiês em tempo real, ou ajustar o formato visual dos relatórios em YAML.
---

# Notify Discord Skill

Gerencia o envio inteligente de relatórios e dossiês de liquidação de apostas no Discord para o **LOL-Database**.

## Como Usar

### 1. Testar Disparo de um Canal
Execute o script utilitário passando a URL do Webhook ou a liga desejada:
```bash
python scripts/test_discord_webhook.py "URL_DO_WEBHOOK" "cblol"
```

### 2. Mapeamento de Canais e Bots por Liga
Os canais temáticos e cores dos bots estão configurados em [`config/league_channels.json`](file:///c:/Users/victo/OneDrive/Desktop/LOL-Database/config/league_channels.json):
- `#cblol` -> `DISCORD_WEBHOOK_CBLOL`
- `#lck` -> `DISCORD_WEBHOOK_LCK`
- `#lpl` -> `DISCORD_WEBHOOK_LPL`
- `#lec` -> `DISCORD_WEBHOOK_LEC`
- `#lcs` -> `DISCORD_WEBHOOK_LCS`
- `#worlds` -> `DISCORD_WEBHOOK_WORLDS`
- `#msi` -> `DISCORD_WEBHOOK_MSI`
- Canal Geral -> `DISCORD_WEBHOOK_DEFAULT`

### 3. Formato do Relatório
O relatório é gerado pelo [`discord/embeds.py`](file:///c:/Users/victo/OneDrive/Desktop/LOL-Database/discord/embeds.py) em bloco de código ````yaml```` monospaçado e limpo.
