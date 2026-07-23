# Runtime and Package Environments

## Purpose

Make interpreter, compiler, runtime, and package selection explicit across
languages without prescribing one implementation tool.

## Precedence

When a language ecosystem supports these layers, resolve from least specific
to most specific:

1. system-provided runtime or packages;
2. user-local runtime or packages;
3. an explicitly selected user profile or toolchain;
4. a project-specific runtime, package set, or launcher.

The most specific valid layer wins. Resolution should be deterministic and
diagnosable: report the selected runtime, version, package source, and reason
when ambiguity would matter.

## Shared Baseline

Track project-required versions, selectors, lockfiles, and compatibility
constraints when the ecosystem supports them. Keep workstation-specific
paths, credentials, caches, and private mirrors in local configuration.

Do not silently install into or update a system-wide or user-owned environment
merely because it is available. Network access, privilege, user-home
mutation, and shared-toolchain changes must remain visible and subject to the
project's approval boundaries.

## Bootstrap and Steady State

Distinguish the minimal environment needed to initialize a project from the
steady-state environment used to build, test, and operate it.

A bootstrap runtime may have a broader compatibility floor and fewer
dependencies. It should establish or locate the declared steady-state
environment without pretending that its own package set is the final
development environment.

## Environment Or Scope Surprises

An unexpected interpreter, compiler, tool version, working scope, container,
sandbox, service account, privilege level, package source, or execution
authority is an interrupt condition.

Stop the current command sequence, report the mismatch, and determine whether
the declared workflow or the invocation is wrong. A fallback command may aid
diagnosis, but its success is not evidence that the documented workflow
passed. Correct and rerun the intended path, or explicitly record why it
could not be run.

Distinguish an ordinary test or lint failure from a surprise about which tool,
environment, authority, target, or scope actually ran. Capture reusable
workflow defects as a bug, ECR, proposal, or other project-management record
instead of normalizing an accidental fallback.

## Multi-Language Projects

Resolve each language or toolchain independently, then document how their
selectors and package managers interact. One language's environment manager
must not silently become the authority for another language.

Project entry may activate environments automatically or may use explicit
launchers. Either approach is acceptable when it is documented, predictable,
works outside one developer's shell history, and does not unexpectedly mutate
global state.

## Language-Specific Standards

Language-specific standards should define:

- supported versions;
- selector and lockfile conventions;
- package isolation;
- build and test entry points;
- local and continuous-integration parity; and
- upgrade and recovery expectations.

FieldManual core defines the precedence model only. Consuming projects or
future verifier submodules own executable checks.
