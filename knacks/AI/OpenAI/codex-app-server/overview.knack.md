# Codex App Server

Load this knack when a local product needs a deep, structured Codex
integration: authentication state, conversation history, approvals, streamed
agent events, or another capability that cannot be represented by a bounded
one-shot command.

Source review: 2026-07-23.

## Choose the Surface Deliberately

`codex app-server` is the protocol service used by rich Codex clients. It is
not the OpenAI Platform API, an MCP server, or a general public remote API.
Starting it does not remove Codex authentication, billing, sandbox, approval,
or workspace-policy boundaries.

Use the smallest suitable surface:

- For a human terminal session, use the Codex CLI.
- For a bounded non-interactive command, use the documented non-interactive
  interface.
- For ordinary application jobs or CI automation, prefer the Codex SDK or the
  supported CI integration.
- For a client that must participate in Codex's bidirectional lifecycle, use
  app-server.

The protocol can change with the Codex release, and some transports, methods,
and fields are explicitly experimental. Treat the installed Codex version as
part of the client compatibility contract.

## Protocol Mental Model

App-server is a long-running, bidirectional service. A client sends requests
and notifications, receives responses and streamed notifications, and may
also receive requests that the client must answer. Approval prompts are the
most important example of that last category.

The messages follow JSON-RPC 2.0 discipline, although the
`"jsonrpc": "2.0"` member is omitted on the wire:

- requests carry a stable `id`, a `method`, and explicit `params`;
- responses match the request `id` and contain either `result` or `error`;
- notifications omit `id`; and
- server-initiated requests contain both a method and an `id`.

Do not assume stdout is an ordinary log stream. On the default transport,
each stdout line is one protocol message. Capture stderr separately for
diagnostics and bound how much of it is retained.

## Connection Lifecycle

Every connection has its own initialization state:

1. Open the selected transport.
2. Send exactly one `initialize` request with accurate client identity and
   only the capabilities the client implements.
3. Check the response, then send the `initialized` notification.
4. Only then invoke account, thread, turn, or other methods.
5. Continue reading while a request or turn is active; progress and completion
   arrive as notifications.
6. Close input and terminate the owned process or connection cleanly when the
   client is finished.

Requests sent before initialization fail. Repeating `initialize` on the same
connection also fails. A reconnect is a new protocol connection and must
initialize again.

Thread, turn, and item are the core conversation concepts. Do not infer that
a successful request response means a turn is complete; follow the documented
notifications through the terminal state.

## Bind to the Installed Version

Do not reproduce the full app-server schema in a maintained prose document or
hand-written collection of loose types. Generate bindings or JSON Schema from
the exact Codex executable the client will launch:

```text
codex app-server generate-json-schema --out ./schemas
codex app-server generate-ts --out ./schemas
```

Generated output is specific to that Codex version. Pin or inventory the
Codex release alongside the generated schema, review schema changes during an
upgrade, and test both expected methods and rejected unknown fields.
Experimental methods and fields require explicit capability opt-in; do not
enable that capability simply to make a schema error disappear.

## Transport Choice

The supported transport shapes have different exposure:

- **stdio** is the default. It uses newline-delimited JSON and naturally keeps
  the service bound to the child process. Prefer it for one local client.
- **WebSocket** uses one protocol message per text frame. It remains an
  experimental, unsupported transport. Restrict plain WebSockets to loopback
  or a protected tunnel; use authentication and TLS termination for a
  deliberately remote connection.
- **Unix socket** carries a WebSocket handshake over the default or an
  explicitly selected local socket. Protect the containing directory and
  socket for the intended user or group.
- **off** disables the local listener.

A listener is a control surface. Never bind it to a shared or public network
merely for convenience. Transport authentication protects client-to-server
access; it is separate from the credential app-server uses for Codex service
requests.

## Safe Client Pattern

A production-quality client should:

- resolve and record the exact executable and version it started;
- use a dedicated child process or explicitly authenticated connection;
- retain request IDs until their responses arrive;
- continue servicing server requests while awaiting another response;
- reject unknown or unsupported server requests with a protocol error;
- default approval decisions to denial unless current user intent and policy
  authorize the exact action;
- bound message size, queues, startup time, request time, total runtime, and
  retained output;
- terminate the complete owned process tree on timeout using the platform's
  process-group, job, or equivalent lifecycle mechanism;
- distinguish protocol errors from transient transport or service failures;
- use exponential backoff with jitter only for plausibly transient failures;
- redact secrets and identifiers before persistence; and
- preserve enough method, ID, timing, error-code, and field-shape evidence to
  diagnose a compatibility failure.

Do not blindly retry malformed JSON, invalid methods, rejected capabilities,
schema mismatches, or denied approvals. Those are client or policy results,
not congestion.

## Authentication and Billing Boundaries

Codex can expose several account modes, including ChatGPT-backed, API-key,
externally managed token, agent identity, personal access token, and provider
specific modes. Method availability differs by mode and can expand over time.
Read the effective account state instead of guessing it from environment
variables or the way app-server was launched.

The transport does not determine billing. A local stdio connection can still
drive authenticated remote model work. Conversely, reading local inventory
does not itself prove a model turn occurred. Before starting turns or
presenting usage data:

- identify the active auth mode through the documented account surface;
- apply the organization's current billing and data-handling policy for that
  mode;
- keep access and refresh tokens out of arguments, logs, artifacts, and
  source control; and
- represent unsupported or unavailable account data as unknown, not zero.

## Review Checklist

- Is app-server necessary, or would the CLI, SDK, or CI integration be
  smaller?
- Is the client bound to schemas generated by its selected Codex version?
- Does every connection complete `initialize` and `initialized` first?
- Can the client handle notifications and server-initiated requests while a
  request is pending?
- Do approval requests fail closed?
- Are transports restricted, authenticated, and encrypted in proportion to
  their exposure?
- Are process lifetime, queues, output, retries, and retained diagnostics
  bounded?
- Are auth mode, billing policy, and telemetry availability explicit?

## Further Information

- OpenAI, Codex App Server:
  <https://learn.chatgpt.com/docs/app-server>
- OpenAI, Codex SDK:
  <https://learn.chatgpt.com/docs/codex-sdk>
- OpenAI, Codex authentication:
  <https://learn.chatgpt.com/docs/auth>
- OpenAI, Codex developer commands:
  <https://learn.chatgpt.com/docs/developer-commands>
- JSON-RPC 2.0 specification:
  <https://www.jsonrpc.org/specification>
- Model Context Protocol specification:
  <https://modelcontextprotocol.io/specification/>
