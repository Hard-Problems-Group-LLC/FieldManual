# Culture-Safe Formatting in .NET

Reviewed: 2026-10-13

## When to Load This Knack

Load this knack when .NET code turns numbers, dates, or identifiers into
text or back, compares or changes the case of strings, or writes files,
logs, keys, or test expectations. It matters most for plugins and libraries
that run inside someone else's process under the user's regional settings.

Load the [numbers companion](CSharp.knack.md)
for invariant number and date APIs on `netstandard2.0` and for floating-point
text that must match across .NET Framework and modern .NET.

## Mental Model

Every culture-sensitive call reads an implicit global:
`CultureInfo.CurrentCulture`. It is per thread, flows into task-based
asynchronous operations, and starts from the user's operating-system
settings, including any customizations made in Windows regional settings. A
host process runs under its user's culture and may change it. The same code
therefore produces different text on different machines unless it names a
culture explicitly.

Classify every string by its audience:

- **Machine text** is read by software: files, saved state, keys,
  identifiers, protocol messages, parseable logs, generated code, sort keys,
  and test expectations. Format it with `CultureInfo.InvariantCulture` and
  compare it ordinally.
- **Human text** is read by a person in a user interface. Format it with the
  current culture or with the host's localization conventions, chosen
  deliberately.
- **Linguistic ordering** for display, such as an alphabetized list, uses
  culture-aware comparison on purpose.

Microsoft's rule CA1305 states the same split: use the current culture for
values displayed to the user, the invariant culture for values stored and
read by software, and let the consumer choose when the destination is
unknown.

## What Goes Wrong

Each of these was observed on both .NET Framework 4.8 and .NET 8:

| Culture | Code | Result |
| --- | --- | --- |
| de-DE | `1.5.ToString()` | `1,5` |
| de-DE | `$"{1.5}"` | `1,5` |
| de-DE | `double.Parse("1.5")` | `15`, with no exception |
| tr-TR | `"file".ToUpper()` | `FİLE` |

The silent parse is the dangerous case: a German-locale user loads a file
written on an English-locale machine and every decimal value is off by
orders of magnitude, with nothing logged.

Integers look safe because their digits are never localized, but signs are.
On .NET 8, `(-5).ToString()` produced `−5` with U+2212 MINUS SIGN under
`sv-SE`, and prefixed invisible direction marks under `ar-SA` (U+061C) and
`fa-IR` (U+200E). .NET Framework printed `-5` for all three. A culture test
that formats only non-negative integers therefore cannot catch a missing
provider.

## Formatting and Parsing

Pass a provider at every boundary where text is machine text:

```csharp
using System.Globalization;

string a = value.ToString(CultureInfo.InvariantCulture);
string b = value.ToString("F2", CultureInfo.InvariantCulture);
string c = FormattableString.Invariant($"{x},{y}");
string d = string.Format(CultureInfo.InvariantCulture, "{0:F3}", value);

bool ok = double.TryParse(
    text, NumberStyles.Float, CultureInfo.InvariantCulture, out double v);
```

`FormattableString.Invariant` works on `netstandard2.0` and .NET Framework;
`string.Create(IFormatProvider, ...)` requires .NET 6 or later. Prefer
`TryParse` with explicit `NumberStyles` for input that may be malformed, and
report the failure with the offending text and its source.

## Comparison and Casing

- Compare identifiers, keys, file names, element names, and enumeration
  names with `StringComparison.Ordinal` or `OrdinalIgnoreCase`, and build
  dictionaries and sorted output with `StringComparer.Ordinal`.
- Change the case of identifiers with `ToUpperInvariant` and
  `ToLowerInvariant`.
- `string.Equals` and `==` are ordinal by default, but `string.Compare`,
  `StartsWith(string)`, `EndsWith(string)`, and `IndexOf(string)` are
  culture-sensitive by default. Pass a `StringComparison` every time.
- .NET 5 and later use ICU on current Windows versions, while .NET Framework
  uses NLS. Culture-sensitive comparison, sorting, and casing can therefore
  differ between a modern test run and a .NET Framework host even under the
  same culture. Ordinal operations do not.

## Hosts, Threads, and Plugins

- Do not change `CurrentCulture` or `DefaultThreadCurrentCulture` from a
  plugin. The setting is shared with the host and every other plugin, and a
  global fix hides missing providers in your own code.
- Threads created by the host or a thread pool may carry a different culture
  from the thread that loaded the plugin. Explicit providers make that
  irrelevant.
- When the host has its own localization system, display text should go
  through it. Numbers embedded in that text still need a deliberate choice of
  format.

## Testing

- Run culture-sensitive tests under hostile cultures: `de-DE` swaps the
  decimal and group separators, `tr-TR` has dotted and dotless capital I,
  `fr-FR` uses a space-like group separator, and `sv-SE` uses a Unicode
  minus sign on modern .NET. Include negative numbers and decimals in the
  values tested. Set `CultureInfo.CurrentCulture` inside the test and
  restore it in a `finally` block or fixture.
- Generate golden files and expected strings with the invariant culture,
  never by capturing the developer's machine output.
- Turn on the globalization analyzers in the shared library. They are not
  build warnings by default; on `netstandard2.0` and .NET Framework targets
  set `EnableNETAnalyzers` to `true`, then raise the rules in
  `.editorconfig`:

```ini
[*.cs]
dotnet_diagnostic.CA1304.severity = warning
dotnet_diagnostic.CA1305.severity = warning
dotnet_diagnostic.CA1307.severity = warning
dotnet_diagnostic.CA1309.severity = warning
dotnet_diagnostic.CA1310.severity = warning
dotnet_diagnostic.CA1311.severity = warning
```

## Sharp Edges

- Interpolated strings, `string.Format` without a provider,
  `Convert.ToString`, and `Convert.ToDouble` all use the current culture.
- Windows users can customize separators for their own culture, so even an
  English-locale machine may not produce a period.
- Invariant formatting fixes separators but not floating-point digits:
  .NET Framework and modern .NET print some doubles differently. See the
  numbers companion.
- `StringComparison.InvariantCulture` is linguistic, not ordinal; it is
  rarely the right choice for identifiers.

## Review Checklist

- Is every string classified as machine or human text?
- Does every machine-text conversion name `InvariantCulture`?
- Do identifier comparisons and casing use ordinal or invariant methods?
- Does the plugin leave the process culture alone?
- Do tests run under at least one comma-decimal culture and `tr-TR`?
- Are the globalization analyzers enabled as warnings?

## Further Information

- [CA1305: Specify IFormatProvider](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca1305)
- [Best practices for comparing strings in .NET](https://learn.microsoft.com/en-us/dotnet/standard/base-types/best-practices-strings)
- [`CultureInfo.CurrentCulture`](https://learn.microsoft.com/en-us/dotnet/api/system.globalization.cultureinfo.currentculture)
- [`CultureInfo.InvariantCulture`](https://learn.microsoft.com/en-us/dotnet/api/system.globalization.cultureinfo.invariantculture)
- [Globalization and ICU](https://learn.microsoft.com/en-us/dotnet/core/extensions/globalization-icu)
- [Code analysis in .NET](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview)
