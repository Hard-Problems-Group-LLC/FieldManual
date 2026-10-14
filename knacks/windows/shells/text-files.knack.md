# Text Files on Windows: Encodings and Line Endings

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion before an agent creates or patches text files on
Windows, when Git prints line-ending warnings, when a diff shows every line
changed, or when non-ASCII characters turn into question marks or
mojibake. Read the [agent shells overview](overview.knack.md)
first.

## Mental Model

A text file is bytes. Three independent properties decide whether two
tools agree about it:

1. **Encoding**: UTF-8, UTF-16LE, or a legacy code page such as
   Windows-1252.
2. **Byte-order mark (BOM)**: present or absent. UTF-8 files may carry the
   three bytes `EF BB BF`; UTF-16 files normally carry one.
3. **Line endings**: LF, CRLF, or, as a defect, a mixture.

Every writer has defaults for all three, and on Windows the defaults
disagree:

| Writer | Typical result on Windows |
| --- | --- |
| Agent file-writing tools | UTF-8 text with the line endings given to them, commonly LF |
| Bash and MSYS tools | Bytes as given; LF |
| Windows PowerShell 5.1 `>` | UTF-16LE with BOM, CRLF |
| PowerShell 7 `Set-Content` | UTF-8 without BOM, CRLF line separators |
| Python text mode, `newline=None` | `\n` written as CRLF |
| Git checkout with `core.autocrlf=true` | CRLF in the working tree for text files |

Check the agent tool's own documentation rather than assuming the first
row. The safe working rule is to observe the existing file's properties and
preserve them unless the change is specifically a conversion.

## Inspect Before Editing

Git reports both the index and working-tree endings:

```bash
git -C <repo> ls-files --eol -- path/to/file
# i/lf    w/crlf  attr/text=auto  path/to/file
```

`i/` describes the committed blob, `w/` the working-tree file, and `attr/`
the attributes that apply. `i/mixed` or `w/mixed` means both conventions
occur in one file. Run it without a path to survey the repository: a
working tree can hold CRLF and LF files side by side even though every
blob is LF, so an edit tool must decide per file, never per repository.

In Git Bash, `cat -A path/to/file | head` shows each carriage return as
`^M` before the `$` that marks a line end.

A byte-level check in PowerShell:

```powershell
$bytes = [System.IO.File]::ReadAllBytes($path)
$hasUtf8Bom = $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and
    $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
$text = [System.Text.Encoding]::UTF8.GetString($bytes)
$crlf = ([regex]::Matches($text, "`r`n")).Count
$lf = ([regex]::Matches($text, "(?<!`r)`n")).Count
"BOM=$hasUtf8Bom CRLF=$crlf LF=$lf"
```

## Git Line-Ending Conversion

`core.autocrlf=true` is equivalent to giving every file the attribute
`text=auto` and setting `core.eol=crlf`: text files are stored with LF in
the repository and checked out with CRLF. Git for Windows commonly
configures this. `core.autocrlf=input` converts CRLF to LF on commit but
does no conversion on checkout.

When an agent tool writes an LF file into such a working tree, `git add`
warns:

```text
warning: in the working copy of 'path/to/file', LF will be replaced by
CRLF the next time Git touches it
```

The commit is still normalized to LF; the warning says the working-tree
copy will change on the next checkout. It is noise, not damage, unless the
file must keep LF on disk, such as a shell script that a POSIX tool runs
from the working tree.

Repository attributes travel with the repository and override each
machine's `core.autocrlf`. A typical `.gitattributes`:

```gitattributes
*        text=auto
*.sh     text eol=lf
*.bat    text eol=crlf
*.cmd    text eol=crlf
*.png    binary
```

After adding or changing such rules, renormalize from a clean tree:

```bash
git add --renormalize .
git status
```

Commit the renormalization separately from content changes so reviewers
can read both. `core.safecrlf` makes Git check that a conversion is
reversible and can warn or refuse; Git notes that CRLF conversion carries a
slight risk of corrupting binary files mistaken for text.

Why the rules above matter:

- A shell script checked out with CRLF fails under Bash, so pin `*.sh` to
  LF.
- Batch files should be CRLF and plain ASCII; see
  [launchers](../porting-cli-tools/launchers.knack.md).
- Byte-exact fixtures, such as signed archives or recorded outputs, need
  `* -text` in a `.gitattributes` inside their folder.
- A tool that writes CRLF into a file that already has CRLF produces
  `\r\r\n`. In a test, a `.gitignore` line ending that way silently
  stopped matching; check the bytes after automated edits of
  configuration files.

## Preserve Endings and Encoding When Patching

Patch a file in five steps:

1. read the raw bytes;
2. record the BOM and the dominant line ending, and stop if endings are
   mixed;
3. decode and normalize to LF in memory;
4. make the edit, failing loudly when the anchor text is missing or
   ambiguous; and
5. restore the original line ending and BOM, then write bytes.

```python
from pathlib import Path

UTF8_BOM = b"\xef\xbb\xbf"


def patch_text(path: Path, old: str, new: str) -> None:
    """Replace exactly one occurrence, preserving BOM and line endings."""
    raw = path.read_bytes()
    bom = raw.startswith(UTF8_BOM)
    text = raw[len(UTF8_BOM):].decode("utf-8") if bom else raw.decode("utf-8")
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    if crlf and lf:
        raise ValueError(f"{path}: mixed endings ({crlf} CRLF, {lf} LF)")
    eol = "\r\n" if crlf else "\n"
    body = text.replace("\r\n", "\n")
    if body.count(old) != 1:
        raise ValueError(f"{path}: expected exactly one match")
    body = body.replace(old, new, 1)
    data = body.replace("\n", eol).encode("utf-8")
    path.write_bytes((UTF8_BOM if bom else b"") + data)
```

Pass `old` and `new` with LF line endings. Decoding errors are deliberate:
a file that is not valid UTF-8 needs a human decision about its encoding,
not a guess. Compare `git diff --stat` before and after; a patch that
touches only a few lines should not report the whole file as changed.

## Python Defaults

- Text mode reads with universal newlines, so CRLF silently becomes `\n`.
  It writes `\n` as `os.linesep`, which is CRLF on Windows. A
  `read_text()` and `write_text()` round trip can therefore convert an LF
  file to CRLF.
- Before Python 3.15, `open()` without `encoding=` used the locale
  encoding, often a legacy code page on Windows, unless UTF-8 Mode was on.
  PEP 686 makes UTF-8 the default from Python 3.15. Pass `encoding` anyway;
  the interpreter on the machine may be older.
- Use `read_bytes()` and `write_bytes()`, or `open(..., encoding="utf-8",
  newline="")`, when exact bytes matter.

## Console and Pipe Encoding

The console has input and output code pages, shown by `chcp`. On many
systems they are legacy pages, not UTF-8 (code page 65001). Text crossing a
pipe between programs can be re-encoded on the way. Characters outside the
code page may become a best-fit ASCII substitute, a question mark, or
mojibake, with no error. Prefer passing data through UTF-8 files instead of
pipes, and treat any non-ASCII text in an inline command as suspect.

## Mixed Endings Are a Smell

A file with both CRLF and LF lines was usually edited by two tools with
different defaults. Do not normalize it as a side effect of an unrelated
edit. Report it, decide the intended convention, and fix it in its own
commit, ideally by adding a `.gitattributes` rule.

## Review Checklist

- Were the file's encoding, BOM, and line endings observed before editing?
- Does the diff touch only the intended lines?
- Does `git ls-files --eol` show no new `mixed` entries?
- Are scripts that run under POSIX tools pinned to LF by attributes?
- Did any write path go through Windows PowerShell 5.1 redirection or
  Python text mode without an explicit encoding and newline policy?

## Further Information

- Git, [gitattributes: end-of-line conversion](https://git-scm.com/docs/gitattributes)
- Git, [git-config: `core.autocrlf`, `core.eol`, `core.safecrlf`](https://git-scm.com/docs/git-config)
- Git, [git-ls-files: `--eol`](https://git-scm.com/docs/git-ls-files)
- Python, [built-in `open()`: encoding and newline](https://docs.python.org/3/library/functions.html#open)
- Python, [PEP 686: Make UTF-8 mode default](https://peps.python.org/pep-0686/)
- Microsoft, [about_Character_Encoding](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding)
- Microsoft, [Console code pages](https://learn.microsoft.com/en-us/windows/console/console-code-pages)
