# Python Standards and Practices

## Scope

This document provides a default Python engineering profile. A consuming
project may adopt stricter requirements when it records them explicitly.

## Project-Declared Baseline

Record the minimum and supported Python versions in project-owned
configuration and use the same supported version line in local development,
continuous integration, packaging, containers, and deployment.

Choose a maintained Python release that is compatible with required
libraries and deployment targets. Do not infer a project's runtime baseline
from FieldManual's own installer: FieldManual retains Python 3.9
compatibility only so its bootstrap can run on broadly available
interpreters. Python 3.9 is not a universal recommendation for project
runtimes.

## Code Quality

- Use one deterministic formatter and one primary linter. Black and Ruff are
  common choices, but the project owns the selection and configuration.
- Require type annotations on public interfaces and important service,
  storage, and integration boundaries.
- Add mypy, Pyright, or an equivalent checker when the project relies on
  typed boundaries. Record the checked source roots and strictness policy.
- Keep imports free of surprising network, filesystem, database, and process
  side effects.
- Document public modules, types, and callables, plus non-obvious invariants
  and failure behavior.

## Dependencies and Environments

- Declare runtime and development dependencies in reviewable project files.
- Use an isolated project environment for development and test dependencies.
- Keep lock or constraint behavior explicit when reproducibility matters.
- Prefer module-aware entry points such as `python -m package.module` so
  import behavior does not depend on an incidental working directory.
- Keep configuration in explicit settings or dependency objects rather than
  mutable module globals.
- Treat environment creation and dependency installation as project-owned
  setup work. FieldManual does not install Python toolchains or packages.

## Design Practices

- Do not place blocking I/O in asynchronous request or worker paths.
- Keep transport handlers thin; route domain work through service boundaries.
- Keep persistence details behind repository or data-access boundaries.
- Treat migrations, seeders, importers, and repair tools as maintained
  project artifacts rather than one-off shell history.
- Make resource ownership visible with context managers or explicit lifecycle
  methods.
- Prefer exceptions that preserve useful cause and remediation context at
  integration boundaries.

## Testing and Verification

Pytest is a common default for unit, integration, and repeatable smoke tests,
but the project may choose another runner.

- Exercise important behavior through real owned implementations when doing
  so is deterministic, inexpensive, and safe.
- Use fixtures and small fakes before mocks shaped around implementation
  details.
- Test supported interpreter versions when compatibility across versions is a
  stated requirement.
- Run representative database, network-boundary, packaging, and command-line
  integration tests where those behaviors matter.
- Keep local verification and continuous-integration commands equivalent.

All formatter, linter, type-checker, and test commands are project-owned.
FieldManual ships no Python verifier.

## Common Pitfalls

- Depending on ambient user or system packages.
- Mixing application configuration with import-time global state.
- Letting web handlers communicate directly with database sessions.
- Mocking owned application wiring in tests described as integration tests.
- Assuming a virtual environment proves that dependency versions are
  reproducible.
- Publishing a package without testing the built artifact.

## Related Guidance

- [Runtime and Package Environments](../../core/runtime-and-package-environments.md)
- [Test Development and Mock Use](../../core/test-development-and-mock-use.md)
- [FastAPI](../../technologies/fastapi.md)
- [SQLAlchemy](../../technologies/sqlalchemy.md)
- [Alembic](../../technologies/alembic.md)
- [Berkeley DB](../../technologies/berkeley-db.md)
