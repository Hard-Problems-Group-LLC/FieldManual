# Go Modules, Builds, and Security

## Purpose

Keep Go source, dependencies, tools, builds, and releases explicit,
reviewable, and reproducible. This document is the canonical FieldManual
guidance for Go project layout, module state, dependency security, build
inputs, compatibility, and release evidence.

## Repository and Module Layout

Start with the smallest layout that works. A simple package or command may
live at the module root.

- Default to one module rooted at the repository root.
- Add another module only for a real independent versioning, publication,
  dependency, or ownership boundary. Each module adds separate tags,
  upgrades, tests, vulnerability checks, and workspace behavior.
- Use `internal/` for packages that are not intentionally supported for
  external import.
- Use `cmd/<name>/` when a repository contains multiple commands or mixes
  commands with importable packages. Keep each `main` thin.
- Do not prescribe a top-level `pkg/` directory. It has no special Go
  semantics; an importable package should exist because it is a supported
  API.
- Keep package tests beside their packages and non-package fixtures under
  `testdata/`.
- Do not adopt a universal community project-layout skeleton without a
  project-specific need for each directory.

A `go.work` file is normally local multi-module development state. Do not
commit it by default: it can override a developer's workspace and cause CI to
test replacements instead of released module versions. A deliberately
committed workspace requires a documented tightly coupled multi-module
contract, and CI must still test every module independently.

## Module and Toolchain Declarations

- Initialize each module with its durable publication or repository import
  path.
- Commit `go.mod` and `go.sum`. Use Go module commands to maintain them and
  review every resulting diff.
- Treat the `go` directive as the minimum required version and a language and
  command-semantics choice.
- Treat the `toolchain` directive as a suggested main-module toolchain. Since
  automatic selection can download a newer toolchain, decide whether that is
  allowed in local development and CI.
- In minimum-version jobs, prevent automatic toolchain switching from masking
  incompatibility. Record the actual `go version` used by every release
  build.
- Keep `go mod tidy` clean. On a supporting toolchain, use its diff mode in
  CI; otherwise run tidy in a clean checkout and require no resulting change.
- Understand `go.sum` as authenticated module-content checksums, not a
  conventional lockfile and not a vulnerability report.
- Use `go mod verify` to detect changes to content already held in the module
  cache. It does not replace ordinary checksum authentication, source review,
  or vulnerability analysis.

For modules supporting Go 1.24 or later, `tool` directives are the preferred
standard mechanism for project tool dependencies. Earlier baselines need
another project-owned, versioned mechanism. Never let CI depend on an
unversioned `@latest` installation or an operator's ambient executable. See
[Tooling Installation and Maintenance](tooling-installation-and-maintenance.md)
for installation scope, dependency-graph effects, cache ownership, and
onboarding policy.

## Dependency Selection and Updates

Before adding or materially upgrading a dependency, review:

- whether its API solves the actual problem more clearly than the standard
  library or a small owned implementation;
- maintainer and ownership continuity;
- release and compatibility history;
- known vulnerabilities and response history;
- license and distribution compatibility;
- transitive module and toolchain cost;
- platform, cgo, and operational requirements; and
- the project's ability to test the behavior it depends upon.

Prefer the standard library when it is adequate. Do not replace a focused,
well-maintained dependency with fragile custom security, protocol, or parsing
code merely to reduce a dependency count.

Upgrade deliberately:

1. inspect release notes, module graph changes, and vulnerability context;
2. select an explicit version;
3. review `go.mod` and `go.sum` changes;
4. run tidy, static analysis, tests, relevant race and integration coverage,
   and vulnerability analysis;
5. build supported deliverables; and
6. record any compatibility or rollout concern.

Do not blindly accept a bulk "latest" update. Do not indefinitely avoid
patched dependencies without recording the constraint and exposure.

## Replacements, Workspaces, and Vendoring

- Treat `replace` directives, especially local filesystem replacements, as
  temporary development state unless the project explicitly documents a
  durable fork.
- Remove accidental replacements before publishing. Replacements apply only
  in a main module or workspace and can make local results differ from
  downstream consumers.
- Run single-module CI with workspace mode disabled unless the workspace is
  intentionally part of the test contract.
- Vendor only for a stated offline, audit, availability, or organizational
  requirement.
- When vendoring, regenerate with the Go tool, commit `vendor/modules.txt`,
  keep it consistent with `go.mod`, and do not hand-edit vendored source.
- Test the actual selected mode. A module-cache build and a vendor build are
  different dependency paths.

## Private Modules and Credentials

Configure `GOPRIVATE` and related proxy/checksum behavior before resolving a
private module path so its name is not disclosed to a public proxy or
checksum database.

- Keep credentials in approved user, CI-secret, or credential-helper storage,
  never in `go.mod`, source, repository URLs, scripts, logs, or diagnostic
  artifacts.
- Record private module prefixes and proxy policy without recording tokens or
  workstation-specific paths.
- Keep authentication non-interactive in CI and fail clearly when access is
  unavailable.
- Do not disable checksum authentication globally merely to solve one private
  module configuration problem.
- Treat module proxies and mirrors as supply-chain infrastructure with
  explicit ownership, access, retention, and incident procedures.

## Builds and Reproducibility

A reproducible Go build requires more than `go.mod` and `go.sum`. Record or
control:

- source revision and dirty-state policy;
- exact Go toolchain;
- selected module graph;
- `GOOS`, `GOARCH`, build tags, experiment flags, and relevant `GOAMD64` or
  analogous target settings;
- cgo mode, C compiler, headers, and native libraries;
- linker and compiler flags;
- generated source and embedded assets;
- version and provenance injection;
- archive timestamps, ownership, ordering, and compression; and
- packaging and signing tools.

Use `-trimpath` when checkout paths are not part of the intended artifact.
Avoid injecting uncontrolled current timestamps. Preserve useful VCS build
metadata, or deliberately replace it with equivalent recorded provenance; do
not disable provenance reflexively.

Cross-compilation demonstrates that code compiles for a target. It does not
demonstrate target runtime behavior, filesystem semantics, networking,
signals, dynamic linking, or cgo compatibility. Execute tests on each
behaviorally significant supported platform.

Do not force `CGO_ENABLED=0` as a generic portability ritual. If the product
supports a pure-Go build, declare and test it. If it uses cgo, treat the
native toolchain and libraries as build, security, and reproduction inputs.

For release artifacts:

- build from a clean, identified source state;
- run the declared release verification with the release toolchain;
- record `go version -m` or equivalent embedded build information;
- retain checksums and signing/provenance records;
- verify installation or startup from the produced artifact; and
- independently rebuild before claiming byte-for-byte reproducibility.

## Security and Vulnerability Handling

- Use the latest patch release within each supported Go release line.
- Run a pinned `govulncheck` against source in CI and against release binaries
  where that view matters.
- Understand its result: call-graph analysis reduces noise by identifying
  reachable vulnerable symbols, but it does not replace dependency review,
  toolchain security updates, configuration review, or testing.
- Review the complete dependency graph after material changes, including
  tool dependencies and modules used only under build tags.
- Add fuzz targets and race coverage at trust and concurrency boundaries as
  described in [Testing and Debugging](testing-and-debugging.md).
- Treat parsers, archive handling, filesystem paths, subprocess invocation,
  templates, network clients and servers, and unsafe or cgo boundaries as
  explicit security review areas.
- Bound input sizes, concurrency, queues, recursion, decompression, retries,
  and time spent on attacker-controlled work.
- Use `crypto/rand` for security-sensitive randomness. Do not substitute a
  deterministic or non-cryptographic generator.
- Set network timeouts and propagate cancellation. Default clients or servers
  without appropriate lifetime limits can turn partial failures into
  resource exhaustion.
- Never expose `pprof`, trace, metrics with sensitive labels, or other debug
  handlers on an unprotected public listener.

When a vulnerability is reported, preserve the advisory and affected-version
evidence, determine actual reachability and configuration exposure, patch or
mitigate, test the fixed path, and record the release or deployment that
contains the resolution.

## Published Module Compatibility

Use semantic versions to communicate compatibility.

- A v1-or-later module preserves backward compatibility within its major
  version.
- A breaking v2-or-later release uses the corresponding `/vN` module and
  import-path suffix.
- Minimize major-version churn; consumers may need both versions during a
  migration and maintainers may need to support both.
- Treat exported names, function signatures, interface method sets, struct
  literal behavior, error identities, side effects, concurrency guarantees,
  and documented defaults as API.
- Test a library as a downstream consumer before release. Executable examples
  and an external test package help exercise that view.
- Publish tags from the correct module directory and verify that the module
  fetched through normal Go tooling contains the intended files and metadata.

## Continuous Integration Matrix

The project-owned CI contract should cover:

- every module independently;
- the declared minimum and normal toolchain versions;
- supported build tags and cgo modes;
- format, tidy, vet, selected static analysis, tests, and deliverable builds;
- a supported race-detector target for concurrent software;
- vulnerability analysis;
- behaviorally significant operating systems and architectures;
- generated-code cleanliness; and
- artifact-level smoke or installation tests before release.

Applications may center CI on the exact production toolchain. Reusable
libraries should normally test both their minimum Go version and a current
supported release. Keep local commands equivalent to CI so a failure is
reproducible without reverse-engineering the pipeline.

## Review Questions

- Is every module an intentional publication or ownership boundary?
- Can a clean checkout identify and acquire the exact required toolchain and
  project tools without ambient global installs?
- Do local workspaces or replacements change what CI and consumers build?
- Are private module names and credentials kept away from public services and
  logs?
- Has each new dependency earned its API, maintenance, security, and
  transitive cost?
- Can the exact release artifact be traced to source, toolchain,
  dependencies, target settings, and packaging inputs?
- Do compatibility claims match the module path and observable API?
- Are vulnerability, race, and target checks applied to the code paths that
  carry the risk?

## Sources

- [Go modules reference](https://go.dev/ref/mod)
- [`go.mod` reference](https://go.dev/doc/modules/gomod-ref)
- [Organizing a Go module](https://go.dev/doc/modules/layout)
- [Managing dependencies](https://go.dev/doc/modules/managing-dependencies)
- [Developing and publishing modules](https://go.dev/doc/modules/developing)
- [Module release workflow](https://go.dev/doc/modules/release-workflow)
- [Developing a major version update](https://go.dev/doc/modules/major-version)
- [Go toolchains](https://go.dev/doc/toolchain)
- [Go security best practices](https://go.dev/doc/security/best-practices)
- [Go vulnerability management](https://go.dev/doc/security/vuln/)
- [`govulncheck`](https://go.dev/blog/govulncheck)
- [Reproducible Go builds](https://go.dev/blog/rebuild)
