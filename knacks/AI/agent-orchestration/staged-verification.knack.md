# Staged Verification for Multi-Agent Work

Load this knack when AI agents build a change through a scripted multi-agent
workflow (builders, reviewers, fixers) and you must decide how much
verification the change needs before it lands.

Source review: 2026-09-25. Agent orchestration tools and model capabilities
change quickly; recheck the references and your tool's own documentation
before relying on specific behavior.

## Mental Model

Exhaustive adversarial review finds real defects, but much of its cost can go
to re-proving behavior that cheaper checks already cover. As an illustration
only (one anecdotal run, not a benchmark), a single reviewer agent on a
browser UI spent about half an hour.

- About half went to ad hoc browser sweeps: many window sizes times several
  UI states, a large before/after comparison, and repeated reruns of one suite
  to characterize a known intermittent failure.
- A large share of the rest went to sequential model turns: read a result,
  decide, issue the next command.
- The sweeps were slow because every step waited a fixed interval after a
  resize, a page load or an animated click. Fixed waits multiply across every
  cell of a test matrix.

Measure your own runs before assuming the same split.

Treat verification like a test pyramid with an escalation path:

- **Tier 1, the fast gate, always runs.** Deterministic checks run
  concurrently, and a time-boxed review maps each agreed requirement to
  evidence.
- **Tier 2, the deep review, runs only when the gate gives a reason.** It is an
  adversarial review scoped to the failures and suspicions the gate reported.
- **Plain code decides escalation** from the gate's structured outputs. Do not
  ask a model whether to escalate: a coded rule is predictable, auditable and
  cheap to run.
- **The ratchet.** Where feasible, each defect class the deep review finds
  also becomes a cheap assertion in the project's own checks. The fast gate
  should get stronger over time and escalations should become rarer. Some
  classes, such as visual judgment, hardware behavior and rare races, may stay
  expensive to check. Watch gate runtime as assertions accumulate.

## Operating Pattern

1. **Prepare before orchestrating.** Fix the agreed requirement list and the
   project's declared, non-interactive check commands. Register checks that
   are known to be flaky, with their observed failure rates. If the project
   declares no checks, record the change as high-risk and make adding a first
   check part of the change.
2. **Build.** Use one or more builder agents. Parallel builders must own
   disjoint files, and none of them commits while others are editing. Builders
   run the checks for what they touched, not the full suite on every
   iteration.
3. **Tier 1 gate.** Run two agents in parallel.
   - A *check runner* for mechanical work. It runs every deterministic check
     concurrently, on distinct ports and workspaces. It reruns a registered
     flaky check at most twice. It returns one structured result per check,
     including the number of attempts.
   - A *coverage reviewer*. It marks each requirement `proven` (citing a named
     assertion or a concrete code path), `unproven`, `violated`, or `unclear`
     (the requirement admits more than one reading). It lists suspicions with a
     severity of `minor`, `major` or `critical`. It writes no new sweeps and
     reruns nothing.
4. **Escalation rule, in code.** An `unclear` requirement stops the run: report
   *needs attention* with the competing readings, because deep review cannot
   settle what a requirement means. Otherwise, escalate when any of these
   holds:
   - the gate itself errored: an agent crashed or timed out, its output failed
     the result schema, or a declared check could not run;
   - a non-flaky check failed, or an unregistered check failed at all;
   - a registered flaky check needed more reruns than its recorded rate
     predicts;
   - a requirement is `unproven` or `violated`;
   - a suspicion is anything other than `minor` (unknown severities count as
     serious);
   - the change was declared high-risk before it was built.

   High risk means state machines, contracts between components, security,
   data integrity, a project with no checks, or anything hard to roll back.
5. **Tier 2 deep review, only on escalation.** Start from exactly the gate's
   failures, gaps and suspicions, and widen only as the evidence requires. Each
   finding carries evidence, a proposed fix, and a *fast check*: the cheapest
   assertion that would catch that class of defect next time.
6. **Fix, only when there is something to fix.** Verify each item, then fix it
   or reject it with evidence. Land each fixed finding's fast check in the
   project's checker in the same change.
7. **Regate, after any fix.** Rerun the deterministic checks once, including
   newly landed fast checks, under the same flaky-rerun rule. If anything
   fails, or a fix touched a requirement no check asserts, stop and report
   *needs attention* rather than looping.
8. **Report measured facts.** State what ran, what escalated and why, and
   where the time went when a stage ran long.

A skeleton of the escalation rule:

```text
if any requirement is "unclear": stop with needs-attention
gate_error  = gate agent failed, timed out, returned schema-invalid output,
              or a declared check did not run          # never read as a pass
failed      = checks that did not pass, excluding registered flaky checks
              that recovered within their rerun budget
flake_drift = flaky recoveries above the registry's expected rate
gaps        = requirements that are "unproven" or "violated"
serious     = suspicions whose severity is not "minor"
              # unknown severities count as serious
escalate    = gate_error or high_risk or failed or flake_drift
              or gaps or serious
```

## Sizing and Effort

- Where the tool exposes a reasoning-effort or model-size setting, match it to
  the stage:
  - low for mechanical runners;
  - medium for coverage review;
  - high for deep review and non-trivial fixes.
- Keep the fast tier's matrices small: a few representative sizes and states,
  not the full cross product. Save full matrices for tier 2, high-risk
  changes, and periodic release checkpoints.
- Prefer waiting on explicit conditions over fixed sleeps: a state flag, an
  animation-end event, a known number of completed polls. Fixed sleeps often
  dominate browser-check runtime.
- Keep the flaky-check registry current. Characterize an intermittent failure
  once, then rely on the registry instead of rerunning whole suites every time
  it appears.

## Sharp Edges

- **The gate can miss what only a sweep would find.** Mitigate this with the
  ratchet, honest risk declaration, and an occasional full sweep before
  important checkpoints.
- **"Proven by reading" is weak evidence for timing, layout and concurrency.**
  Require a cited assertion for those.
- **Flake reruns can hide real regressions.** Record every recovery, compare
  it with the registry, and treat drift as a reason to escalate.
- **Free-text verdicts drift.** Use structured output schemas for gate results
  so that the escalation rule reads fields, not prose.
- **Keep reviewing and fixing separate.** A reviewer that fixes as it goes
  produces unauditable findings and races other agents in the same tree.
- **Builders that rerun full checkers many times inflate build time without
  adding assurance.** Leave full passes to the gate.
- **Operator-facing summaries can overstate results.** Report the gate
  verdict, whether it escalated, and anything left unverified, such as
  behavior in a browser or on hardware the automated checks cannot reach.

## Review Checklist

- The requirement list was agreed and passed to the gate verbatim.
- Every declared check runs non-interactively, and flaky checks are
  registered with observed rates.
- The escalation rule is code, and the risk level was declared before the
  build.
- Unclear requirements stopped the run instead of reaching deep review.
- The deep review, if it ran, was scoped to the gate's output, and every
  finding proposes a fast check.
- The ratchet was applied: fixed findings landed with their fast checks.
- The regate passed, or the run reported *needs attention*.
- Long stages have a time breakdown: tool time, model turns, fixed waits.

## Further Information

- FieldManual, [Browser Automation][browser-automation]: harness-versus-product
  evidence and condition-based waits.
- FieldManual, [Test Development and Mock Use][test-development].
- Anthropic, Building effective agents: workflow patterns such as prompt
  chaining, parallelization and evaluator-optimizer loops.
  <https://www.anthropic.com/engineering/building-effective-agents>
- Anthropic, How we built our multi-agent research system: orchestrator and
  sub-agent design, effort scaling, and evaluation.
  <https://www.anthropic.com/engineering/multi-agent-research-system>
- Ham Vocke, The Practical Test Pyramid: why cheap tests should dominate and
  expensive tests should be few.
  <https://martinfowler.com/articles/practical-test-pyramid.html>
- Google Testing Blog, Flaky Tests at Google and How We Mitigate Them: flake
  rates, reruns, and why reruns need tracking.
  <https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html>
- Martin Fowler, Eradicating Non-Determinism in Tests: causes of flakiness,
  and waiting on conditions instead of sleeps.
  <https://martinfowler.com/articles/nonDeterminism.html>
- Google, Site Reliability Engineering, "Testing for Reliability": the
  hierarchy of unit, integration and system tests, and the time and compute
  cost of each.
  <https://sre.google/sre-book/testing-reliability/>

[browser-automation]: ../../UI/browser/browser-automation.knack.md
[test-development]: ../../../standards-and-practices/core/test-development-and-mock-use.md
