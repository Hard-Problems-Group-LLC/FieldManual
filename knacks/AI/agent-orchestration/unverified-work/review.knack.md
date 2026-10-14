# Integrating Unverified Agent Work: Review

Load this companion to the
[overview](overview.knack.md) when you
review a delivery from an agent that could not build or run it. Each
signature below gives what it looks like, how to detect it cheaply, and
what to do.

Source review: 2026-10-13.

## Order of Review

Mechanical checks first, judgment last:

1. checksum and compare every copy of the delivery;
2. scan for placeholders and stubs;
3. build on the real toolchain;
4. check external APIs against the real interfaces;
5. validate data values against the real schema;
6. run the tests, count them, and prove new ones can fail;
7. diff structured and formatted files byte for byte;
8. check facts: dates, versions, install locations, citations; and only
   then
9. review the design and logic.

Reading logic that does not compile wastes the reviewer's attention on code
that will change anyway.

## Placeholders and Elisions

**Looks like:** comments such as "see previous message for the full code",
"truncated here for brevity", "rest unchanged", "placeholder"; source files
of one or two lines; data definitions naming classes that exist only in the
elided code.

**Detect:**

```sh
grep -rniE "for brevity|previous message|truncated|placeholder" .
grep -rniE "rest (of|is) unchanged|\.\.\. ?existing" .
find . -name "*.cs" -size -200c       # suspiciously small sources
```

Adjust the extensions and patterns to the language. Then checksum every
copy that claims to be the same version (archives, downloads, unpacked
folders): in one project one copy held real code and a later one held
placeholders throughout.

**Do:** rebuild from the last complete copy. Asking the agent to regenerate
the missing parts produces new unverified code, not the lost code.

## Near-Miss APIs

**Looks like:** names a little off from the real ones. Neutral examples of
the kinds seen:

- `SoundIds.ShieldAbsorb` where the host defines `Shield_Absorb`;
- `Commands.DropCarried` where the real member is `DropCarriedActor`;
- a constant such as `Categories.FoodMeals` that the host never defined;
- a named parameter `nearValidator:` where the method takes
  `extraValidator:`; and
- an override signature from an older host version.

**Detect:** compile against the real assemblies or headers. Where the host
is closed, search its reference source or a decompilation for every
external name the delivery uses, and record the host version checked.

**Do:** fix each call from the real interface, then re-read the logic
around it. A wrong name often comes with a wrong assumption about behavior.

## Tests That Pin Defects

**Looks like:** "regression" or snapshot tests asserting current values:
a field set to a value the host rejects, a flag the host no longer reads, a
supported-version list that includes a version the project does not target.

**Detect:** for every literal a test asserts about data, find the real
schema or the host's loader and confirm that the value is valid. Also check
test fakes against the real components: a fake random source returning
values in `[0, 1)` encoded an assumption the host's generator does not
honor.

**Do:** correct the value and the code, then prove the test fails on the old
value. A test that pins current behavior is a characterization test and is
useful only when the current behavior is known to be right.

## Claims Without Evidence

**Looks like:** "all tests pass", "no build changes required", "audited
against the documentation", without the commands or output that would
show it; citations through reader proxies or caching services; decision-log
dates that disagree with commit dates.

**Detect:** ask for, or rerun, the commands; compare every logged date with
`git log --format='%ad %h %s'` for the commit that introduced it; resolve
every citation to the canonical page and check that it says what is
claimed.

**Do:** mark unverified claims as such in the record, replace citations with
canonical links, and correct dates from the history.

## Misapplied Formatting

**Looks like:** a pull request described as formatting that also:

- splits identifiers or type names across lines;
- wraps values in build files, connection strings or paths;
- inserts line breaks into user-facing text, which the host then shows
  literally;
- re-serializes XML or JSON (quote style, attribute order, declaration);
  or
- drops or adds a byte-order mark, or changes line endings.

**Detect:**

```sh
git diff --stat <base>..<branch>
git diff -w <base>..<branch>          # changes beyond whitespace
git diff --text <base>..<branch> -- '*.sln' '*.xml' | head
git ls-files --eol                    # line endings per file
```

Build after every formatting change, and diff structured files at the byte
level.

**Do:** enforce width with a formatter that understands the language, exempt
structured files and user-facing strings from prose rules, and never accept
a wrap-only diff that was not compiled.

## Invented Environment Facts

**Looks like:** install instructions pointing at a folder the host never
loads plugins from; the wrong target version; asset briefs that ignore the
host's conventions (a perspective the host does not use, sizes and
resolutions that do not match its sprites, icons for features that do not
exist); promised files that were never created.

**Detect:** check each fact against the host's official documentation or
the project's own working configuration. Derive asset briefs from the
code's actual texture paths and the project's art-direction document.

**Do:** correct the facts and the instructions that produced them.

## Process Signatures

- **Many tiny pull requests**, each merged seconds after its commit, with no
  build. Review the combined diff rather than each request.
- **Documentation and process changes outnumber code changes.** These are
  cheap to keep when sound; check that they describe what exists.
- **A tool that failed once and was retried silently.** Look for repeated
  identical operations in the agent's log; a flaky tool can leave partial
  edits.

## Recording the Review

For each artifact, record the decision and the evidence:

```text
src/core/selector.cs     rewrite  never compiled; 3 near-miss APIs
tests/data_tests.cs      rewrite  pins 2 values the host rejects
AGENTS.md                keep     sound process; dates corrected
docs/install.md          rewrite  wrong install folder and target version
```

The table becomes the basis for the reconciliation in the [integration
companion](integration.knack.md).

## Further Information

- Nihal Jain et al., [On Mitigating Code LLM Hallucinations with API
  Documentation](https://arxiv.org/abs/2407.09726), 2024.
- Git, [git-diff](https://git-scm.com/docs/git-diff) and
  [git-ls-files](https://git-scm.com/docs/git-ls-files): whitespace-blind
  diffs and per-file line endings.
- FieldManual, [Proving Checks Can Fail: Vacuous
  Checks](../../../software-engineering/testing/proving-checks/vacuity.knack.md).
