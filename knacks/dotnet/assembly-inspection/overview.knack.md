# Closed-Assembly Inspection

Reviewed: 2026-10-13

## When to Load This Knack

Load this knack before relying on the behaviour of a closed .NET assembly
that a project compiles against, such as a host application's game or
business logic or a vendor library, and when validating data files against
that assembly's types. The working rule is to double-check the references: a
member's name and signature are not a contract for what it does.

Load the [ilspycmd companion](ilspycmd.knack.md)
for decompilation commands and the
[PowerShell reflection companion](reflection.PowerShell.knack.md)
for metadata queries and data-file validation.

## Licence First

This section flags a legal question; it does not answer it. Decompiling a
third-party binary may be restricted by its licence or end-user licence
agreement. Some jurisdictions permit limited decompilation to achieve
interoperability; for example, Article 6 of EU Directive 2009/24/EC allows it
under narrow conditions and Article 8 voids contrary contract terms. Rules
differ by jurisdiction and purpose. When the licence is unclear, ask the
vendor or qualified counsel before decompiling, and record the decision.

Regardless of permission:

- never commit, publish, or redistribute decompiled source;
- keep decompiler output in an ignored, checkout-local folder, following
  FieldManual's [local operator state](../../../standards-and-practices/core/local-operator-state.md)
  standard;
- quote only what a note needs, such as a signature or a few lines; and
- describe conclusions in your own words in project records.

## Mental Model

Use the cheapest evidence that answers the question:

1. **Documentation and vendor material**: manuals, published API
   references, partial source, and the host's own data files.
2. **Metadata**: names, signatures, field types, visibility, virtual and
   abstract modifiers, attributes, and enumeration values, read by
   reflection. Metadata answers whether something exists and how it is
   declared.
3. **Decompiled code**: what a method does, including base implementations,
   validation, side effects, exceptions, and call order.
4. **In-host experiment**: behaviour that depends on live state, confirmed
   by a smoke test.

Before calling, overriding, or depending on a member, read it at the level
its risk requires. Overriding a virtual method and deciding whether to call
the base needs level 3. Reading a private field needs level 2 plus a plan for
host updates. Writing a data file needs the target type's fields.

## Workflow

1. Record the host version, for example the file version of its main
   assembly. Every conclusion is about that version.
2. Query metadata first with a reflection script or `ilspycmd -l`.
3. Decompile only the types in question with `ilspycmd -t`. Decompile the
   whole assembly to a project when a wide search is needed; large
   assemblies take minutes.
4. Search the decompiled tree for overrides, callers, and string literals
   such as an error message seen in a log.
5. Write the conclusion, the evidence level, and the host version in project
   notes.
6. Confirm risky conclusions in the host with a smoke test.
7. Repeat the relevant checks after a host update.

## Read Before Calling

- **Base virtual methods.** A base implementation may throw
  `NotImplementedException` by design, so an override that calls `base`
  crashes. Another base method may do essential bookkeeping that an override
  must not skip. Read it, then decide.
- **Validation.** Learn whether the host clamps, rejects, or silently
  accepts out-of-range input.
- **Side effects and order.** Methods often notify other systems, schedule
  work, or mutate shared state in addition to their named purpose.
- **Threading.** Engine APIs are often restricted to the main thread; find
  out before calling from a worker.
- **Static initializers.** Touching a type, or reading a static field by
  reflection, runs its type initializer, which may call into the engine.
- **Private members.** Reflection can reach them, but they change without
  notice. Resolve each `FieldInfo` or `MethodInfo` once at load time, fail
  loudly with the host version if it is missing, and cover the access path in
  a smoke test.

## Reading Decompiled Code

Decompiled output is a reconstruction, not the original source:

- comments are gone and local names may be synthesized;
- closures become compiler-generated classes such as `<>c__DisplayClass5_0`,
  and cached lambdas live in a nested `<>c` class;
- iterators and `async` methods become state-machine classes such as
  `<Run>d__12` with a `MoveNext` method;
- auto-properties expose fields such as `<Name>k__BackingField`;
- `switch` statements may appear as hash computations, comparison chains, or
  `goto` labels where the decompiler cannot recover structure, which says
  nothing about how the original was written; and
- constants from other assemblies appear as literal values.

When the C# rendering is ambiguous, read the IL with `ilspycmd -il`.
Compiler-generated names can change between host builds; never reflect on
them from shipped code.

## Validate Data Files Against Host Types

Hosts that map data files onto types, for example XML elements onto fields,
may skip or merely log an unknown or misspelt field. A script that checks
every element name against the target type's fields, including inherited
ones, catches the mistake before launch. Teach the validator the host's
aliases and custom loaders, or it will report false positives. The
reflection companion shows the pattern.

## Sharp Edges

- The runtime that performs reflection is not the host's runtime. A type can
  load in one and fail in the other; record which runtime you used.
- .NET Framework cannot unload a single assembly, so a reflection session
  locks the file until its process exits.
- `Assembly.GetTypes()` excludes forwarded types, so a facade assembly
  appears nearly empty.
- Decompiler releases differ in output and required .NET runtime; pin the
  version.
- File paths in a host's stack traces come from the symbol files written on
  the author's build machine. A path in a trace does not mean that folder
  exists on the machine being debugged.
- Whole decompiled trees pasted into prompts, issues, or reviews raise both
  licence and context-size problems. Share conclusions instead.

## Review Checklist

- Was the licence position checked and recorded before decompiling?
- Is decompiled output ignored by version control and absent from commits?
- Does each conclusion name its evidence level and host version?
- Were base implementations read before deciding whether to call them?
- Are private-member accesses resolved once, checked, and smoke-tested?
- Are data files validated against the host's types?

## Further Information

- [ILSpy repository](https://github.com/icsharpcode/ILSpy)
- [ilspycmd README](https://github.com/icsharpcode/ILSpy/blob/master/ICSharpCode.ILSpyCmd/README.md)
- [`Assembly.GetTypes`](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.assembly.gettypes)
- [Inspect assembly contents using MetadataLoadContext](https://learn.microsoft.com/en-us/dotnet/standard/assembly/inspect-contents-using-metadataloadcontext)
- [Load and unload assemblies](https://learn.microsoft.com/en-us/dotnet/standard/assembly/load-unload)
- [EU Directive 2009/24/EC on the legal protection of computer programs](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0024)
