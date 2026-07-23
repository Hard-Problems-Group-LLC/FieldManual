# Core Standards and Practices

This directory contains the reusable, language- and platform-neutral operating
standards for projects that adopt FieldManual.

The documents are intentionally descriptive rather than executable. They
define expected outcomes, decision boundaries, record lifecycles, and review
criteria. A consuming project may implement those expectations with tools
appropriate to its languages and platforms. Executable verification belongs
in the consuming project or in a separately versioned verifier submodule.

## Contents

- [Development Workflow](development-workflow.md)
- [Proposal Format](proposal-format.md)
- [Documentation](documentation.md)
- [Test Development and Mock Use](test-development-and-mock-use.md)
- [Pragmatic Edit and Change Safety](pragmatic-edit-and-change-safety.md)
- [Local Operator State](local-operator-state.md)
- [Session and Project Boundaries](session-and-project-boundaries.md)
- [Version-Control Safety](version-control-safety.md)
- [Changelog and History](changelog-and-history.md)
- [Proposal and Bug Lifecycle](proposal-and-bug-lifecycle.md)
- [Engineering Change Requests](engineering-change-requests.md)
- [Runtime and Package Environments](runtime-and-package-environments.md)

## Interpretation

- Project-specific instructions may strengthen these standards.
- A project should record any deliberate variance near the affected policy or
  in its decision log.
- When two documents appear to conflict, prefer the more specific
  project-owned instruction and record the conflict for correction.
- Avoid copying the same normative rule into many files. Point to its
  canonical document instead.

## Provenance

These standards were adapted in July 2026 from reusable material audited in
TheKnowledge. They were rewritten for FieldManual to remove implementation
machinery, fixed toolchains, language-specific commands, special-purpose
branches, and repository-specific assumptions. The original proposal and
decision history remains source-project provenance; these documents are the
maintained FieldManual form.
