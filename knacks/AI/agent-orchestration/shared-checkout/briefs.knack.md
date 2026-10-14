# Shared-Checkout Subagents: Briefs and Records

Load this companion to the
[shared-checkout overview](overview.knack.md) when you
write the brief for a background agent, split work between parallel agents,
read their final reports, or resume after an interruption.

Source review: 2026-10-13. Agent tools differ in how they start background
agents, return results and survive restarts; check your tool's documentation.

## What Every Brief Contains

A background agent knows only what its brief says and what it finds on disk.
Anthropic's account of its research system puts the minimum as "an objective,
an output format, guidance on the tools and sources to use, and clear task
boundaries", and reports that vague briefs led agents to duplicate work and
leave gaps. In a shared checkout the boundaries must be concrete:

- **Objective**: the outcome, with the acceptance checks that prove it.
- **Read first**: the specification, the decision log, and the documents
  that govern the area, so that the agent does not rediscover settled
  questions.
- **Commands**: the exact build, validation, unit-test and integration-test
  commands, and the evidence expected from each, including proof that new
  checks can fail.
- **Owned files**: the exact paths the agent may create or change.
- **Read-only files**: everything else it needs to read, including the
  interface it builds against.
- **Forbidden commands**: named, not implied (see the sweep table in the
  [Git patterns](git.knack.md) companion).
- **Where to build and test**: the shared tree, its own worktree, or nowhere
  (edits only, with the orchestrator building).
- **Commit cadence**: commit and push after each sub-step, by path, with a
  stated message style.
- **Shared records**: do not edit them; propose entries in the report.
- **Final report format**: the fields listed below.

A template:

```text
Objective: <outcome>. Done when <checks> pass.
Read first: <spec>, <decision log>, <area docs>.
Commands: build <cmd>; validate <cmd>; unit tests <cmd>; smoke <cmd>.
  Prove each new check can fail (sabotage run) and report the evidence.
You own: <path>, <path>. Create or change no other file.
Read only: <interface file>, <spec>, <neighboring code>.
Never run: git commit -a, git add -A, git add ., git stash, git restore .,
  git checkout -- ., git reset --hard, git clean, git switch, force pushes,
  tree-wide formatters.
Build and test in: <worktree path | shared tree, only these commands>.
After each sub-step that builds and passes its checks: git add -- <new
  files>; git commit -m "<area>: <what>" -- <your paths>; fetch; integrate
  only if the tree is clean; push. If you cannot push, say so in the report.
Do not edit <TODO, decision log, changelog>. Propose entries instead.
Final report: changed paths and commit ids; checks run and results; Not
  verified; Decided differently (and why); proposed record entries; open
  questions; hazards.
```

State the whole task in the brief, even when the operator has just
described it. Some orchestration harnesses forward the operator's most
recent message to every agent as its authoritative request, even when that
message concerned something else; a self-contained brief keeps an unrelated
aside from steering the agent.

Triage every intermittent failure an agent reports rather than filing it as
noise, and when an agent works in an area with known flakes, consider
asking it to investigate them as a side task. In one case an agent asked to
look at three flakes near its feature found two kinds of test noise and one
real bug, which ordinary use would also have hit, and fixed all three.

## Partitioning Work

Split by file before splitting by idea. Two agents that "work on different
features" but both need the central registration file will collide there.
List each agent's files, look for overlaps, and resolve every overlap before
starting:

- give the contested file to one agent and let the other propose its change
  in its report;
- move the shared part into a contract committed first (below); or
- run the two agents one after the other.

Tree-wide side effects count as files. A build that regenerates project
files, a formatter, or a lock-file update writes to paths no brief listed.
Assign them to one owner or keep them out of the parallel phase.

Ownership holds for the orchestrator too. A decision reached while an agent
is still running, which touches that agent's files, waits for the agent to
finish, or goes into the next agent's brief. Patching a file a running agent
owns creates exactly the collision the partition was meant to prevent.

## Contract-First Parallel Work

When two agents meet at an interface, say a host-free routing library and the
host-side adapter that calls it, freeze the interface before either starts:

1. **Write the contract.** Shared types, function signatures, and the
   behavior each promises: units, error cases, ownership of returned objects.
2. **Commit it as stubs.** The stubs must compile and must fail loudly when
   called, so that nothing passes against an unimplemented body.
3. **Push the stub commit.** Both agents start from it.
4. **Fill both sides at once.** The library agent implements and unit tests
   the stubs. The host agent writes the adapter against the signatures and
   tests what it can with small fakes that honor the documented behavior.
5. **Route contract changes through the orchestrator.** A needed change
   becomes a new stub commit that both agents pull. Neither edits the
   contract file on its own. A workable rule for both agents: never rename,
   remove or change the signature of an existing public member; adding
   members is allowed and must be reported.
6. **Merge and run the integrated checks.** Replace the host agent's fakes
   with the real library and run the end-to-end checks. Expect the
   integration to find mismatches in documented behavior, not in signatures.

Give both agents' report schemas two extra fields: **contract deviations**
(where the agent had to depart from the contract) and **contract needs**
(what the contract lacks). In one run, a host-free planning library and its
host-side caller were built in parallel against stubs that threw "not
implemented". Both agents independently reported the same flaw through
these fields: a distance rule measured from a bounding box made every
candidate site fail. A flaw seen from both sides of an interface is
usually in the contract itself.

The stub commit also serves as the record of what was agreed, which helps
when a session is interrupted halfway.

## Commit Cadence and Durability

Have agents commit and push after every sub-step, not at the end. A session
can end without warning. When a forced operating-system restart once ended a
long session mid-agent, every pushed sub-step survived and the unpushed work
in progress had to be redone.

- A sub-step is the smallest change that builds and passes its own checks.
- Each commit message names the area and the behavior, so the history reads
  as a progress log when the reports are lost.
- Push sub-steps to the feature branch. A shared integration branch should
  receive only states that work, not commits that sit on top of stubs.
- An agent that cannot push (diverged remote, dirty tree, no credentials)
  commits locally and says so in its report; the orchestrator integrates.

For planning, one project's single-agent steps, from a review-fix pass to
a feature step, each took between 19 and 76 minutes, roughly 100 to 300
tool calls, and 0.35 to 0.8 million tokens. Steps of that length are long
enough for an interruption to matter.

## Final Reports

The final report is the record of the agent's work. The orchestrator's
context, and often the operator's attention, holds only what the report says.
Ask for:

- **Changes**: paths and commit identifiers.
- **Verification**: the commands run and their results, including any
  sabotage runs that proved new checks can fail (see
  [Proving Checks Can Fail](../../../software-engineering/testing/proving-checks/overview.knack.md)).
- **Not verified**: what the agent could not check, and why. Visual results
  in a host the agent cannot see belong here.
- **Decided differently**: where the agent departed from its brief, and why.
- **Proposed record entries**: TODO items, decisions, known issues.
- **Open questions** for the operator, each with a proposed answer the
  agent acted on (see below).
- **Hazards**: anything the next writer must know, such as a file left
  mid-edit, a stash, or a failing check.

Ask for compact reports with these headings. Very large reports, around
50 KB in one session, may arrive as a pointer to a saved file instead of
inline text, which the orchestrator must then remember to read.

**Deciding asynchronously.** An agent that stops at every open question
stalls the work while the operator is away. Have it record each question
with a proposed answer that "stands unless changed", proceed on that
answer, and list it in the report. Record interpretations of ambiguous
instructions in the decision log, so the operator can overturn them later.
Settle a feature's specification before its code grows past groundwork,
when changing course is still cheap.

On receipt, the orchestrator:

1. checks the key claims against the history (`git log`, `git show --stat`)
   and, where cheap, reruns the checks;
2. relays the essentials to the operator: what landed, what is unverified,
   what needs a decision. The "not verified" and risk lists deserve the
   closest reading: in one project a risk an implementing agent listed in
   its last line became the most serious finding of the later review;
3. writes the proposed record entries at a quiet point, as the single writer
   of shared records; and
4. treats a missing report as unverified work, never as success.

## Shared Records

Decision logs, TODO lists, known-issue lists, changelogs and indexes are
edited by many hands and read by every future session. They need stricter
handling than code:

- one writer at a time, normally the orchestrator;
- re-read immediately before editing, because the copy in the writer's
  context may be stale;
- committed only when no other agent is writing, because a path commit of a
  record would take any in-flight edit with it;
- entries written from the agents' reports, with the commit or report that
  supports each one;
- merge conflicts in append-only logs resolved by keeping both sides, in
  date order; and
- integrated promptly, because a stale record misleads the next
  reorientation.

## Reorientation After an Interruption

After a restart, a context compaction, or a handoff to a new session:

1. **Read the record.** Decision log, TODO list, the last relayed reports and
   any handoff note. These say what was intended.
2. **Check the repository.** Branch, status, divergence from the remote,
   recent commits, worktrees and stashes (commands in the
   [Git patterns](git.knack.md) companion).
   These say what actually happened.
3. **Reconcile.** Mark each in-flight sub-step as landed, lost, or partly
   present in the tree. Partly present work belongs to an agent that may no
   longer exist; decide explicitly whether to finish, commit, or discard it.
4. **Rebuild and test.** Do not continue from an unverified state. A pass
   here is the new baseline; a failure is the first thing to fix.
5. **Re-brief.** Restart lost agents from the reconciled state with fresh
   briefs; do not assume they remember anything.

FieldManual's
[Session and Project Boundaries](../../../../standards-and-practices/core/session-and-project-boundaries.md)
standard gives the general reorientation checks; this procedure applies them
to a fleet of agents.

## Review Checklist

- Every brief lists owned files, read-only files, forbidden commands, build
  location, commit cadence and report format.
- File lists were checked for overlaps, including generated files.
- Interfaces between parallel agents were committed as failing stubs first,
  and contract changes went through the orchestrator.
- Each sub-step was committed by path and pushed, or the report says why not.
- Every final report was checked against the history and relayed.
- Shared records had one writer and were committed at a quiet point.
- After an interruption, record and repository were reconciled, and the
  build and tests passed before work resumed.

## Further Information

- Anthropic, [How we built our multi-agent research
  system](https://www.anthropic.com/engineering/multi-agent-research-system):
  task descriptions, persistent outputs, and resuming after errors.
- Anthropic, [Building effective
  agents](https://www.anthropic.com/engineering/building-effective-agents):
  the orchestrator-workers pattern.
- FieldManual, [Staged Verification for Multi-Agent
  Work](../staged-verification.knack.md).
- FieldManual, [Test Development and Mock
  Use](../../../../standards-and-practices/core/test-development-and-mock-use.md):
  small fakes with documented behavior, and real-path coverage.
- FieldManual, [Agent Shells on
  Windows](../../../windows/shells/overview.knack.md):
  shell pitfalls worth naming in briefs, such as writing a script to a file
  rather than passing a long one inline.
