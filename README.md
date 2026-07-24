# FieldManual

FieldManual is a reusable standards and practices library for projects that
use AI-assisted development. It gives human and AI collaborators a common
operating baseline without prescribing one programming language, platform,
editor, package manager, or verification stack.

The framework supplies:

- language-neutral development, testing, documentation, change-safety, and
  project-management practices;
- separate language, technology, and technique guidance that projects load
  only when applicable;
- reusable task guidance in the form of knacks;
- clean project-management, review, specification, and cross-project ECR
  skeletons; and
- one dependency-free Python bootstrap that installs those skeletons and
  establishes an explicit project/framework configuration.

FieldManual does not install runtimes, dependencies, Git hooks, linters,
formatters, scanners, or language-specific verification programs. Projects
own their executable toolchains. Reusable verification suites may later be
distributed as separate submodules.

## Start Here

For every engagement:

1. Read the project's `FieldManual-config.toml`.
2. Apply `.local/FieldManual-localconfig.toml` when it exists.
3. Confirm which project root is being changed and which FieldManual checkout
   supplies the guidance.
4. Read [core standards](standards-and-practices/core/README.md).
5. Load the applicable
   [language](standards-and-practices/languages/README.md),
   [technology](standards-and-practices/technologies/README.md),
   [technique](standards-and-practices/techniques/README.md), and
   [knack](knacks/README.md) documents.
6. Follow the consuming project's own instructions and explicitly recorded
   exceptions.

Project-specific policy should refine FieldManual's defaults rather than
silently contradicting them.

## Root Configuration

Every consuming project keeps a tracked configuration at:

```text
$(PROJECTROOT)/FieldManual-config.toml
```

Checkout-local overrides live at:

```text
$(PROJECTROOT)/.local/FieldManual-localconfig.toml
```

Both files declare:

```toml
FieldManual_ProjectRoot = "."
FieldManual_FrameworkRoot = "FieldManual"
```

Relative paths in either file resolve from the project root. The local file
loads after the tracked file and overrides its recognized values.

When maintaining FieldManual itself, both roots are `"."`. In a consuming
project, the framework root must be a strict descendant of the project root,
normally the FieldManual submodule path. The running bootstrap rejects a
configuration that points at a different framework checkout.

See [configuration](docs/configuration.md) for the complete contract.

## Bootstrap

From a typical consuming project whose submodule is `FieldManual/`:

```bash
python FieldManual/bootstrap.py --project-root .
```

For FieldManual itself:

```bash
python bootstrap.py --project-root .
```

Use `--dry-run` to inspect the planned filesystem changes.

The expected layout is declared in
[`FieldManual-layout.toml`](FieldManual-layout.toml). The bootstrap creates
missing directories and skeletons, manages only marked sections of
`AGENTS.md`, and ensures required `.gitignore` entries. Existing project-owned
records are preserved by default.

The bootstrap performs no network, Git, shell-profile, user-home, package,
environment, hook, or validation operations. See
[bootstrap behavior](docs/bootstrap.md) for safety and rerun semantics.

## Repository Map

- [`standards-and-practices/`](standards-and-practices/) contains the
  normative core plus optional language, technology, technique, and guideline
  branches.
- [`knacks/`](knacks/) contains reusable, task-oriented reference material.
- [`templates/`](templates/) contains clean create-only project skeletons.
- `project-management/` is FieldManual's own live state and is distinct from
  the clean templates.
- [`docs/`](docs/) contains framework configuration, bootstrap, and migration
  documentation.
- [`ECRs/`](ECRs/) holds source-owned change requests to other projects.
  Consuming projects receive a ready `FieldManual/` target and a reusable
  `_target-template/` for any other project.

FieldManual's original knowledge-repository guidance remains available as the
optional [knowledge-management profile](knacks/knowledge-management/README.md)
instead of being imposed on every project.

## Project Lifecycle

The default lifecycle is:

1. propose when a meaningful design or policy decision needs review;
2. backlog approved work or direct operator requests;
3. move work into the active record when execution starts;
4. validate in proportion to risk using the project's declared tools;
5. clear completed work with evidence, or defer it without losing the
   original request.

Under-review proposals are not established policy. This is especially
important for imported current work such as the expert review-board proposal.

## Migration From TheKnowledge

FieldManual retains TheKnowledge's strongest documentation and governance
ideas while intentionally excluding its Python environment and automation
platform. The source review, dirty-worktree provenance, selected material,
and exclusions are recorded in the
[migration assessment](docs/migration/theknowledge-assessment-2026-07-23.md).
The later repository-wide [knack
assessment](docs/migration/codebase-knack-assessment-2026-07-23.md) records
the deduplicated review of project-owned and submodule knack trees throughout
the local codebase.
