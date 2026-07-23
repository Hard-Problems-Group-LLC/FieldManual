# Tailscale

## Use When

Use Tailscale when a service or administrative path should be reachable
through an authenticated private network rather than public ingress. It is
not a substitute for application authorization, least privilege, or a
documented public-exposure decision.

## Project-Declared Version Policy

Declare the supported client and service features required by the project.
Record tailnet dependencies such as DNS, HTTPS certificate support, ACLs,
grants, tags, and service exposure.

## Configuration Baseline

- Discover assigned addresses and DNS names from authoritative Tailscale
  status rather than hardcoding transient values.
- Keep ACL, grant, and tag ownership reviewable through the organization's
  approved configuration process.
- Distinguish direct node access from access published through Tailscale
  Serve or another proxy.
- Keep application listeners private unless broader host exposure is
  deliberate.
- Record certificate issuance and renewal ownership when using tailnet HTTPS.

## Security and Operations

Use least-privilege network policy and fail closed when identity, certificate,
or policy prerequisites are unavailable. Do not assume membership in the
tailnet grants application-level permission.

Observe backend state, assigned addresses, DNS identity, relay versus direct
connectivity, published services, certificate expiry, and application health.

## Validation

- Confirm the node has the intended identity, address, tags, and policy.
- Verify allowed and denied access from representative clients.
- Test direct and proxied paths separately when both exist.
- Inspect the certificate and hostname served on HTTPS endpoints.
- Diagnose DNS, relay, firewall, MTU, proxy, and application health as
  separate layers.

Exact commands and automation are project-owned. FieldManual ships no
Tailscale verifier.

## Failure Handling and Rollback

Remove or disable unintended exposure before attempting a broad repair. Keep
the previous proxy or Serve configuration available for review, and restore
only a known-good state. Certificate failure should not fall back to
unexpected public or plaintext exposure.

## Maintenance Risks

- Overbroad ACLs or reusable tags.
- Hardcoded node names or addresses.
- Relay, firewall, or MTU drift mistaken for application failure.
- Certificate renewal ownership left implicit.

## Related Guidance

- [Caddy](caddy.md)
- [Podman](podman.md)
