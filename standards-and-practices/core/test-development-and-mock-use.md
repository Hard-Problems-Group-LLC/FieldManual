# Test Development and Mock Use

## Purpose

Use tests to establish confidence in observable behavior, failure handling,
and compatibility boundaries rather than merely reproducing implementation
details.

## Test Design

- Start from a documented behavior, acceptance criterion, defect, or risk.
- Cover representative success paths, boundary conditions, failure modes, and
  regressions.
- Keep fixtures deterministic, minimal, and explicit about their purpose.
- Put disposable test workspaces under the configured project root's
  `.local/tmp/` by default, following
  [Local Operator State](local-operator-state.md) for naming, cleanup,
  security, and system-temporary-directory exceptions.
- Prefer assertions about externally meaningful outcomes over incidental
  call counts or internal ordering.
- Use the narrowest test level that proves the behavior, then retain
  representative real-path coverage for important integrations.
- Treat test flakiness as a defect, not as an ordinary retry condition.

## Real Implementations, Fakes, and Mocks

Prefer a real local implementation when it is deterministic, inexpensive, and
safe.

Use a small fake when a substitute with a documented behavior contract is
clearer and more stable than dynamic mocking.

Reserve mocks for boundaries that are:

- external;
- destructive or unsafe;
- expensive;
- nondeterministic;
- unavailable in the test environment; or
- impractical to force into a needed failure state.

Unit tests may mock an owned collaborator when isolating one bounded decision.
Integration, contract, smoke, browser, and end-to-end tests should normally
exercise real owned wiring.

Important behavior tested through mocks should also have representative
real-path coverage. Review mock-heavy tests for brittle call choreography,
false confidence, and assumptions that users cannot observe.

## Evidence and Completion

Record what was tested, where it was tested, and any important validation that
could not run. A local pass on an emulated platform does not replace
authoritative validation on a supported target platform.

FieldManual defines this test doctrine but does not prescribe executable
test commands. Those belong to consuming projects or verifier submodules.
