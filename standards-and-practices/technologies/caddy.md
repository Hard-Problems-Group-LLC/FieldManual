# Caddy

## Use When

Use Caddy when a project needs an HTTP reverse proxy, TLS termination, or
static-file service with reviewable configuration. Keep application and
network-exposure decisions separate from proxy convenience.

## Project-Declared Version Policy

Declare the supported Caddy release or container image and any required
modules. Pin immutable image identifiers where reproducible deployment is
required.

## Configuration Baseline

- Keep the Caddy configuration small, reviewable, and reproducible.
- Make upstream addresses, public listeners, redirects, and trust boundaries
  explicit.
- Keep certificates and private keys outside application images.
- Mount sensitive material read-only when practical.
- Record whether TLS is automated, externally supplied, or issued by a
  private network authority.

## Security and Operations

Bind only the interfaces and ports the service is meant to expose. Preserve
the original client address only through explicitly trusted proxies. Apply
least privilege to the proxy process and its configuration, certificate, and
log paths.

Provide first-class access to proxy health, configuration errors, request
logs, and upstream failures. Avoid logging credentials or sensitive query
content.

## Validation

- Validate configuration before replacing a running instance.
- Verify routing, headers, redirects, and upstream failure behavior.
- Inspect the certificate, hostname, chain, and expiry served on each intended
  TLS endpoint.
- Test exposure from the networks that should and should not have access.

Exact commands and automation are project-owned. FieldManual ships no Caddy
verifier.

## Failure Handling and Rollback

Keep a known-good configuration available and make replacement atomic. A
failed validation must not displace a working configuration. Distinguish
proxy, certificate, DNS, firewall, and upstream failures during diagnosis.

## Maintenance Risks

- Accidentally broad listeners.
- Drift between mounted certificate paths and configuration.
- Trusting forwarded headers from untrusted clients.
- Reloading invalid configuration without a rollback path.

## Related Guidance

- [Podman](podman.md)
- [Tailscale](tailscale.md)
