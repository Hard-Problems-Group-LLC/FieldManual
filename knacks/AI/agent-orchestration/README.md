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

For a product's own control surfaces and APIs, see the product topics in
the [AI knacks index](../README.md). A consuming project owns its
requirement lists, check commands, flaky-check registry, risk
classification, and escalation thresholds.
