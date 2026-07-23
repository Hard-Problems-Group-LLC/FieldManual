# Language Standards and Practices

## Purpose

This subtree holds guidance that applies to a particular programming
language or its usual development ecosystem. Cross-language engineering
standards belong elsewhere; technology-specific guidance belongs under
[`../technologies/`](../technologies/README.md).

Each language directory should explain:

- how a project declares its supported language and runtime versions
- formatting, linting, and static-analysis expectations
- dependency and environment practices
- testing strategy and continuous-integration parity
- common design and maintenance hazards
- related technology guidance

## Baseline Policy

Consuming projects own their version baselines. A language page may describe
reasonable selection criteria, but it must not turn a moving "current
version" into a permanent FieldManual requirement.

Projects should record supported versions in a reviewable project-owned file
and keep local development, continuous integration, packaging, and deployment
aligned with that declaration.

Projects also own their verification commands and any scripts that run them.
FieldManual provides standards and practices; it does not ship
language-specific formatters, linters, test runners, or verification scripts.

The language pages apply the shared
[runtime and package environment](../core/runtime-and-package-environments.md)
and [test development](../core/test-development-and-mock-use.md) standards.

## Available Guidance

- [Go](go/README.md)
- [Python](python/README.md)
- [TypeScript](typescript/README.md)
- [Language guidance template](_template.md)

## Adding a Language

Start from `_template.md`. Keep the guidance useful without assuming a
particular package manager, editor, operating system, or repository layout.
Link to technology pages rather than nesting or duplicating them under a
language.

## Provenance

The initial Python and TypeScript guidance was adapted from TheKnowledge's
language SOPs. It was rewritten to use project-declared, time-resilient
baselines and to remove TheKnowledge-specific bootstrap and verification
machinery. The Go profile was researched separately against current official
Go documentation and living industry guidance; its source review and currency
policy are recorded in the profile.
