# Integrating Unverified Agent Work: Agent Instructions

Load this companion to the
[overview](overview.knack.md) when you
write or revise the instruction file (such as `AGENTS.md`) for an agent
that works without the project's real toolchain, or when you set up how
such an agent is run.

Source review: 2026-10-13. Product settings named here are examples; check
the product's current documentation, such as the
[OpenAI knacks](../../OpenAI/README.md) and OpenAI's
[sandboxing documentation](https://learn.chatgpt.com/docs/sandboxing) for
Codex.

## Principles

The instructions cannot give the agent a toolchain it lacks. They can make
its output honest about that, and cheap to verify:

- say what was and was not executed;
- never present partial work as complete;
- take names and facts from references, not memory;
- keep rules inside the scope they were written for; and
- leave merging to a gate the agent cannot satisfy by assertion.

## A Template

```text
## Working Without the Toolchain
Your environment cannot build this project or run its host. Therefore:
- Report every build, test and run as "not run" unless you ran it and
  quote its output. Never write "tests pass" without output.
- End every report with "Not verified": everything a build, a test run or
  a person must still check.
- Never elide code. No "for brevity", "rest unchanged" or "see previous
  message". Deliver whole files, or say which parts are missing.

## Interfaces and Data
- Use only host APIs found in <reference source / decompile / docs path>.
  List every external API you used in the report. If you cannot confirm a
  name, leave a TODO naming the question; do not guess.
- Data values must be valid in the host's schema (<schema path>). Cite the
  schema for every value a test asserts. Do not snapshot current values as
  requirements unless the test is labeled a characterization test.

## Scope of Rules
- The line-length rule applies to prose. For code, use the formatter
  (<command>). Never wrap identifiers, structured files (XML, JSON, project
  and solution files) or user-facing strings.
- Preserve encodings, byte-order marks, line endings and quote styles.

## Facts
- Dates come from the clock or from git, never from memory.
- Target version: <version>. Install location: <path rule>. Do not
  change either without a cited source.
- Cite canonical URLs, not proxies or caches.
- Asset briefs derive from the code's actual asset paths and
  <art-direction document>.

## Changes
- Batch related tasks into one reviewable change. Do not merge your own
  pull requests; merges require the build-and-test gate.

## Tool Reliability
- If a tool fails, use the fallback below and record the failure here.
  <tool>: <failure>, <date>; fallback: <method>.
```

Fill the placeholders with project facts. Keep the file short enough that
the agent reads all of it.

## Why Each Line Is There

- **"Not run" reporting.** An agent that cannot run tests still tends to
  describe them as passing. One project's instruction file had to state
  that the container lacked the language SDK and that test execution must
  be reported as "not run".
- **No elisions.** Generated files have shipped with "truncated for
  brevity" in place of code, and data files referring to classes that
  existed only in the elided part.
- **Interfaces from references.** Near-miss names compile nowhere. A list of
  the external APIs used turns review into a lookup.
- **Schema-checked values.** Tests that snapshot invalid values entrench
  the bugs they should catch.
- **Rule scope.** A width rule meant for prose, applied everywhere, has
  split identifiers, broken build files and put literal line breaks into
  user-facing text.
- **Facts from sources.** Dates, versions and install locations from memory
  have been wrong: a decision-log entry dated more than a year before its
  commit, a target version one release behind, and an install folder the
  host never reads.
- **Batching and no self-merge.** Per-task requests merged within seconds
  bypass every check.
- **Tool reliability record.** When a tool fails in the agent's sandbox (in
  one case a patch tool failed in a nested sandbox), demote it after one
  failure, use a fallback such as editing named files and reviewing with
  `git diff`, and record the fact so later sessions do not rediscover it.

## Running the Agent

Environment choices made outside the instruction file matter as much as
the file:

- **Approval policy.** A policy that never asks can also never escalate. In
  one setup a no-approval policy blocked the escalations needed to write
  git's index and refs and to push, because the sandbox exposed the
  repository's `.git` directory read-only; a policy that asks when leaving
  the sandbox worked. Check how your product's sandbox treats version
  control before choosing.
- **Run the pinned binary.** Start the agent from its installed, pinned
  executable. A package runner such as `npx` installs missing packages from
  the registry into its cache, so a missing local install can resolve to an
  unrelated package that shares the name.
- **Smoke-test startup, not the version string.** A `--version` command can
  skip the start-up path that fails. Test an offline start-up command in a
  fresh, empty home directory.
- **Protect the agent's home.** Its sessions, memories and credentials are
  state, not cache. Exclude them from cleanup scripts, back them up before
  repairs, and check login status after reinstalling.
- **Repair through the managed path.** An emergency install run from the
  repository root leaves package manifests and dependency folders behind.
  Repair through the managed installer, then remove only those emergency
  artifacts.

## Review Checklist

- The instruction file says what the environment cannot do and requires
  "not run" and "Not verified" reporting.
- Elisions are forbidden in writing.
- Reference locations for APIs and the data schema are named.
- Formatting rules state their scope; structured files and user-facing
  strings are exempt.
- Target version, install rules and the art-direction source are stated.
- The agent cannot merge its own work; the gate is enforced elsewhere.
- Tool failures are recorded with fallbacks.
- The agent runs from a pinned binary with an approval policy that can
  escalate.

## Further Information

- OpenAI, [Sandboxing](https://learn.chatgpt.com/docs/sandboxing) and
  [Codex cloud](https://learn.chatgpt.com/docs/cloud): sandbox modes,
  approval policies and task environments.
- npm, [npx](https://docs.npmjs.com/cli/v11/commands/npx): installing
  missing packages from the registry.
- FieldManual, [Shared-Checkout Subagents: Briefs and
  Records](../shared-checkout/briefs.knack.md):
  brief structure and report fields.
- FieldManual, [Proving Checks Can
  Fail](../../../software-engineering/testing/proving-checks/overview.knack.md).
