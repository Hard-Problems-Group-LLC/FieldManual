# Adversarial Review: Research and Concept Workflows

Load this companion to the
[adversarial review overview](overview.knack.md) when a
question must be researched and a design chosen before building: a new
feature for a host you know only partly, a choice between architectures, or
a concept that must satisfy several stakeholders at once.

Source review: 2026-10-13. The research on model judges and sampling is
recent and moving; recheck it before relying on specific effect sizes.

## Shape of the Workflow

```text
question ──► researchers, one axis each (parallel)
                │ research pack: findings with sources and confidence
                ▼
             proposers, one angle each (parallel, independent)
                │ complete concepts, same template
                ▼
             judge: score against a fixed rubric, then merge
                │ merged concept + scores + rejected alternatives
                ▼
             skeptic pass on the merged concept (optional) ──► operator
```

The stages separate gathering facts, generating options, and choosing among
them. Each stage's output is written to a file that later stages and people
can read, rather than relayed only through the orchestrator's context.
Implementing agents can then be pointed at those files ("verified against
the reference source; read what you need") instead of receiving a summary.

The workflow can run in the background while the orchestrator reads the
code it will touch; the two meet when the concept arrives.

## Stage 1: Researchers on Different Axes

Split the question by axis, not by source, so that the researchers do not
duplicate one another. Typical axes for a feature in a host application:

- **Host surface**: which APIs, data definitions and extension points exist,
  and how they behave, with links to reference material or source;
- **Prior art**: how existing plugins, products or papers solved similar
  problems, and what went wrong for them;
- **Constraints**: performance budgets, save compatibility, platform limits,
  licensing;
- **Users**: what the people who will use it expect, from the specification,
  issue reports or the operator's notes; and
- **Risks**: failure modes, abuse cases, interactions with other features.

Anthropic's description of its research system reports that briefs without
clear objectives and boundaries led subagents to duplicate work and leave
gaps. Each researcher's brief needs the question, its axis, the sources to
prefer (primary documentation and source code over forum posts), the output
format, and an effort limit.

Researcher output, per finding: the claim, its source as a link or a file
and line, a confidence level, and whether the researcher verified it (for
example by reading source or running an experiment) or only read it.
Unverified claims stay marked as unverified in every later stage.

## Stage 2: Independent Concept Proposals

Give every proposer the same research pack and the same concept template,
and a different angle. Useful angles include:

- the simplest design that meets every requirement;
- the most robust design under failure, interruption and misuse;
- the design that best serves the project's purpose or tone, for example
  the most entertaining one where play is the point; and
- the most reusable design, which others could build on.

Proposers must not see one another's drafts. Tversky and Kahneman showed
that estimates anchor on an initial value even when it is irrelevant. By
analogy, a proposer shown another's draft is likely to produce a variation
of it. Independent samples are also what makes
aggregation useful; self-consistency sampling improves model reasoning by
drawing several independent reasoning paths and combining their answers.

The template keeps proposals comparable:

```text
Summary (3 sentences)
How it meets each requirement (one line per requirement)
Host APIs and data it depends on (from the research pack, with sources)
Main risks and how the design handles them
What it costs: complexity, performance, effort
What it deliberately leaves out
```

## Stage 3: The Judge

Fix the rubric before the proposals arrive, so that it cannot be bent to fit
a favorite. A rubric names criteria, weights and a scale:

| Criterion | Weight | Scale anchor for top score |
| --- | --- | --- |
| Meets every requirement | 3 | Each requirement met, with evidence |
| Feasible on the host as researched | 3 | Every dependency verified in stage 1 |
| Robustness | 2 | Handles interruption, reload and misuse |
| Fit with project purpose | 2 | Operator's stated goals served directly |
| Cost | 1 | Small, testable, reversible |

Score each proposal on its own, criterion by criterion, before comparing
them. Then merge: take the best-scoring proposal as the base, graft in
elements from others that scored higher on specific criteria, and check that
the grafts do not conflict. Re-verify every host identifier and API the
merged concept names against the research pack or the host's data; merging
is where a name from one proposal meets an assumption from another. Record
the scores, the reasons, and the rejected alternatives with why each was
rejected. The record is what later readers need when a choice is
questioned.

In one such run, three proposers took a historical-homage angle, a
practical test-range angle and a comedy angle. The judge scored fit, fun,
test value, buildability and tone, took the comedy concept as the base, and
grafted named ideas from the other two. The whole research workflow, eight
agents, took about half an hour and 1.5 million tokens.

Model judges have measured biases. Zheng and colleagues report position,
verbosity and self-enhancement biases. Counter them:

- present proposals in a randomized order, or score each in a separate call;
- strip length differences that carry no content, or score against a length
  cap;
- where you can, judge with a different model or configuration from the
  proposers; and
- require the judge to cite the proposal text that earned each score.

## Stage 4: Skeptic and Operator

A skeptic pass on the merged concept looks for claims about the host that
stage 1 did not verify, requirements the merge dropped, and conflicts
between grafted elements. Its confirmed findings return to the judge or to
the operator.

The operator decides. Present the merged concept, the scores, the main
rejected alternative, and the open questions. Record the decision and its
reasons where the project keeps decisions.

## Sizing

Not every question needs every stage. One researcher and one proposal suit
a small, well-understood change. Use parallel researchers when the host or
domain is unfamiliar. Use independent proposals when reasonable people would
design it differently. Use a judge and skeptic when the decision is costly
to reverse. Anthropic reports multi-agent systems using about fifteen times
the tokens of a chat; spend that where a wrong choice would cost more.

## Sharp Edges

- **Research that is only reading.** A claim about host behavior that no one
  checked against source or an experiment can sink the chosen design.
  Carry confidence and verification status forward.
- **Angles that collapse.** Proposers given vague angles converge. Make each
  angle a concrete optimization target.
- **Merges that do not fit.** Grafted elements can contradict one another's
  assumptions. Re-run the requirement check on the merged concept.
- **Rubrics written afterward.** A rubric fitted to the winner records a
  preference, not a judgment.
- **Lost artifacts.** If research packs and proposals live only in a
  session's context, an interruption loses them. Write them to files.

## Further Information

- Anthropic, [How we built our multi-agent research
  system](https://www.anthropic.com/engineering/multi-agent-research-system):
  parallel subagents, task descriptions, rubric-based judging, artifacts
  that persist outside the lead agent, and token cost.
- Anthropic, [Building effective
  agents](https://www.anthropic.com/engineering/building-effective-agents):
  sectioning, voting and orchestrator-workers patterns.
- Amos Tversky and Daniel Kahneman, [Judgment under Uncertainty: Heuristics
  and Biases](https://doi.org/10.1126/science.185.4157.1124), *Science*
  185(4157), 1974: anchoring.
- Xuezhi Wang et al., [Self-Consistency Improves Chain of Thought Reasoning
  in Language Models](https://arxiv.org/abs/2203.11171), ICLR 2023.
- Lianmin Zheng et al., [Judging LLM-as-a-Judge with MT-Bench and Chatbot
  Arena](https://arxiv.org/abs/2306.05685), NeurIPS 2023 Datasets and
  Benchmarks.
- Yilun Du et al., [Improving Factuality and Reasoning in Language Models
  through Multiagent Debate](https://arxiv.org/abs/2305.14325), 2023: an
  alternative in which agents critique one another over several rounds.
