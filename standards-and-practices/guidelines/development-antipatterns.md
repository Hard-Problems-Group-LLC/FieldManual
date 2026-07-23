# Development Antipatterns

## Scope

These cross-cutting antipatterns commonly reduce delivery quality,
traceability, and recoverability.

## Avoid

- Starting material implementation before requirements, acceptance criteria,
  or explicit direction are recorded.
- Depending on tribal knowledge, one workstation, or shell history to build,
  test, operate, or recover a system.
- Mixing unrelated behavior changes, refactors, formatting churn, generated
  updates, and tooling migrations into one review unit.
- Treating tests, documentation, security review, or recovery planning as
  cleanup after implementation.
- Keeping important decisions or operational state only in transient chat.
- Accepting generated or AI-produced changes without checking them against
  actual requirements and observable behavior.
- Coupling deployment, backup, rollback, or incident recovery to one host or
  operator.
- Allowing documentation, project state, and release history to drift from
  what shipped.
- Adding automation before the manual contract is understood well enough to
  test.

## Recommended Default

- Keep changes small enough to review confidently.
- Record requirements, decisions, and recovery steps in versioned,
  appropriately scoped files.
- Make routine build, validation, and recovery paths repeatable.
- Exercise edge cases and failure behavior before calling work complete.
- Treat documentation and project-state updates as delivery work.

## Sources and Review Caveat

This guidance reflects long-lived continuous-integration, operational
excellence, and site-reliability practices. Project context can justify a
different choice, but the tradeoff should be explicit.

Reviewed: 2026-07-23.

- Martin Fowler, [Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)
- Google, [Site Reliability Engineering](https://sre.google/sre-book/table-of-contents/)
- Microsoft,
  [Operational Excellence](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/)
