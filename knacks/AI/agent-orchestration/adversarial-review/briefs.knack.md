# Adversarial Review: Briefs and Schemas

Load this companion to the
[adversarial review overview](overview.knack.md) when you
write the briefs for reviewers, skeptics and fixers, define their output
formats, or code the rule that routes findings between them.

Source review: 2026-10-13. Adapt the schemas to your orchestration tool's
structured-output support; the field names here are illustrative.

## Inputs Every Agent Receives

- the change: a diff, a commit range, or a list of paths;
- the specification or agreed requirement list, verbatim;
- reference material for the host or library, and where to look it up
  (documentation links, reference source, decompiled code);
- the check commands and their latest results;
- the dimension (reviewers), the single finding (skeptics), or the confirmed
  findings (fixers); and
- the output schema, with the instruction that output outside it is an error.

Reviewers and skeptics are read-only. They may run read-only commands and
existing checks, and may write throwaway experiments in a scratch location,
but they change no tracked file. Told also not to build, launch the host or
commit, a review can run alongside another session's test run without
disturbing it.

## Reviewer Brief

```text
You are reviewing <change> for ONE dimension: <dimension>.
Do not report issues outside this dimension. Do not fix anything.
For each finding give: location (file:line or behavior), claim (one
sentence), evidence (quotation, reference link, code path, or reproduction
steps), severity (minor | major | critical, as defined below), proposed fix,
and fast check (the cheapest assertion that would catch this class of
defect).
Severity: critical = data loss, crash, security, or a requirement violated;
major = wrong behavior a user would notice; minor = everything else.
Report "no findings" explicitly if you find none, with what you examined.
```

Questions that keep each dimension focused:

- **Host and API correctness.** For each host call: what does the reference
  say it does, when is it legal to call, which thread or phase owns it, what
  units does it use, and what does it do on failure? Which behavior did the
  author assume rather than check?
- **Side effects.** What other systems read or write the state this change
  touches? What happens on save and load, on undo, when the feature runs
  twice, or when another actor reaches the same object? What does it cost
  per frame or per request at the expected scale?
- **Specification conformance.** For each requirement: where is it met, and
  where is the evidence? Is any requirement met by a reading the operator
  would not recognize? Is any behavior present that no requirement asked
  for?
- **Test rigor.** For each new check: what claim does it prove, can it fail
  (is there sabotage evidence), does it assert its preconditions, and is its
  oracle independent of the code under test? Which claims have no check?

## Finding Schema

```json
{
  "id": "R2-04",
  "dimension": "side-effects",
  "location": "src/settlement/storage.cs:88",
  "claim": "Settlement storage pulls items from the player's base.",
  "evidence": "Top priority, accepts all items; haulers pick top priority.",
  "severity": "major",
  "proposed_fix": "Narrow the filter; exclude it from player hauling.",
  "fast_check": "Smoke: an item dropped in the base stays put for N ticks."
}
```

Deduplicate before verification: two findings with the same location and
the same claim merge, keeping the stronger evidence and the higher severity.

## Skeptic Brief

```text
You are verifying ONE finding. Your job is to REFUTE it if it is wrong.
Finding: <claim, location, evidence>. You are not given the reviewer's
reasoning; examine the code and references yourself.
Try, in order: reproduce it (a failing check, a scripted experiment, or a
direct call into the built host-free library, after confirming the build is
newer than its sources); trace the code path and look for anything that
prevents it; check the cited reference says what the finding claims.
Verdict: confirmed | refuted | inconclusive.
Give the evidence for your verdict. If inconclusive, say what experiment
would settle it. You may change the severity, with a reason.
Do not fix anything. Do not report other issues; list them under "noticed"
in one line each.
```

## Verdict Schema

```json
{
  "finding_id": "R2-04",
  "verdict": "confirmed",
  "evidence": "Scripted run: base item moved to the settlement at tick 410.",
  "severity": "major",
  "settling_experiment": null,
  "noticed": []
}
```

## Routing Rule, in Code

Decide routing with plain code over the structured verdicts, as staged
verification does for escalation. A model asked whether to route a finding
is less predictable than a rule and cannot be audited.

```text
for each verdict:
  if output failed the schema or the skeptic errored:
                                  route to "needs attention"
  elif verdict == "confirmed":    route to fix queue
  elif verdict == "refuted":      record with counter-evidence
  else:                           route to "needs attention"
orchestrator turns the fix queue into decisions (below)
group decisions by file; one fix agent per file group
"noticed" items: record; do not fix in this round
```

A schema failure is never read as a pass, and an inconclusive verdict is
never read as a refutation.

## From Findings to Decisions

Before briefing a fixer, the orchestrator reads the confirmed findings and
writes one decision per item, or per group of duplicates:

```text
D3 (findings R2-04, R4-01): Settlement storage accepts only settlement
   goods and is excluded from player hauling. Overrides R4-01's proposal to
   delete the storage. Fast check: R2-04's.
```

Decisions resolve conflicting proposals, merge duplicates, and record any
deliberate departure from a reviewer's advice. They bind the fixer, which
keeps fixes consistent and makes the fix report checkable item by item.

## Fixer Brief

```text
Implement ONLY these decisions: <list, each citing its findings and the
verdict evidence>. They override the reviewers where they differ.
You own: <paths>. Change no other file (see shared-checkout rules). Do not
edit shared records; list the record changes you would make.
For each decision: make the smallest fix; add its fast check to the
project's checks; prove the check by a sabotage run (break the fixed
behavior, see the check fail, restore); run the affected checks.
If a fix needs a change outside your files, or a decision looks wrong once
you are in the code, stop and report instead of improvising.
Report per decision: commit, check added, sabotage evidence, results; then
"Decided differently" (where and why you departed from a decision) and
"Not verified".
```

After the fixers finish, rerun the gate once. If anything fails, or a fix
changed behavior that no check asserts, report "needs attention" rather than
starting another review loop automatically.

## Final Review Report

The orchestrator's report to the operator states:

- the change reviewed and the dimensions used;
- confirmed findings with their fixes, fast checks and sabotage evidence;
- refuted findings, in one line each with the counter-evidence;
- inconclusive findings and the experiment that would settle each;
- what was not reviewed, such as behavior only a person or real hardware can
  judge; and
- cost and time where a stage ran long.

## Calibration

Track, per dimension and per skeptic configuration:

- **refutation rate**: a skeptic that refutes nothing is not checking, and
  one that refutes everything may be under-informed;
- **confirmed findings later found wrong** during fixing; and
- **escaped defects**: defects found after release that a dimension should
  have caught.

Adjust briefs and dimensions from these numbers, not from impressions.

## Further Information

- Victor R. Basili et al., [The Empirical Investigation of Perspective-Based
  Reading](https://doi.org/10.1007/BF00368702), *Empirical Software
  Engineering* 1(2), 1996: scenario-driven reading per perspective.
- Anthropic, [How we built our multi-agent research
  system](https://www.anthropic.com/engineering/multi-agent-research-system):
  objectives, output formats, tool guidance and boundaries for subagents.
- FieldManual, [Staged Verification for Multi-Agent
  Work](../staged-verification.knack.md): structured gate outputs and a coded
  escalation rule.
- FieldManual, [Proving Checks Can
  Fail](../../../software-engineering/testing/proving-checks/overview.knack.md).
