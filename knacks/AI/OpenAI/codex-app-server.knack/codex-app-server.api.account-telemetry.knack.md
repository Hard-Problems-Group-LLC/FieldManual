# Codex App-Server Account Telemetry

Load this API companion when a client needs to inspect Codex authentication,
ChatGPT rate-limit state, or ChatGPT token-activity summaries without scraping
the interactive terminal UI.

Source review: 2026-07-23. Read the
[app-server overview](codex-app-server.overview.knack.md) first.

## Scope and Safety

Account telemetry is a diagnostic surface. A narrow telemetry client should
initialize a connection, read only the required account methods, normalize a
small result, and close. It should not start a thread or turn, change login
state, consume credits, send email, modify Codex configuration, or make an
approval decision.

Do not encode the complete response schema in this document. Generate the
schema from the installed Codex version and treat every response member as
version-sensitive unless the generated binding proves otherwise.

## Read the Account State First

Use `account/read` to determine whether authentication is required and which
account type is active. Request token refresh only when the product's
documented workflow and credential owner authorize it.

Normalize only the facts the caller needs, such as:

- whether an account is present;
- whether OpenAI authentication is required;
- account or auth mode;
- plan type when supplied; and
- whether the desired telemetry method is supported.

Account IDs, workspace IDs, email addresses, token material, and opaque
credentials are not display fields. Do not retain them merely because they
appear in a response.

## Rate-Limit Snapshot

`account/rateLimits/read` fetches ChatGPT-backed Codex rate-limit state. A
current response can include:

- `rateLimits`, a backward-compatible single-bucket view;
- `rateLimitsByLimitId`, a multi-bucket map keyed by metered limit ID;
- primary and secondary windows for a bucket;
- `usedPercent`, `windowDurationMins`, and `resetsAt` for a window;
- an optional user-facing limit name and plan type;
- workspace credit details when available;
- a server-classified reached-limit state; and
- earned rate-limit-reset credit counts or detail rows.

Prefer the multi-bucket view when present, but accept the compatible
single-bucket view. Preserve every returned bucket and window in the
normalized result. `usedPercent` is consumption, not remaining capacity, and
`resetsAt` is a Unix timestamp in seconds.

If a UI needs one pressure indicator, select the highest consumed active
window and keep its reset time attached to that same window. Do not combine
the percentage from one bucket with the reset time from another. A per-window
table is clearer whenever more than one limit affects the operator.

App-server may also send `account/rateLimits/updated`. A retained client can
use that notification to invalidate a cached snapshot, but it should still
handle reconnects and a full read.

## Token-Activity Summary

`account/usage/read` fetches ChatGPT account token-activity summaries and
optional daily buckets. Current fields can include lifetime and peak-daily
token counts, turn-duration information, streak information, and dated token
buckets.

These values may be null or absent. The method requires authentication backed
by Codex services; API-key-only and Amazon Bedrock authentication do not
provide this ChatGPT usage view. Unsupported authentication means
“unavailable for this account mode,” not “no usage.”

Rate limits and token activity answer different questions. Do not present a
token summary as billing, remaining quota, or a substitute for the
rate-limit snapshot.

## Reset Credits Are Not Telemetry

The rate-limit response may describe earned reset credits. Reading that
description is diagnostic. Calling
`account/rateLimitResetCredit/consume` changes account state.

Keep reset consumption out of a read-only collector. If a product offers it,
use a separate, explicitly authorized action with:

- a user-visible description of the affected limit;
- an idempotency key scoped to one logical attempt;
- confirmation of the returned outcome;
- a fresh `account/rateLimits/read` afterward; and
- an audit record that does not expose the opaque credit identifier.

Likewise, methods that send a credit or usage-limit notification email are
mutating account actions and do not belong in background telemetry polling.

## Normalized Diagnostic Shape

A stable project-owned result can remain small even when the upstream schema
grows. Useful fields include:

- local schema version;
- capture timestamp and duration;
- Codex executable version;
- data source and method names;
- auth mode and optional plan type;
- availability and staleness;
- normalized bucket and window rows;
- normalized token-activity values when requested;
- warnings and a bounded last-error category; and
- redaction counts.

If raw evidence must be retained for a parser failure, encrypt or
access-restrict it, apply recursive key and value redaction, bound its size and
lifetime, and keep it separate from ordinary UI responses.

## Caching and Failure Semantics

Polling should be slower than a UI refresh heartbeat. Cache one snapshot for a
documented short interval, allow an update notification to invalidate it, and
ensure concurrent readers do not each start another app-server process.

On failure:

- distinguish missing or incompatible Codex from authentication, transport,
  timeout, protocol, and service failures;
- retain the last successful value only when it is prominently marked stale;
- use a bounded deadline for startup and the complete probe;
- retry only failures likely to be transient, with capped backoff and jitter;
- never turn missing fields, unsupported auth, or an error into zero usage;
  and
- keep unrelated product work independent of telemetry availability.

An inventory-only mode that verifies the selected executable and version
without starting app-server is useful for diagnosing environment selection.
It is not a successful account probe.

## Redaction Boundary

Apply an allowlist to normalized output and defense-in-depth redaction to any
retained raw diagnostic. At minimum, treat these as sensitive:

- access, refresh, ID, bearer, OAuth, and session tokens;
- API keys, authorization headers, cookies, and passwords;
- account, workspace, organization, and session identifiers;
- email addresses; and
- new opaque high-entropy strings not recognized by an older parser.

Preserve safe structural evidence such as method name, request ID, error code,
field names, numeric limit values, timestamps, durations, executable version,
and the number of redactions.

## Validation Checklist

- The connection initializes before account methods run.
- No thread or turn is created.
- Active auth mode is inspected rather than inferred.
- Multi-bucket and primary/secondary windows remain distinct.
- Null, absent, unsupported, stale, and zero are represented differently.
- Reset-credit consumption and notification email are absent from the
  read-only path.
- Polling is cached and bounded.
- Unknown server requests are denied.
- Retained output is size-limited and redacted.
- A schema change fails visibly instead of silently dropping new meanings.

## Further Information

- OpenAI, Codex App Server, including account methods:
  <https://learn.chatgpt.com/docs/app-server>
- OpenAI, Codex authentication:
  <https://learn.chatgpt.com/docs/auth>
- OpenAI, Codex pricing:
  <https://learn.chatgpt.com/docs/pricing>
- OpenAI, Codex developer commands:
  <https://learn.chatgpt.com/docs/developer-commands>
- JSON-RPC 2.0 specification:
  <https://www.jsonrpc.org/specification>
