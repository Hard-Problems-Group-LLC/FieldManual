# Agent Orchestration Knacks

This area covers product-neutral patterns for orchestrating AI agents,
such as builders, reviewers, and fixers, that work together on a change.
It does not cover any one product's API. Orchestration tools and model
capabilities change quickly, so each knack states its source-review date.

## Contents

- [Staged Verification for Multi-Agent Work](staged-verification.knack.md) —
  a fast gate that always runs, a deep adversarial review only on
  escalation, and a ratchet that turns each found defect class into a
  cheap check
- [Shared-Checkout Subagents](shared-checkout/overview.knack.md) —
  background agents in one working tree: file ownership, commits by path,
  shared records, worktrees for builds, contract-first parallel work, and
  recovery after interruption
  - [Git patterns](shared-checkout/git.knack.md)
  - [Briefs and records](shared-checkout/briefs.knack.md)
- [Adversarial Review With Skeptics](adversarial-review/overview.knack.md) —
  one-dimension reviewers, skeptics that try to refute each finding, fixes
  only for confirmed findings, and research-and-judge workflows
  - [Briefs and schemas](adversarial-review/briefs.knack.md)
  - [Research and concept workflows](adversarial-review/research.knack.md)
- [Integrating Unverified Agent Work](unverified-work/overview.knack.md) —
  reviewing and merging work from agents that could not build or run it:
  near-miss APIs, pinned defects, a build-and-test merge gate, reconciling
  histories, and instructions for such agents
  - [Review](unverified-work/review.knack.md)
  - [Integration](unverified-work/integration.knack.md)
  - [Agent instructions](unverified-work/instructions.knack.md)

Agent briefs and reviews also enforce
[Proving Checks Can Fail](../../software-engineering/testing/proving-checks/overview.knack.md),
which lives with the testing knacks.

For a product's own control surfaces and APIs, see the product topics in
the [AI knacks index](../README.md). A consuming project owns its
requirement lists, check commands, flaky-check registry, risk
classification, and escalation thresholds.
