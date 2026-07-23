# Go Testing and Debugging

## Purpose

Make Go verification representative, deterministic, and useful when it
fails. This document covers tests, fuzzing, race detection, benchmarks,
diagnostic evidence, profiles, traces, and the outcomes a project-owned
verification workflow should provide.

Apply the shared [test development and mock-use
standard](../../core/test-development-and-mock-use.md) first.

## Test Structure

- Keep `*_test.go` files beside the package they test.
- Use an external `package name_test` when the consumer-visible API is the
  subject. Use the package itself when access to unexported behavior is
  necessary and materially improves the test.
- Test observable contracts, important invariants, failure behavior, and
  lifecycle obligations rather than duplicating implementation steps.
- Prefer the standard `testing` package unless an additional library provides
  enough value to justify its dependency and failure vocabulary.
- Use table-driven tests when cases share genuinely similar setup, action,
  and assertion logic. Give rows descriptive names and use named subtests
  when isolation and filtering help.
- Use separate tests when a table would require branches, optional fields, or
  case-specific control flow that obscures the scenario.
- Write failure messages that identify the operation and inputs and report
  `got` before `want`. A failure should make the next diagnostic action
  obvious.
- Test helpers that can fail accept the current testing handle, call
  `Helper` immediately, and add relevant context.
- Use `Error` when later checks remain meaningful. Use `Fatal` only when the
  current test or subtest cannot continue.
- Never call `FailNow`, `Fatal`, or `Fatalf` from a goroutine other than the
  one running that test or subtest. Return an error or result to the owning
  test goroutine.
- Use executable examples with `// Output:` for public APIs whose correct use
  benefits from a compiled demonstration.

Prefer small tests with a clear reason to fail. A large assertion framework
or shared fixture is not automatically more maintainable than direct Go.

## Isolation and Determinism

Tests must be independently runnable and must not depend on:

- execution order;
- a developer's credentials or home-directory state;
- a public network service;
- mutable process globals left by another test;
- arbitrary wall-clock sleeps;
- a previously populated module or build cache; or
- undeclared files, ports, tools, or environment values.

Use `Cleanup`, `TempDir`, and `Setenv` when the project baseline supports
them. Use the testing handle's context for test-owned work when available.
Remember that environment variables and the process working directory are
process-wide and cannot be changed safely by parallel tests.

Parallelize only tests that are actually isolated. Identify shared ports,
files, environment, process globals, rate limits, and external fixtures
before calling `Parallel`.

Periodically shuffle tests to expose order dependencies and retain the
reported shuffle seed when a failure occurs. When a test uses randomized
domain input, print and preserve its seed and minimized failing input.

## Time and Concurrent Behavior

Prefer a synchronous API when callers can choose concurrency themselves.
When asynchronous behavior is part of the contract:

- expose completion and error observation;
- test cancellation, deadline, backpressure, and shutdown paths;
- wait on explicit events or state transitions rather than sleeping for an
  estimated duration;
- place a bounded diagnostic timeout around a wait so a regression fails
  with useful state instead of hanging indefinitely; and
- verify that owned goroutines and resources terminate before the test ends.

For projects supporting Go 1.25 or later, `testing/synctest` can make
in-process concurrent and time-based tests deterministic. Use it when its
isolated bubble and fake clock match the system under test. It does not
replace integration tests involving real networks, external processes, or
events outside the bubble.

On older baselines, inject a clock or coordination dependency where that
keeps the production API clear, or synchronize on explicit channels and
state. Avoid "eventually" polling without a deadline and failure details.

## Real Implementations and Test Doubles

- Exercise owned implementations directly when doing so is deterministic,
  inexpensive, and safe.
- Use `httptest`, in-process protocol endpoints, temporary files, and
  disposable real services to retain production encoding and client behavior
  where appropriate.
- Prefer a small fake at an external boundary over a mock that asserts an
  internal call sequence.
- Do not replace the project's own composition root in a test described as
  integration or end-to-end.
- Keep test-only interfaces as small as the consumer requires. Do not distort
  a production API solely to satisfy a mocking framework.
- Record intentional integration-test prerequisites and skips. A skipped test
  must be visible in the verification result rather than silently treated as
  coverage.

## Fuzzing

Use native fuzzing for parsers, decoders, protocol and serialization
boundaries, path and identifier handling, round trips, and other untrusted or
structurally varied input.

- Seed valid, invalid, empty, boundary, and previously failing cases.
- Assert useful invariants such as round-trip stability, bounded output,
  canonicalization, preserved meaning, or a documented error. "Does not
  panic" alone is rarely enough.
- Keep each fuzz iteration independent, bounded, and free from persistent
  external side effects.
- Do not retain or mutate fuzz-owned input after an iteration.
- Preserve minimized failures under the package's fuzz corpus so ordinary
  tests rerun them as regressions.
- Use a bounded fuzz budget in normal CI and longer scheduled or continuous
  campaigns for security-sensitive targets.

Fuzzing supplements designed examples and integration behavior; it does not
replace them.

## Race Detection

Run the race detector in a separate supported-platform job for projects with
concurrent code. Exercise a race-instrumented binary under realistic load
when package tests do not cover the relevant runtime paths.

The detector reports only races that execute. A passing run is evidence about
the exercised paths, not a proof that the program is race-free. Increase
useful concurrent coverage instead of treating repeated identical runs as a
formal guarantee.

Document every exclusion with the unsupported platform, resource constraint,
or test defect and a follow-up condition. Do not hide a known race behind a
build tag.

## Coverage

Use coverage reports to locate important behavior that lacks tests and to
understand which paths a verification run exercised. Do not use a universal
percentage as a proxy for assertion quality, integration realism, race
coverage, or security.

Branch, error, state-transition, and ownership coverage often provides more
value than executing another trivial line. Review uncovered code in the
context of its risk.

## Benchmarks and Performance

A benchmark should answer a decision, guard a known performance property, or
reproduce an observed bottleneck.

- Profile representative behavior before optimizing production code.
- On supported toolchains, prefer `testing.B.Loop` and keep ordinary setup
  outside the measured loop.
- Report allocations when allocation behavior matters.
- Prevent benchmark work from being optimized away and verify that the
  benchmark still represents the intended operation.
- Compare multiple before-and-after samples on the same quiet machine,
  toolchain, target, flags, and configuration. Use a statistical comparison
  tool such as a pinned `benchstat`; do not infer a regression from one noisy
  result.
- Record the Go version, `GOOS`, `GOARCH`, CPU, benchmark arguments, and
  relevant configuration with published results.
- Validate performance improvements against correctness, readability, and
  operational cost. Keep a more complex implementation only when the
  measured benefit justifies its maintenance burden.

Microbenchmarks do not substitute for end-to-end latency, throughput,
resource, or production profiles.

## Logging and Failure Evidence

Tests and tools should leave enough evidence to reproduce a failure without
requiring a second lucky occurrence.

- Include the failing test or subtest, safe input or corpus reference, seed,
  toolchain, target, relevant flags, and dependency/configuration mode.
- Preserve bounded stdout, stderr, structured logs, and service diagnostics
  for failed integration tests.
- Use the testing package's artifact directory when supported and useful.
  Its contents are temporary unless `go test -artifacts` retains them; use
  `-outputdir` when the collection location must be controlled. On older
  baselines, place retained artifacts in a project-declared CI location.
- Avoid logging secrets, credentials, complete sensitive payloads, or
  checkout-local private paths.
- Keep failure output focused. Repeated stack frames and the same logged error
  at every layer make diagnosis harder.

## Debuggers, Profiles, and Traces

- Use Delve for interactive source debugging when a debugger is the right
  tool; it understands Go runtime behavior better than a generic native
  debugger.
- Retain symbols or a corresponding debuggable artifact for builds that may
  require post-failure analysis.
- Use CPU and heap profiles for hot paths and allocation behavior.
- Use goroutine, block, and mutex profiles for leaks, stalls, and contention.
- Use execution traces for scheduler behavior, goroutine timelines,
  serialization, and latency across concurrent work.
- Capture one intrusive diagnostic mode at a time when their overhead could
  distort results, and record the capture conditions.
- Expose `pprof`, trace, and other debug endpoints only through an isolated,
  authenticated, or otherwise protected operational path. They are sensitive
  control and information surfaces.
- Prefer measurements from representative workloads. A convenient local
  profile of an unrealistic path can be precisely misleading.

## Project-Owned Verification Contract

A normal Go project should define commands that provide these outcomes. The
commands below are common implementations, not scripts supplied by
FieldManual.

| Outcome | Common implementation | Typical cadence |
| --- | --- | --- |
| Canonical source | `gofmt` or a pinned `goimports` cleanliness check | Every change |
| Module consistency | `go mod tidy -diff`, or tidy followed by a clean-diff check | Every change |
| Likely correctness defects | `go vet ./...` plus selected pinned analyzers | Every change |
| Package behavior | `go test ./...` in each module | Every change |
| Deliverable compilation | `go build` for declared commands and target configurations | Every change |
| Data races | `go test -race ./...` on a supported platform | Every change or a frequent separate job |
| Known reachable vulnerabilities | pinned `govulncheck ./...` | Every change and before release |
| Fuzz exploration | bounded native fuzz targets | Short CI budget plus longer scheduled runs |
| Version compatibility | minimum and current declared Go toolchains | Libraries and compatibility-sensitive applications |
| Platform behavior | native tests on behaviorally significant targets | According to support and risk |

Run the workflow separately in each nested module; the `./...` pattern does
not cross a module boundary. Build tags and cgo modes in the support contract
also need explicit coverage.

## Review Questions

- Can every test run alone, in a shuffled order, and in a clean checkout?
- Does each failure identify the operation, input, got value, and wanted
  contract?
- Are time, cancellation, and goroutine completion synchronized explicitly?
- Do integration tests retain the real encoding and client/server behavior
  that matters?
- Are fuzz and race runs exercising risky paths rather than merely existing?
- Is a benchmark tied to a decision and supported by representative
  measurement?
- Can an operator collect the right profile or trace without exposing a
  public debug surface?

## Sources

- [`testing` package](https://pkg.go.dev/testing)
- [Subtests and sub-benchmarks](https://go.dev/blog/subtests)
- [Testable examples](https://go.dev/blog/examples)
- [`testing/synctest` package](https://pkg.go.dev/testing/synctest)
- [Testing time and asynchronous code](https://go.dev/blog/testing-time)
- [Go fuzzing](https://go.dev/doc/security/fuzz/)
- [Data race detector](https://go.dev/doc/articles/race_detector)
- [Go security best practices](https://go.dev/doc/security/best-practices)
- [Benchmark loops](https://go.dev/blog/testing-b-loop)
- [Go diagnostics](https://go.dev/doc/diagnostics)
- [Diagnostics with execution traces](https://go.dev/blog/execution-traces-2024)
- [Google Go testing best practices](https://google.github.io/styleguide/go/best-practices#tests)
