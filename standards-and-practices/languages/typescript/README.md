# TypeScript Standards and Practices

## Scope

This document provides a default TypeScript engineering profile for browser,
server, library, and tooling projects. Projects should narrow the profile to
the environments they actually support.

## Project-Declared Baseline

Record the supported TypeScript and JavaScript runtime versions in
project-owned configuration. For Node.js projects, declare the supported
Node.js release line and package-manager family. Keep those declarations
aligned across local development, continuous integration, packaging, and
deployment.

Commit the chosen lockfile. Where the ecosystem supports it, declare the
package-manager version or use an appropriate project selector so clean
checkouts do not depend on an operator's incidental global default.

## Code Quality

- Use deterministic formatting and linting. Prettier and ESLint are common
  choices, but their selection and rules belong to the project.
- Run the TypeScript compiler in type-checking mode without relying on an
  emitted build as the only type check.
- Avoid allowing `any` to become an undocumented interface contract.
- Narrow `unknown` values deliberately at trust boundaries.
- Share or generate transport types instead of maintaining inconsistent DTO
  copies across multiple modules.
- Keep generated files clearly identified and out of hand-edited source
  paths.

## Dependencies and Environments

- Install dependencies from the committed manifest and lockfile.
- Keep runtime dependencies separate from development-only tooling.
- Invoke project-local command shims through package scripts or the selected
  package manager.
- Do not require global formatter, linter, compiler, or test-runner installs.
- Treat browser-visible environment values as public data. Never place secrets
  in frontend bundles or development-server configuration.

## Design Practices

- Keep state ownership and asynchronous effects explicit.
- Clean up subscriptions, timers, observers, and in-flight work when their
  owning lifecycle ends.
- Separate reusable components from page or application orchestration.
- Keep utility-only exports separate when a framework's hot-reload model
  depends on component export boundaries.
- Treat responsive behavior, keyboard operation, focus, and accessibility as
  functional requirements.
- Represent loading, empty, error, retry, and stale-data states explicitly.

## Testing and Verification

Vitest is a common choice for unit and component tests. Add browser-level or
end-to-end coverage when user workflows, rendering, focus, routing, or
cross-component behavior carry material risk.

- Type-check without emitting output.
- Test production builds, not only development-server behavior.
- Exercise supported runtime and browser boundaries where compatibility is a
  stated promise.
- Keep local test and build commands equivalent to continuous integration.
- Test API-contract decoding and failure behavior at trust boundaries.

All formatter, linter, compiler, test, and build commands are project-owned.
FieldManual ships no TypeScript or JavaScript verifier.

## Common Pitfalls

- Treating successful transpilation as proof of runtime correctness.
- Letting unlocked dependency updates change clean-checkout behavior.
- Duplicating backend data shapes instead of maintaining a typed boundary.
- Mixing component and utility exports in ways that break hot reload.
- Treating responsive and accessible behavior as optional visual polish.
- Assuming values available to browser code can remain secret.

## Related Guidance

- [Runtime and Package Environments](../../core/runtime-and-package-environments.md)
- [Test Development and Mock Use](../../core/test-development-and-mock-use.md)
- [React](../../technologies/react.md)
- [Vite](../../technologies/vite.md)
