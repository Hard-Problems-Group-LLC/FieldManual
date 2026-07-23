# Podman

## Use When

Use Podman when a project needs OCI container build and runtime behavior,
especially where rootless operation is available. Do not use containers to
hide undocumented host, storage, network, or privilege assumptions.

## Project-Declared Version Policy

Declare the supported Podman and OCI image-format baseline for the target
hosts and continuous-integration environment. Pin base images or immutable
digests when reproducibility and supply-chain review require them.

## Configuration Baseline

- Keep build files and runtime options in version control.
- Make environment variables, ports, networks, mounts, and health behavior
  explicit.
- Prefer rootless containers and a non-root user inside the image.
- Use an intentional user-namespace mapping when host file ownership matters.
- Keep persistent data in declared volumes or host paths, not writable image
  layers.
- Account for SELinux and other host labeling requirements on mounted paths.

## Security and Operations

Grant only required devices, capabilities, mounts, and network exposure.
Never pass secrets through image layers or committed environment files.
Separate build-time trust from runtime credentials.

Provide documented ways to inspect status, health, logs, configuration, and
the running container without reconstructing commands from shell history.

## Validation

- Build from a clean context and review what enters the image.
- Run with production-representative users, mounts, networks, and environment.
- Exercise health checks and application smoke tests against the running
  container.
- Verify stop, restart, replacement, and host-reboot behavior.
- Scan and update base images according to project policy.

Exact commands and automation are project-owned. FieldManual ships no Podman
verifier.

## Failure Handling and Rollback

Preserve named volumes and mounted data unless destructive replacement is
explicitly authorized. Keep the previously deployable image available long
enough to support rollback. Distinguish image, runtime, permission, port, and
application failures.

## Maintenance Risks

- Rootless ownership and SELinux labeling failures.
- Floating base images changing clean builds.
- Stale containers masking current startup failures.
- Cleanup commands that remove persistent data.

## Related Guidance

- [Caddy](caddy.md)
- [PostgreSQL](postgresql.md)
