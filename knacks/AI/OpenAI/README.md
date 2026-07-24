# OpenAI Knacks

Load these documents only when the task uses the named OpenAI product surface.
Do not transfer behavior between the OpenAI Platform API, ChatGPT, Codex, MCP,
and local Codex control protocols merely because they share an authentication
provider.

## Codex App Server

- [Overview](codex-app-server.knack/codex-app-server.overview.knack.md) —
  surface selection, protocol lifecycle, transports, and safe client design
- [Account Telemetry API](codex-app-server.knack/codex-app-server.api.account-telemetry.knack.md) —
  account, rate-limit, and usage diagnostics

The Codex app-server protocol is version-sensitive. Recheck the official
documentation and generate schemas from the installed Codex version before
implementing or updating a client.
