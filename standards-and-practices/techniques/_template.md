# Technique Name

## Use When

Describe the recurring problem and the conditions that make this technique a
good fit. State important non-goals.

## Invariants and Safety Boundaries

- List properties every implementation must preserve.
- Identify destructive, privileged, privacy-sensitive, or externally visible
  actions.

## Design Choices

Describe the important choices, their tradeoffs, and the evidence a project
should use to decide among them. Do not prescribe a language or technology
without a requirement that makes it necessary.

## Execution Pattern

1. Describe the implementation-neutral sequence.
2. Identify decisions that must be recorded.
3. Identify review or authorization boundaries.

## Validation Outcomes

Describe observable outcomes that prove the technique works, including
failure paths and recovery. Commands and automation belong to the consuming
project; FieldManual supplies no technique-specific verifier.

## Failure Handling and Rollback

Describe how to fail safely, preserve evidence or data, and return to a
known-good state.

## Common Pitfalls

- Add concise, actionable pitfalls.

## Related Guidance

- Link applicable documents under `../languages/`.
- Link applicable documents under `../technologies/`.
