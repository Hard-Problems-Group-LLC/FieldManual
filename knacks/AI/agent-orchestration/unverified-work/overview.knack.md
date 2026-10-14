# Integrating Unverified Agent Work

Load this knack when code, tests, documentation or assets arrive from an AI
agent that could not build or run what it produced: a cloud coding agent in
a container without the project's toolchain, a chat assistant that returned
files, or any agent whose environment lacked the host application the code
targets. Load it too when deciding how to merge such work with a line of
development that was verified locally. Companions:

- [Review](review.knack.md): the
  failure signatures to look for and how to check each one.
- [Integration](integration.knack.md):
  the merge gate, reconciling the agent's history with a verified line, and
  what to keep.
- [Agent instructions](instructions.knack.md):
  what to tell such an agent so that its work arrives honest and easy to
  verify.

Source review: 2026-10-13. Agent products, their sandboxes and their
defaults change quickly; check the product's current documentation, such as
the [OpenAI knacks](../../OpenAI/README.md) for Codex surfaces.

## Mental Model

An agent that cannot compile, test or run its output still produces output
that looks finished. The code is idiomatic, the tests are plausible, the
pull request says what was done, and nothing in the text distinguishes
verified from unverified. Treat the whole delivery as a draft written from
memory.

Hosted coding agents typically work in an isolated environment prepared by
setup scripts. Whatever the scripts do not install, such as a proprietary
host application, a licensed SDK, or the host's own assemblies, does not
exist for the agent. In one project an agent's container lacked the
language SDK altogether; its "rebuild" of the project had never compiled
when it was first built on a real machine.

The failures follow a pattern. In one plugin project, work produced this way
showed:

- **near-miss APIs**: plausible names one character, word or version away
  from the real ones, and parameters that do not exist;
- **placeholders presented as code**: "see previous message for the full
  code (truncated for brevity)" inside a file shipped as complete;
- **tests that pin defects**: snapshot tests asserting the current,
  invalid data values, which turned the bugs into requirements;
- **claims without evidence**: an audit stating that "no build adjustments
  are required" while the build was broken, and a decision log dated more
  than a year before the commit that added it;
- **rules applied where they do not belong**: a prose line-length rule
  wrapped identifiers mid-token, broke build-file values, and inserted line
  breaks into user-facing text; a formatting pass re-serialized structured
  files and dropped a byte-order mark;
- **invented environment facts**: an install folder the host never reads,
  and the wrong target version; and
- **merge churn**: one branch and one pull request per task, each merged
  13 to 23 seconds after its commit with no build, six of seven touching
  only documentation or process.

Research on code models supports the first signature in general terms:
models hallucinate package names at measurable rates, and their accuracy
falls for rarely used APIs, which is where a niche host's plugin interface
sits.

Not everything was waste. The same agent's scaffolding, an agent
instruction file, a set of record files, a host-free core library and a
test project, was worth keeping. Its behavior was not. **Salvage process
and structure; re-derive behavior.**

## Operating Pattern

1. **Quarantine.** Treat the delivery as unverified until it builds on the
   real toolchain. Do not merge it into the line you trust.
2. **Build it where it can build.** Check it out in a separate worktree on a
   machine with the real toolchain and host, and build it before reading
   the logic. The compiler finds near-miss APIs faster than review does.
3. **Scan for the signatures** in the [review
   companion](review.knack.md):
   placeholders, near-misses, pinned defects, fabricated facts, misapplied
   formatting.
4. **Validate data against the real schema** before trusting any test that
   snapshots it.
5. **Prove the tests can fail**, as [Proving Checks Can
   Fail](../../../software-engineering/testing/proving-checks/overview.knack.md)
   describes. Tests written without running them are the most likely to be
   vacuous or to pin the wrong value.
6. **Decide per artifact**: keep, rewrite, or drop. Keep structure and
   process that are sound; rewrite behavior against the real host.
7. **Reconcile histories** so that provenance survives and the verified line
   wins where they conflict (see the [integration
   companion](integration.knack.md)).
8. **Gate future merges** on "it builds and runs more than zero tests" on
   the real toolchain.
9. **Fix the instructions** so the next delivery reports what it could not
   run (see the [instructions
   companion](instructions.knack.md)).

## Sharp Edges

- **Fluency is not evidence.** The best-written file can be the one that
  never compiled.
- **Green can mean zero.** A misconfigured test project can report success
  while discovering no tests, or, depending on the toolchain version, abort
  instead. Count what ran, and assert a known minimum.
- **Snapshot tests entrench.** A test that pins the current value pins the
  current bug unless the value was first checked against the real schema.
- **Formatting diffs hide changes.** A pull request described as "wrap
  lines" or "reformat" can change identifiers, values and file encodings.
  Build after every formatting change.
- **Merged is not built.** A branch that says "merged" may never have
  compiled anywhere. Build it before relying on it.
- **Dates and citations can be invented.** Check logged dates against
  commit dates, and replace proxy or reader-service links with the canonical
  source.
- **Copies drift.** Generated archives, downloads and unpacked folders of
  "the same" version can differ; one may hold placeholders where another
  holds code. Checksum every copy, and rebuild from the last complete one
  rather than regenerating.

## Review Checklist

- The delivery was built on the real toolchain, in its own worktree, before
  its logic was reviewed.
- No placeholder, elision marker or one-line stub remains.
- Every external API it calls exists, with that signature, in the version
  the project targets.
- Every value a test pins was checked against the real schema.
- Each new test was seen to fail, and the suite ran more than zero tests.
- Dates, versions, install locations and citations were checked against
  primary sources.
- Structured files kept their encoding, quoting and byte-order marks.
- Kept, rewritten and dropped artifacts are recorded with reasons.
- The agent's instructions were updated to prevent the next occurrence.

## Further Information

- Joseph Spracklen et al., [We Have a Package for You! A Comprehensive
  Analysis of Package Hallucinations by Code Generating
  LLMs](https://arxiv.org/abs/2406.10279), USENIX Security 2025.
- Nihal Jain et al., [On Mitigating Code LLM Hallucinations with API
  Documentation](https://arxiv.org/abs/2407.09726), 2024: accuracy falls for
  low-frequency APIs.
- OpenAI, [Codex cloud](https://learn.chatgpt.com/docs/cloud) and
  [Sandboxing](https://learn.chatgpt.com/docs/sandboxing): isolated task
  environments, setup scripts, sandbox modes and approval policies.
- FieldManual, [Proving Checks Can
  Fail](../../../software-engineering/testing/proving-checks/overview.knack.md)
  and [Adversarial Review With
  Skeptics](../adversarial-review/overview.knack.md).
