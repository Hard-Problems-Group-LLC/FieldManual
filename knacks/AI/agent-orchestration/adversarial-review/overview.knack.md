# Adversarial Review With Skeptics

Load this knack when a change needs a deep review: it is high-risk, a
[staged verification](../staged-verification.knack.md) gate escalated it, or
it was built by agents and has not been examined by anyone who did not write
it. Load it as well when a design or research question needs several
independent perspectives before a decision. Companions:

- [Briefs and schemas](briefs.knack.md): reviewer
  dimensions, skeptic and fixer briefs, finding and verdict formats, and the
  routing rule.
- [Research and concept workflows](research.knack.md):
  parallel researchers, independent concept proposals, and a judge that
  scores and merges.

Source review: 2026-10-13. Model behavior and agent tooling change quickly;
measure your own false-positive and refutation rates instead of assuming
these.

## Mental Model

A single generalist reviewer, human or model, finds some defects and misses
others, and a model reviewer also produces confident findings that are wrong:
a misremembered API, a misread branch, a requirement it invented. Two
well-studied ideas address both problems.

- **Perspectives.** Fagan's inspections gave participants defined roles, and
  Basili and colleagues' perspective-based reading had each reviewer read
  from one viewpoint, such as tester, designer or user, on the premise that
  combined perspectives cover more defects than repeated general reading.
  Give each reviewer one dimension.
- **Verification before action.** Treat every finding as a claim and give it
  to a separate skeptic whose job is to refute it. Only findings that survive
  go to a fixer.

The pipeline:

```text
change ──► reviewers, one dimension each (parallel)
              │ findings: claim, location, evidence, severity, fast check
              ▼
           skeptics, one per finding (parallel), told to refute
              │ verdicts: confirmed | refuted | inconclusive, with evidence
              ▼
           routing rule in code: confirmed → fix queue; others → record
              ▼
           orchestrator: confirmed findings → binding decisions
              ▼
           fix agent(s), one per contested file ──► regate
```

Finding, verifying and fixing stay separate. A reviewer that fixes as it goes
produces findings no one can audit, and it races other agents in the same
tree.

## Review Dimensions

Choose dimensions that match the change's risks. These four served well in
reviewing a plugin for a closed host application:

1. **Host and API correctness.** Is every call to the host, library or
   engine used as that system actually behaves? Check documentation,
   reference source or decompiled code, not memory. Look for lifecycle
   rules, threading, units, and calls that are legal but do something other
   than their name suggests.
2. **Side effects on the wider system.** What else changes when this runs:
   other subsystems, saved data, shared resources, other actors' behavior,
   performance? This reviewer reads outward from the change.
3. **Conformance to the specification.** Is each requirement met as written,
   with no silent reinterpretation, and is any deviation recorded?
4. **Test rigor.** Can each new check fail? Do the checks cover the claims?
   This reviewer applies [Proving Checks Can
   Fail](../../../software-engineering/testing/proving-checks/overview.knack.md)
   and asks for sabotage evidence.

Add security, data integrity, concurrency, accessibility or user experience
when the change warrants them. Keep each brief to one dimension: a reviewer
asked to cover everything drifts back to generalist reading.

In one review of a feature that generated a small settlement inside a host
world, four dimension reviewers, each followed by a skeptic, raised 21
findings; the skeptics confirmed 19 and refuted 2, and several confirmed
findings were duplicates across dimensions. The existing tests had caught
none of the confirmed defects, which included a storage area in the
settlement that pulled in the player's own supplies, residents who could
starve within days, and site clearing that touched the whole bounding
rectangle rather than only the occupied parts. The storage problem had
already been listed as a risk in the implementing agent's report; read the
builders' "not verified" and risk lists before choosing where reviewers
look.

## Skeptics

A skeptic receives one finding, its cited evidence, and access to the code
and references. Its instruction is to refute the claim: reproduce it, find
the code path that prevents it, or show that the cited documentation says
otherwise. It returns one of three verdicts:

- **confirmed**, with the evidence that convinced it, ideally a reproduction
  or a failing check;
- **refuted**, with the counter-evidence; or
- **inconclusive**, with what would settle it.

Route only confirmed findings to the fix queue. Record refuted findings with
their counter-evidence, so the same false claim is not raised again. Put
inconclusive findings in front of a person, or give them a targeted
experiment.

Skeptics fail in a predictable way: they agree. Counter this by asking for
refutation explicitly, by giving them the claim and evidence but not the
reviewer's full reasoning, and by tracking how often they refute. A skeptic
that never refutes is not checking.

Keep decision logic in a library that does not need the host, and skeptics
can settle disputes with numbers instead of argument. Read-only verifiers,
forbidden to build, have loaded an already-built pure library into a
scripting shell and called it directly to measure a generated layout
exactly, after checking that the library was newer than every source file.

Pipeline the stages: start each finding's skeptic as soon as its reviewer
finishes, rather than waiting for every reviewer.

## Fixing

Before fixing, the orchestrator turns confirmed findings into decisions.
Reviewers' proposed fixes can conflict, and some findings are better
settled another way. A short list of binding decisions, which override the
reviewers where they differ, gives the fixer one instruction per item. In
one review, 19 confirmed findings became 11 decisions, and a single fixer
completed them in under 20 minutes, reporting per item and listing where it
had decided differently and why.

Fix agents receive the decisions grouped by file, with one agent per
contested file (see [Shared-Checkout
Subagents](../shared-checkout/overview.knack.md)).
Each fix lands with the finding's fast check, proved by a sabotage run, so
that the class of defect is caught cheaply next time: the ratchet from
staged verification. Then regate.

## Research Workflows

The same separation helps before code exists. Parallel researchers each take
one axis of a question. Several proposers then draft complete concepts from
different angles without seeing each other's drafts. A judge scores the
concepts against a rubric fixed in advance and merges the strongest
elements. The
[research companion](research.knack.md) gives the
details.

## Sharp Edges

- **Cost.** Anthropic reports that multi-agent systems use about fifteen
  times the tokens of a chat. For scale, the eight-agent review above took
  about 33 minutes and 1.85 million tokens. Reserve the full pipeline for
  escalations and high-risk changes.
- **Duplicates.** Dimensions overlap. Deduplicate by location and claim
  before verification, keeping the strongest evidence.
- **Severity inflation.** Reviewers rewarded for findings find more. Define
  severities in the brief and let the skeptic adjust them.
- **Scope creep.** A deep review of a change is not an audit of the code
  base. Tie each finding to the change or to behavior the change relies on.
- **Unverifiable evidence.** "The documentation says" without a link or a
  quotation is not evidence. Require a citation, a file and line, or a
  reproduction.
- **Judge bias.** Model judges show position, verbosity and self-enhancement
  biases. Randomize order, score each item before comparing, and avoid
  judging a model's output with the same model and prompt that produced it
  where you can.
- **Silent fixes.** A fixer that changes behavior beyond its finding needs
  review too. Keep fixes scoped to confirmed findings.

## Review Checklist

- Dimensions were chosen for the change's risks, one per reviewer.
- Every finding carries location, evidence, severity, a proposed fix and a
  fast check.
- Every finding went to a skeptic told to refute it.
- Only confirmed findings reached a fixer, as binding decisions; refuted
  ones were recorded with counter-evidence.
- Fixes landed with sabotage-proved fast checks, and the gate was rerun.
- The report states what was reviewed, confirmed, refuted, left
  inconclusive, and left unreviewed.

## Further Information

- M. E. Fagan, [Design and Code Inspections to Reduce Errors in Program
  Development](https://doi.org/10.1147/sj.153.0182), *IBM Systems Journal*
  15(3), 1976: structured review with defined roles.
- Victor R. Basili et al., [The Empirical Investigation of Perspective-Based
  Reading](https://doi.org/10.1007/BF00368702), *Empirical Software
  Engineering* 1(2), 1996.
- Anthropic, [Building effective
  agents](https://www.anthropic.com/engineering/building-effective-agents):
  parallelization by sectioning and voting, including several prompts
  reviewing code for vulnerabilities.
- Anthropic, [How we built our multi-agent research
  system](https://www.anthropic.com/engineering/multi-agent-research-system):
  token cost, task descriptions, and rubric-based model judges.
- Lianmin Zheng et al., [Judging LLM-as-a-Judge with MT-Bench and Chatbot
  Arena](https://arxiv.org/abs/2306.05685), NeurIPS 2023 Datasets and
  Benchmarks: position, verbosity and self-enhancement biases.
- FieldManual, [Staged Verification for Multi-Agent
  Work](../staged-verification.knack.md): when deep review runs, and the
  ratchet.
