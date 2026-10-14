# C# Language Features on netstandard2.0

Reviewed: 2026-10-13

Load this companion after the
[shared-library overview](overview.knack.md) when
choosing a C# language version for a `netstandard2.0` or .NET Framework
project, adding polyfills, or diagnosing errors such as CS0518, CS0656,
CS8701, or CS8919. The feature lists below were checked by compiling probe
code for `netstandard2.0` with a .NET 9 SDK compiler at `LangVersion` 12 and
13.

## The Version Decision

The compiler picks the default language version from the target framework.
For `netstandard2.0`, `netstandard1.x`, and every .NET Framework version the
default is C# 7.3. Microsoft states that using a newer language version than
the one associated with the target framework is unsupported and can cause
hard-to-diagnose compile-time and runtime errors, and it warns against
`LangVersion` `latest` because its meaning changes with the installed
compiler. The first symptom is often `<Nullable>enable</Nullable>` failing
with CS8630, "Invalid 'nullable' value: 'Enable' for C# 7.3".

Raising the version on `netstandard2.0` is nonetheless common, and
polyfill packages exist to support it. A project that does so should:

1. record the decision and its reason in its decision log;
2. pin a number, such as `12.0`, never `latest` or `preview`;
3. make sure the oldest Visual Studio or .NET SDK that builds the project
   understands that number; and
4. use only features whose requirements the target meets, as classified
   below.

To see the compiler and language version a build actually uses, put
`#error version` in a source file temporarily; the compiler reports CS8304
with both values.

## Syntax-Only Features

These compile for `netstandard2.0` without extra types once the language
version allows them:

- switch expressions, property and relational patterns;
- file-scoped namespaces and global `using` directives;
- target-typed `new`, `using` declarations, and static local functions;
- raw string literals;
- primary constructors on classes;
- collection expressions for arrays and `List<T>`;
- mutable `record struct` declarations; and
- nullable reference annotations with `<Nullable>enable</Nullable>`.

Value tuples also work, because `System.ValueTuple` is part of .NET Standard
2.0.

## Features That Need Compiler-Required Types

The compiler looks these types up by name. If they are missing it reports an
error; declaring an `internal` copy in the library satisfies it.

| Feature | Missing type | Error seen |
| --- | --- | --- |
| `init` accessors, `record` classes, `readonly record struct` | `System.Runtime.CompilerServices.IsExternalInit` | CS0518 |
| `required` members | `RequiredMemberAttribute`, `CompilerFeatureRequiredAttribute`; also `SetsRequiredMembersAttribute` when a constructor uses it | CS0656, CS0246 |
| `^1` indexes, `..` ranges, and list patterns such as `[1, _, 3]` | `System.Index`, `System.Range` | CS0518 |
| `[NotNullWhen]` and other nullable-flow attributes | `System.Diagnostics.CodeAnalysis` attributes | CS0246 |
| `[CallerArgumentExpression]` | `System.Runtime.CompilerServices.CallerArgumentExpressionAttribute` | CS0246 |

Notes:

- A mutable positional `record struct` generates read-write properties and
  needs no polyfill; a `readonly record struct` generates `init` properties
  and does.
- List patterns need `System.Index` even without a slice.
- Marker types such as `IsExternalInit` are empty and safe to hand-write.
  `System.Index` and `System.Range` are structs with real behaviour; prefer
  explicit `array.Length - 1` arithmetic or a maintained polyfill package
  over a hand-written copy.
- A source generator such as PolySharp emits only the polyfills a target
  needs. It still requires an explicit `LangVersion`, and it is a build-time
  dependency to review like any other.

## Runtime Features

No polyfill can supply these on `netstandard2.0` or .NET Framework:

- default interface members (CS8701, "Target runtime doesn't support default
  interface implementation"); and
- static abstract or static virtual interface members (CS8919).

Design around them with abstract base classes, extension methods, or explicit
strategy objects.

## Weaker Nullable Analysis

The `netstandard2.0` reference assemblies have no nullable annotations, so
the compiler cannot learn from framework methods. On `netstandard2.0` this
code warns CS8602 although it is safe:

```csharp
if (!string.IsNullOrEmpty(name))
{
    return name.Length; // CS8602 on netstandard2.0
}
```

Use a pattern (`name is { Length: > 0 }`), an explicit null comparison, or a
local helper annotated with a polyfilled `[NotNullWhen(false)]`. The same
source compiles cleanly in a modern test project, so do not judge the core's
nullable warnings from the test build alone.

## Missing APIs

Each of the following failed to compile for `netstandard2.0`; all are
available on modern .NET:

- `Math.Clamp`, `MathF`, and the `HashCode` struct;
- `Dictionary<TKey, TValue>.GetValueOrDefault` and `TryAdd`;
- deconstruction of `KeyValuePair<TKey, TValue>` in `foreach (var (k, v) in
  dictionary)`;
- `Enumerable.ToHashSet`;
- `string.StartsWith(char)`, `string.Join(char, ...)`, and
  `string.Split(char, StringSplitOptions)`;
- `ArgumentNullException.ThrowIfNull` and `Random.Shared`; and
- `string.Create(IFormatProvider, ...)` for invariant interpolation.

`string.Contains(char)` is a trap: with `using System.Linq` in scope it
compiles by binding to `Enumerable.Contains<char>`, so the code works but
takes a different path than on modern .NET.

`array.Reverse()` is a worse trap at C# 14. For targets older than `net10.0`
that reference `System.Memory`, the compiler binds it to the in-place
`MemoryExtensions.Reverse(Span<T>)` instead of `Enumerable.Reverse`, so the
call mutates the array and returns nothing. Write
`Enumerable.Reverse(array)` when a reversed sequence is wanted.

Records' synthesized equality compares each member with its default
equality, so array and list members compare by reference: two records whose
arrays hold equal contents are not equal. Compare such members explicitly,
for example with `SequenceEqual`.

Packages fill some gaps, such as `System.Memory` for `Span<T>`,
`Microsoft.Bcl.AsyncInterfaces` for `IAsyncEnumerable<T>`, and
`Microsoft.Bcl.HashCode` for `HashCode`. Each adds an assembly to deploy and
may conflict with a different version already loaded by the host. Prefer a
small local helper when the need is small.

## Review Checklist

- Is a raised `LangVersion` recorded, numeric, and supported by every build
  machine?
- Does every compiler-required type exist exactly once, `internal`, in the
  correct namespace?
- Does the design avoid default and static abstract interface members?
- Are nullable warnings judged from the `netstandard2.0` build?
- Are added packages deployable to, and compatible with, the host?

## Further Information

- [C# language versioning](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-versioning)
- [Configure the C# language version](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/configure-language-version)
- [C# language version history](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-version-history)
- [Records reference](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/record)
- [Init-only setters specification](https://github.com/dotnet/csharplang/blob/main/proposals/csharp-9.0/init.md)
- [PolySharp repository](https://github.com/Sergio0694/PolySharp)
- [Compiler breaking changes in .NET 10, including `Reverse`](https://github.com/dotnet/roslyn/blob/main/docs/compilers/CSharp/Compiler%20Breaking%20Changes%20-%20DotNet%2010.md)
- [.NET Standard 2.0 API list](https://github.com/dotnet/standard/blob/v2.1.0/docs/versions/netstandard2.0.md)
