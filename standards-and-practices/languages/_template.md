# Language Name

## Scope

State what language and ecosystem this document covers, including important
boundaries with related languages or runtimes.

## Project-Declared Baseline

Describe how a consuming project records:

- supported language and runtime versions
- package-manager or build-tool expectations
- compatibility promises and upgrade policy

Do not impose a moving universal version from FieldManual.

## Code Quality

Describe the expected approach to:

- formatting
- linting
- static analysis or type checking
- public interfaces and documentation
- generated code

Name tools as reasonable options, not as hidden FieldManual dependencies.

## Dependencies and Environments

Explain dependency declaration, lock or constraint files, environment
isolation, reproducible setup, and the boundary between project and
user/system state.

## Design Practices

Record language-specific patterns and hazards that materially affect
maintainability, correctness, security, or portability.

## Testing and Verification

Describe suitable unit, integration, contract, smoke, and end-to-end
strategies. Require local and continuous-integration behavior to agree.

Verification commands and scripts are owned by the consuming project.
FieldManual does not provide a verifier for this language.

## Common Pitfalls

- Add concise, actionable pitfalls.

## Related Guidance

- Link cross-language standards.
- Link applicable documents under `../../technologies/`.
