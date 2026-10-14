# Testing Knacks

Reviewed: 2026-10-13

Use these knacks for test techniques that apply across languages and
products: how to gather evidence where ordinary unit tests cannot reach, and
how to keep that evidence honest. FieldManual's
[test standard](../../../standards-and-practices/core/test-development-and-mock-use.md)
sets the doctrine; these knacks give working patterns.

## Contents

- [In-Host Smoke Testing](in-host-smoke/overview.knack.md) —
  testing a plugin inside a closed host application with an in-plugin
  runner, an isolated data folder, a structured log protocol and a launcher
  - [Runner](in-host-smoke/runner.knack.md)
  - [Launcher](in-host-smoke/launcher.knack.md)
  - [Flakiness](in-host-smoke/flakiness.knack.md)
- [Proving Checks Can Fail](proving-checks/overview.knack.md) —
  sabotage runs for new checks, red-first regression checks, and the
  patterns by which checks pass vacuously
  - [Vacuous checks](proving-checks/vacuity.knack.md)
  - [Sabotage runs](proving-checks/sabotage.knack.md)

## Related

- [Adversarial Review](../../AI/agent-orchestration/adversarial-review/overview.knack.md)
  — skeptic verification of review findings in agent workflows
- [Data-First Generation](../procedural-generation/data-first/overview.knack.md)
  — testing generated content as host-free data

A consuming project owns its test commands, host versions, timeouts,
thresholds and flaky-check registry.
