# Go Standards and Practices

Source review: 2026-07-23.

## Scope

This directory provides FieldManual's default engineering profile for Go
modules, packages, libraries, commands, and services. The language's name is
Go; `go/` is the conventional short directory name. Technology-specific
rules, such as those for an HTTP framework, RPC system, database, or
orchestrator, belong under `../../technologies/`.

A consuming project may strengthen or specialize this profile when it records
the decision explicitly. It must not quietly weaken correctness, security, or
compatibility promises.

## How To Use This Profile

Read this overview for every substantive Go engagement, then load the focused
documents that apply:

- [Code and API Design](code-and-api-design.md) for formatting, naming,
  packages, interfaces, errors, context, concurrency, documentation, and
  diagnostic design.
- [Testing and Debugging](testing-and-debugging.md) for test structure,
  deterministic concurrency tests, fuzzing, the race detector, benchmarks,
  logging evidence, profiles, traces, and verification outcomes.
- [Modules, Builds, and Security](modules-builds-and-security.md) for
  repository layout, dependency and tool management, private modules,
  reproducible builds, release compatibility, and vulnerability handling.
- [Tooling Installation and Maintenance](tooling-installation-and-maintenance.md)
  for system-wide, user-wide, and project-local ownership; tool and package
  dependency graphs; clean onboarding; caches; and administrator policy.

These documents define outcomes and review criteria. FieldManual does not
install Go, choose a linter on a project's behalf, or provide a Go
verification script.

## Engineering Priorities

Prefer, in order:

1. correct and safe behavior;
2. clarity to the reader;
3. the simplest design that serves the real use case;
4. useful interfaces and operational behavior;
5. maintainability and ease of diagnosis;
6. consistency with the surrounding Go code; and
7. performance demonstrated by measurement.

Concise code is valuable when it improves signal, but brevity is not a reason
to hide ownership, failure, cancellation, synchronization, or data flow.
Choose familiar Go constructs over clever compression, speculative
abstraction, reflection, or a custom mini-framework.

Optimize for the maintainer who is debugging the code under imperfect
conditions. Important decisions, lifetimes, boundaries, and failure paths
should be visible from the code and its public contract.

## Project-Declared Baseline

Every Go project must record in project-owned configuration or documentation:

- each module root and durable module path;
- the minimum Go language/toolchain version;
- the normal development and release toolchain versions;
- supported `GOOS` and `GOARCH` targets;
- whether cgo is required, optional, or unsupported;
- required build tags and generated-code steps;
- commands for formatting, analysis, tests, builds, security checks, and
  releases; and
- the compatibility and upgrade policy for public modules and deployed
  applications.

The `go` directive in `go.mod` is the module's minimum required Go version and
also selects language and command semantics. A `toolchain` directive is a
suggested toolchain for work in the main module; it is not a substitute for a
documented support policy.

Libraries should normally test their declared minimum version and a current
supported release. Applications should pin the exact patched toolchain used
to build production artifacts. Upgrade supported release lines deliberately,
and take current patch releases promptly after proportionate testing,
especially when they contain security fixes.

Do not turn the Go version current on this document's review date into a
permanent requirement. The project's recorded baseline is authoritative.

## Version-Gated Practices

Use newer facilities only when every toolchain in the declared support matrix
can build the affected code.

| Facility | Available from | FieldManual use |
| --- | --- | --- |
| Native fuzzing | Go 1.18 | Prefer for high-risk, structurally varied input. |
| Automatic toolchain selection | Go 1.21 | Configure deliberately; do not let it mask a minimum-version test. |
| `log/slog` | Go 1.21 | Preferred standard-library structured logger for new applications when supported. |
| `go.mod` `tool` directives | Go 1.24 | Preferred option for pinned project tools when supported. |
| `testing.B.Loop` | Go 1.24 | Preferred benchmark loop on supported toolchains. |
| `testing.T.Context` | Go 1.24 | Preferred root context for test-owned work when supported. |
| Stable `testing/synctest` | Go 1.25 | Prefer where it makes concurrent or time-based tests deterministic. |
| `testing.T.ArtifactDir` | Go 1.26 | Use to stage useful diagnostics; retain them with `go test -artifacts` and, when needed, `-outputdir`. |

This table is a compatibility aid, not an instruction to raise a project's
minimum version merely to obtain a convenience.

## Required Verification Outcomes

Each project must define executable checks appropriate to its risks. At
minimum, its declared workflow should demonstrate:

- canonical formatting;
- module-file consistency;
- successful compilation of supported packages and commands;
- unit and integration behavior;
- explicit `go vet` and any selected high-signal static analysis;
- race detection for concurrent code on a supported platform;
- known-vulnerability analysis;
- supported-version and target coverage; and
- reproducible failure information when a check does not pass.

The focused documents explain these outcomes and common implementations.
Commands remain owned by the consuming project.

## Common Pitfalls

- Importing a package hierarchy or object model from another language instead
  of designing small Go packages around coherent responsibilities.
- Creating `util`, `common`, `types`, `api`, or `interfaces` dumping grounds.
- Introducing an interface, generic abstraction, goroutine, or channel before
  a concrete need establishes its value and ownership.
- Treating `go.sum` as a conventional lockfile or `go mod verify` as a
  vulnerability scanner.
- Logging and returning the same error at every layer.
- Starting background work without a stop condition, error path, and wait
  mechanism.
- Using sleeps, coverage percentages, or a passing race run as substitutes
  for deterministic assertions and exercised behavior.
- Depending on an unpinned workstation tool or allowing local `go.work` and
  `replace` state to alter release validation.
- Exposing diagnostic endpoints, payloads, credentials, or sensitive
  configuration in logs.
- Optimizing code before a benchmark or profile identifies a meaningful
  bottleneck.

## Related Guidance

- [Runtime and Package Environments](../../core/runtime-and-package-environments.md)
- [Test Development and Mock Use](../../core/test-development-and-mock-use.md)
- [Documentation](../../core/documentation.md)
- [Development Workflow](../../core/development-workflow.md)
- [Pragmatic Edit and Change Safety](../../core/pragmatic-edit-and-change-safety.md)

## Source Basis and Currency

This profile synthesizes the current Go specification, standard-library and
tool documentation, module guidance, security guidance, and diagnostics
documentation with the living Google Go Style Guide and selected production
practices from Uber's Go Style Guide.

Source authority is applied in this order:

1. current Go specifications and official package/tool documentation for
   language and tool behavior;
2. current Go project guidance for ecosystem practices;
3. the Google guide for a comprehensive readability model;
4. selected industry practices when they improve portable ownership,
   maintenance, or diagnosis.

[Effective Go](https://go.dev/doc/effective_go) remains useful for core
idioms, but its own notice says it was written for the 2009 release and is not
actively updated; it is not authoritative for modules, generics, or newer
libraries. Organization-specific tools and house rules from Google and
[Uber](https://github.com/uber-go/guide/blob/master/style.md) were not copied
as universal requirements.

Primary entry points:

- [Go release history and support policy](https://go.dev/doc/devel/release)
- [Go module reference](https://go.dev/ref/mod)
- [Organizing a Go module](https://go.dev/doc/modules/layout)
- [Go doc comments](https://go.dev/doc/comment)
- [Go security best practices](https://go.dev/doc/security/best-practices)
- [Go diagnostics](https://go.dev/doc/diagnostics)
- [Google Go Style Guide](https://google.github.io/styleguide/go/)

Review this profile when the supported Go baseline changes materially, when a
new release changes a cited facility, or at least annually.
