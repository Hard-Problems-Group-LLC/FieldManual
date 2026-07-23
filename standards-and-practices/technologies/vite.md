# Vite

## Use When

Use Vite for frontend development and production builds when its plugin model
fits the selected framework. Keep development-server convenience separate
from production hosting and security assumptions.

## Project-Declared Version Policy

Declare compatible Vite, Node.js, package-manager, framework-plugin, and test
runner versions together. Commit the lockfile and review build output after
major upgrades.

## Configuration Baseline

- Keep frontend code and build configuration under a clear ownership root.
- Define backend proxy routes explicitly and limit them to development where
  appropriate.
- Keep aliases, public paths, output directories, and browser targets
  reviewable.
- Treat client-exposed environment variables as public. In particular, do
  not place secrets in values intentionally exposed to application code.
- Keep plugins minimal and justify plugins that execute code during build.

## Security and Operations

Do not treat development-server TLS, proxy exceptions, or network binding as
production controls. Bind development servers only as broadly as required.
Review source-map publication and bundle contents for unintended source or
configuration disclosure.

Use terminal diagnostics and the browser overlay during development, but keep
production build and deployment failures observable outside the development
server.

## Validation

- Run the project's unit and component tests.
- Build the production bundle from a clean dependency install.
- Smoke-test the built output through its intended hosting path.
- Verify proxy behavior, base paths, dynamic imports, and static assets.
- Confirm hot reload still works after module-boundary changes without using
  it as a substitute for a production build.

Exact commands and automation are project-owned. FieldManual ships no Vite
verifier.

## Failure Handling and Rollback

Keep previously deployable static artifacts or a reproducible prior build
available for rollback. Separate package, plugin, proxy, application, and
hosting failures during diagnosis.

## Maintenance Risks

- Development proxy behavior drifting from deployed routing.
- Secrets included in client-visible environment data.
- Mixed exports interfering with framework hot reload.
- Floating dependencies changing build output.
- Successful development startup masking a broken production bundle.

## Related Guidance

- [TypeScript](../languages/typescript/README.md)
- [React](react.md)
