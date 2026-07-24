# Cyclomatic Complexity

Load this knack when branch structure has become difficult to reason about,
when a complexity report changes materially, or when review needs a focused
prompt for testing and refactoring.

## What The Metric Says

Cyclomatic complexity measures the number of linearly independent paths in a
control-flow graph. For a graph, McCabe expressed it in terms of edges,
nodes, and connected components. For a simple structured routine, tools often
approximate it as a base path plus decision points.

That approximation is not one universal counting rule. Tools and languages
differ on whether they count boolean operands, switch or match arms,
exceptions, comprehensions, conditional expressions, macros, generated
branches, and nested functions. Two numbers are comparable only when their
scope and measurement semantics are comparable.

The metric describes control-flow structure. It does not directly measure:

- the clarity of names and abstractions;
- nesting depth or the effort needed to retain context;
- data-flow and state-space complexity;
- coupling between modules;
- concurrency or temporal behavior;
- requirements coverage; or
- whether a branch is correct.

A flat dispatcher may score higher while remaining readable. Deeply nested
code may score lower and still be hard to maintain.

## Use It As A Signal

Treat an elevated or rising score as a request to inspect:

- whether one routine owns too many independent decisions;
- whether branch scenarios and failure modes are identifiable;
- whether risky paths have tests that assert meaningful outcomes;
- whether nesting, mutation, coupling, or asynchronous behavior compounds the
  control-flow count;
- whether a generated file, parser, state machine, or integration boundary
  explains the shape; and
- whether the same behavior could be expressed more clearly.

Do not use one FieldManual-wide threshold. Historical guidance often uses
values such as 10 or 15 as review triggers, but an appropriate trigger depends
on the language, analyzer, risk, generated-code policy, and architecture. A
project that enforces a threshold must declare the tool and version, scope,
value, exceptions, and reason in project-owned policy.

A change-based review can be more useful than a universal ceiling. Investigate
unexpected increases, high-complexity code with high defect or change
frequency, and functions whose measured score conflicts with reviewer
experience.

## Refactoring Responses

Prefer changes that lower reasoning risk, not changes that merely lower the
reported number:

- name complex predicates and domain decisions;
- use guard clauses when they make the normal path clearer;
- separate independent lifecycle phases;
- isolate platform, protocol, and recovery policy;
- replace uniform cases with table-driven dispatch when the data form is
  genuinely clearer;
- reduce hidden mutation and make invariants explicit; and
- characterize branch behavior with tests before restructuring it.

Do not split a cohesive operation into tiny functions that hide shared state,
force readers to jump between files, or move decisions into opaque data solely
to satisfy a metric.

Comments should explain domain scenarios, invariants, hazards, and why a
decision boundary remains cohesive. They should not narrate every branch or
compensate for code that can be made clear directly.

## Testing Interpretation

Cyclomatic complexity can guide basis-path testing, but the number is not an
automatic count of sufficient test cases. Some paths may be infeasible, and
path execution alone does not establish correct requirements, data values,
side effects, error handling, concurrency behavior, or integrations.

Combine structural evidence with requirements-based tests, boundary cases,
regressions for known failures, and integration or system validation
appropriate to the risk. Coverage and complexity are complementary
observations, not proofs of quality.

## Measurement Record

When a metric influences a decision, record:

- repository revision and analyzed paths;
- analyzer, version, language mode, and configuration;
- treatment of tests, generated code, vendored code, and nested functions;
- baseline and current result;
- the code and risk reviewed because of the result; and
- the resulting action or explicit decision to leave the structure intact.

This record prevents a tool upgrade or configuration change from masquerading
as a code-quality regression.

## Review Checklist

- Are the metric's counting semantics and scope known?
- Is the result being used as a signal rather than a verdict?
- Do nesting, state, coupling, or concurrency create risk the score misses?
- Are meaningful branch and failure scenarios tested?
- Would a proposed refactor improve local reasoning and debugging?
- Is any threshold project-owned, justified, and reproducible?

## Further Information

- Thomas J. McCabe,
  [A Complexity Measure](https://doi.org/10.1109/TSE.1976.233837)
- NIST SP 500-235,
  [Structured Testing: A Testing Methodology Using the Cyclomatic Complexity Metric](https://www.nist.gov/publications/structured-testing-testing-methodology-using-cyclomatic-complexity-metric-0)

Reviewed: 2026-07-23.
