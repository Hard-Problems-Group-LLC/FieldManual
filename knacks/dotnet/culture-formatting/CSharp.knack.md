# Culture-Safe Numbers and Dates in C#

Reviewed: 2026-10-13

Load this companion after the
[culture-safe formatting overview](overview.knack.md)
when writing numbers or dates as machine text from `netstandard2.0` or .NET
Framework code, and whenever the same code runs on both .NET Framework and
modern .NET, as a shared library does when its tests run on `net8.0` and its
host runs .NET Framework. Behaviour marked "observed" was checked on .NET
Framework 4.8 and .NET 8 on 64-bit Windows; Mono-based hosts were not tested.

## Invariant APIs Available on netstandard2.0

| Task | API |
| --- | --- |
| Number to text | `value.ToString(format, CultureInfo.InvariantCulture)` |
| Interpolation | `FormattableString.Invariant($"...")` |
| Composite format | `string.Format(CultureInfo.InvariantCulture, ...)` |
| Builder | `builder.AppendFormat(CultureInfo.InvariantCulture, ...)` |
| Text to number | `double.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out v)` |
| Integer parse | `int.TryParse(text, NumberStyles.Integer, CultureInfo.InvariantCulture, out n)` |
| XML values | `XmlConvert.ToString(value)` and `XmlConvert.ToDouble(text)` |
| Date to text | `utc.ToString("o", CultureInfo.InvariantCulture)` |
| Text to date | `DateTime.ParseExact(text, "o", CultureInfo.InvariantCulture, DateTimeStyles.RoundtripKind)` |
| Test cultures | `CultureInfo.GetCultureInfo("de-DE")`, cached and read-only |

`XmlConvert` ignored a `de-DE` current culture in observation and produced
the same text on both runtimes for the values tried.

## Choose NumberStyles Deliberately

The default style for `double.Parse` accepts group separators. Under the
invariant culture the comma is the group separator, so the default parse of
`"1,5"` returned `15` on both runtimes: the mirror image of the German-locale
failure in the overview. `NumberStyles.Float` omits group separators, and
`double.TryParse("1,5", NumberStyles.Float, CultureInfo.InvariantCulture,
out _)` returned `false`. Rejecting text is better than misreading it.

| Style | Accepts |
| --- | --- |
| `NumberStyles.Integer` | Leading and trailing white space, leading sign |
| `NumberStyles.Float` | `Integer` plus decimal point and exponent |
| `NumberStyles.Float \| NumberStyles.AllowThousands` | The `double.Parse` default |

## Floating-Point Text Differs Between Runtimes

Invariant culture fixes the separators, not the digits.

**Default format.** Modern .NET formats `double` with the shortest
round-trippable string; .NET Framework uses 15 significant digits (`G15`)
and `float` uses `G7`. Observed:

| Expression | .NET Framework 4.8 | .NET 8 |
| --- | --- | --- |
| `0.1 + 0.2` | `0.3` | `0.30000000000000004` |
| `1.0 / 3` | `0.333333333333333` | `0.3333333333333333` |
| `1.1f * 3` | `3.3` | `3.3000002` |

**Round-trip formats.** Microsoft recommends `"G17"` for `double` and `"G9"`
for `float`, because `"R"` can fail to round-trip on .NET Framework. In
observation, `G17` round-tripped every tested value on both runtimes, but for
81 of about 200,000 random bit patterns the 17th digit differed between
runtimes. Values with a few decimal places did not differ.

**Fixed formats.** With `"F3"` and `"0.###"`, observed differences were:

- negative values that round to zero printed `-0.000` on .NET 8 and
  `0.000` on .NET Framework, and `Math.Round(-0.0001, 3)` printed `-0` and
  `0` respectively; and
- values close to a rounding midpoint could round differently, for example
  `110696425.014` and `110696425.015`, because .NET Framework first reduces
  the value to 15 significant digits.

No standard format guarantees byte-identical text for every `double` across
the two runtimes.

## Techniques

**Round-trip storage.** When a value must parse back exactly, write it with
`"G17"` (or `"G9"` for `float`) and the invariant culture, and compare parsed
values, not strings, in tests.

**Stable text.** When text must be byte-identical everywhere, as in golden
files, hashes, generated identifiers, or strings compared by tests, round to
an integer number of units first and format the integer:

```csharp
/// <summary>
/// Formats a value with exactly three decimals, identically on .NET
/// Framework and modern .NET.
/// </summary>
/// <param name="value">A finite value within the range of milli-units
/// representable by <see cref="long"/>.</param>
/// <returns>Invariant text such as <c>-12.300</c>.</returns>
internal static string FormatMilli(double value)
{
    if (double.IsNaN(value) || double.IsInfinity(value))
    {
        throw new ArgumentOutOfRangeException(nameof(value));
    }

    long milli = (long)Math.Round(
        value * 1000, MidpointRounding.AwayFromZero);
    return ((decimal)milli / 1000m).ToString(
        "F3", CultureInfo.InvariantCulture);
}
```

This produced identical text on both runtimes for 300,000 random values.
`long` has no negative zero, and `decimal` formatting is exact. Choose the
midpoint rule on purpose; `Math.Round` defaults to banker's rounding.

**Negative zero.** If a floating-point format must be used, normalize first:
`if (value == 0) { value = 0.0; }` turns `-0.0` into `0.0`, because
`-0.0 == 0.0` is true.

**Display.** Pick a fixed number of decimals that suits the quantity and
the reader; never rely on the default `ToString()` for display or storage.

**Tests.** Assert numeric results with a tolerance appropriate to the
calculation, and keep string assertions for values produced by the
stable-text technique.

## Dates and Times

- Store instants in UTC with the round-trip `"o"` format and parse them with
  `ParseExact` and `DateTimeStyles.RoundtripKind`; the kind survives the round
  trip.
- Culture affects more than separators. Under `th-TH`, the default calendar
  is the Thai Buddhist calendar, and `ToString("yyyy")` for 2026 produced
  `2569` on both runtimes. Use `CultureInfo.InvariantCulture` for any date
  written as machine text.
- Avoid persisting local times; their meaning depends on the machine's time
  zone and daylight-saving rules.

## Review Checklist

- Does every parse name both a culture and a `NumberStyles` value?
- Are persisted floating-point values written with `G17` or `G9`?
- Is byte-stable text derived from integers or `decimal`, not formatted
  `double` values?
- Is negative zero normalized where floating formats remain?
- Are dates persisted as UTC with the `"o"` format?
- Do tests compare floating-point results numerically?

## Further Information

- [Standard numeric format strings](https://learn.microsoft.com/en-us/dotnet/standard/base-types/standard-numeric-format-strings)
- [Floating-point parsing and formatting improvements in .NET Core 3.0](https://devblogs.microsoft.com/dotnet/floating-point-parsing-and-formatting-improvements-in-net-core-3-0/)
- [`NumberStyles`](https://learn.microsoft.com/en-us/dotnet/api/system.globalization.numberstyles)
- [`FormattableString.Invariant`](https://learn.microsoft.com/en-us/dotnet/api/system.formattablestring.invariant)
- [Standard date and time format strings](https://learn.microsoft.com/en-us/dotnet/standard/base-types/standard-date-and-time-format-strings)
- [`XmlConvert`](https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlconvert)
- [`Math.Round`](https://learn.microsoft.com/en-us/dotnet/api/system.math.round)
