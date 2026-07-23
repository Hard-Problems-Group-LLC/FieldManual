# High-Level Debugging

Load this knack when a failure is real but the route from symptom to cause is
unclear. It stays above any particular language, tool, architecture, or
platform and emphasizes evidence, causal isolation, and recoverable
experiments.

## Mental Model

Debugging is structured search under uncertainty, not a sequence of plausible
fixes. The goal is to explain the gap between expected and observed behavior
well enough to:

1. restore correct behavior;
2. identify the smallest useful causal account; and
3. reduce the chance that the failure family returns unnoticed.

AI can generate polished explanations faster than it can discover truth.
Anchor the session in observations, competing hypotheses, and tests that can
disconfirm them.

## Core Loop

### State the Problem Precisely

Record:

- expected behavior;
- observed behavior;
- reproduction conditions, if known;
- relevant state and inputs; and
- changes near the time the failure appeared.

Separate observations from assumptions. A vague report invites narrative
completion instead of diagnosis.

### Reproduce and Stabilize

Make the failure repeat in a controlled setting when possible. Define the
exact condition that counts as the same failure so a changed symptom is not
mistaken for a fix.

Intermittent failures still deserve investigation. Capture timing, state,
environment, and frequency rather than declaring them unreal.

### Reduce the Failure Surface

Minimize the failing input, sequence, state, and environment while preserving
the same failure. A smaller reproducer removes noise, sharpens hypotheses, and
makes evidence easier to share.

### Generate Competing Hypotheses

List several plausible causes. For each, state:

- why it fits existing evidence;
- what else should be true if it is correct; and
- what observation would make it less likely.

This counters both human confirmation bias and model confabulation.

### Run Discriminating Tests

Choose the smallest safe observation that separates leading hypotheses.
Change one meaningful variable at a time when practical. Record negative
results; they narrow the search space and prevent repeated work.

### Separate Diagnosis from Repair

Pause after identifying a likely cause. Ask:

- what minimal change addresses that cause;
- what nearby behavior shares the same risk;
- how the change could fail; and
- what result would show that only the symptom was hidden.

### Validate Broadly

Confirm that:

- the original failure is gone;
- the minimized case now behaves correctly;
- related success and failure paths still work;
- no new bad state replaced the old one; and
- the causal explanation agrees with the observed repair.

## Working Effectively with AI

- Provide primary artifacts—exact failures, captured output, reproductions,
  and dated notes—rather than only a narrative summary.
- Ask for an explanation of observations before asking for a rewrite.
- Ask hypotheses to predict additional observations.
- Use AI to propose reductions, boundary cases, and cheap experiments.
- Keep a case log during long investigations.
- Preserve disconfirming evidence and failed attempts.
- Ask what adjacent behavior could fail for the same reason.

## Anti-Patterns

- Shotgun debugging: several speculative changes at once.
- Treating a nearby change or timing correlation as proof of causation.
- Letting a model "self-correct" repeatedly without new external evidence.
- Rewriting large areas after every failed attempt.
- Adding instrumentation without considering how observation changes timing
  or state.
- Suppressing symptoms with retries, guards, or broad exception handling
  before understanding the cause.
- Hiding uncertainty instead of designing the next test.

## Case Questions

- Which statements are observations, and which are assumptions?
- What is the smallest reproducer that fails for the same reason?
- Which two hypotheses are most useful to separate next?
- What result would falsify the leading theory?
- If the proposed repair works, what else should become true?
- If it fails, what new information will the result provide?

## Further Information

- Google SRE, "Effective Troubleshooting":
  <https://sre.google/sre-book/effective-troubleshooting/>
- The Debugging Book, "Reducing Failure-Inducing Inputs":
  <https://www.debuggingbook.org/html/DeltaDebugger.html>
- NIST, "Root Cause Analysis":
  <https://csrc.nist.gov/glossary/term/root_cause_analysis>
- OpenReview, "Teaching Large Language Models to Self-Debug":
  <https://openreview.net/forum?id=KuPixIqPiq>
- OpenReview, "Large Language Models Cannot Self-Correct Reasoning Yet":
  <https://openreview.net/forum?id=IkmD3fKBPQ>
- Google SRE, example postmortem:
  <https://sre.google/sre-book/example-postmortem/>
