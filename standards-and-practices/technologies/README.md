# Technology Standards and Practices

## Purpose

This subtree holds guidance for frameworks, databases, infrastructure tools,
and other technologies that may be used from more than one language.
Technology pages remain separate from language pages so projects can combine
them without inheriting an assumed stack.

Each page describes:

- when the technology is an appropriate choice
- how a project declares its supported version
- configuration and security expectations
- observability and operational behavior
- local and continuous-integration validation
- failure handling, rollback, and maintenance risks

## Adoption Policy

A consuming project owns the decision to adopt a technology, its supported
version, and its executable commands. FieldManual does not install these
technologies and does not ship technology-specific verification wrappers.

Examples describe intent rather than a universal command line. Projects
should record exact commands in their own documentation and automation.

Technology validation should follow the shared
[test development](../core/test-development-and-mock-use.md) standard, and
runtime selection should follow
[runtime and package environments](../core/runtime-and-package-environments.md).

## Available Guidance

- [Alembic](alembic.md)
- [Berkeley DB](berkeley-db.md)
- [Caddy](caddy.md)
- [FastAPI](fastapi.md)
- [Podman](podman.md)
- [PostgreSQL](postgresql.md)
- [React](react.md)
- [SQLAlchemy](sqlalchemy.md)
- [Tailscale](tailscale.md)
- [Vite](vite.md)
- [Technology guidance template](_template.md)

## Provenance

The initial pages were adapted from TheKnowledge's technology SOPs. They were
rewritten as concise, cross-linked guidance with project-owned version and
verification policy. TheKnowledge-specific scripts, bootstrap assumptions,
and prescribed application stack were excluded.
