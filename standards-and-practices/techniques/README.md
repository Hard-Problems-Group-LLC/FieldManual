# Technique Standards and Practices

## Purpose

Technique documents describe reusable ways to solve recurring engineering
problems. A technique should be broader than one framework, language,
deployment host, or repository layout.

Good technique guidance states:

- the problem and conditions in which the technique applies
- invariants and safety boundaries
- meaningful design choices and tradeoffs
- an implementation-neutral execution pattern
- observable validation outcomes
- failure handling and rollback expectations

Language details belong under [`../languages/`](../languages/README.md).
Framework, database, and infrastructure details belong under
[`../technologies/`](../technologies/README.md). A technique may link to those
pages without prescribing one mandatory stack.

Projects own commands and verification automation for adopted techniques.
FieldManual does not ship technique-specific scripts.

Technique validation should follow
[Test Development and Mock Use](../core/test-development-and-mock-use.md),
and changes should follow
[Pragmatic Edit and Change Safety](../core/pragmatic-edit-and-change-safety.md).

## Available Material

- [Technique guidance template](_template.md)

No TheKnowledge technique was imported verbatim in the initial migration.
Its new-web-service and internal-web-service SOPs assumed a specific
Python/TypeScript/container/network stack, repository layout, and utility
scripts. Their reusable technology practices were retained in the language
and technology subtrees instead.

## Provenance

The organization and template were adapted from TheKnowledge's technique SOP
structure, with stack prescriptions and script dependencies removed.
