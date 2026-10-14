# Steam Install Layout

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion to find a Steam game's install folder, version, DLC,
or Workshop content from a script, or to read Steam's KeyValues (VDF)
files. Read the [Steam overview](overview.knack.md) first; its
evidence labels (documented, observed, inferred) apply here. Valve
documents none of the client files below for third parties, so treat
every layout detail as observed and parse defensively.

## The Steam Root

Steam Support gives the default game location as
`C:\Program Files (x86)\Steam\steamapps\common\` and lets players add
library folders on other drives (documented). Find the actual root from
the registry rather than assuming the default (observed values):

| Key | Value | Notes |
| --- | --- | --- |
| `HKCU\Software\Valve\Steam` | `SteamPath` | Lower case with forward slashes, such as `c:/program files (x86)/steam`; normalize before use |
| `HKCU\Software\Valve\Steam` | `SteamExe` | Full path of `steam.exe`, in the same form |
| `HKLM\SOFTWARE\WOW6432Node\Valve\Steam` | `InstallPath` | Backslashes and original case |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App <appid>` | `InstallLocation` | One game's folder, when present |

Paths read from `SteamPath` compare unequal to the same path in another
case unless the comparison ignores case, as Windows path comparisons
should. `HKCU\Software\Valve\Steam\Apps\<appid>` also holds `Installed`,
`Running`, and `Updating` values, and the parent key a `RunningAppID`
(observed). They reflect the client's view only; do not use them to prove
that a process is or is not yours.

## Libraries

`<root>\steamapps\libraryfolders.vdf` lists every library (observed).
Current clients write one numbered block per library:

```text
"libraryfolders"
{
	"0"
	{
		"path"		"C:\\Program Files (x86)\\Steam"
		"apps"
		{
			"9876540"		"1520000000"
		}
	}
	"1"
	{
		"path"		"D:\\SteamLibrary"
		"apps"
		{
		}
	}
}
```

Real files carry more keys per library, among them a label, a content
ID, and size tallies. The `apps` block maps each installed app ID to a
size in bytes (observed). Older clients wrote each library as a plain
string value instead of a block (community reports), so accept both
shapes. The client
rewrote this file within seconds of starting (observed): read it, never
edit it, and re-read it rather than caching it across sessions.

A game lives at `<library>\steamapps\common\<installdir>`, where
`installdir` comes from the app manifest, not from the store name.

## App Manifests

`<library>\steamapps\appmanifest_<appid>.acf` describes one installed app
(observed):

```text
"AppState"
{
	"appid"		"9876540"
	"name"		"Example Colony"
	"StateFlags"		"4"
	"installdir"		"Example Colony"
	"LastUpdated"		"1791000000"
	"LastPlayed"		"1791900000"
	"buildid"		"20000000"
	"TargetBuildID"		"0"
	"AutoUpdateBehavior"		"0"
	"AllowOtherDownloadsWhileRunning"		"0"
	"InstalledDepots"
	{
		"9876541"
		{
			"manifest"		"1234567890123456789"
			"size"		"1400000000"
		}
		"9876552"
		{
			"manifest"		"2345678901234567890"
			"size"		"120000000"
			"dlcappid"		"9876550"
		}
	}
	"UserConfig"
	{
		"language"		"english"
	}
}
```

| Key | Use |
| --- | --- |
| `installdir` | Folder name under `steamapps\common` |
| `buildid` | The installed build; record it with every result and baseline |
| `StateFlags` | Install state, a bit field; see below |
| `LastUpdated`, `LastPlayed` | Unix times in seconds; `LastPlayed` also moves for direct launches (observed) |
| `InstalledDepots` | Installed depots; a depot with `dlcappid` belongs to that DLC |
| `UserConfig` | The player's choices for this app, such as language |
| `LastOwner` | An account ID; never copy it |

Valve does not document the `StateFlags` bits. On the observed client,
538 of 562 manifests showed exactly `4`; 21 showed `6`, matching the
content log's `Update Required,Fully Installed`; and 3 showed `68` while
no game was running, so a flag can be stale (observed). The client's
`logs\content_log.txt` names the flags at each state change, for example
`Fully Installed,Update Queued,Update Running`. Require exactly 4 for the
app under test, treat any other value as "not settled", and wait or
report rather than test against it. Do not use the manifest to decide
whether the game is running.

DLC and expansions usually arrive as extra depots installed into the same
game folder, so the game's own layout decides where their files land
(observed). Inspect the folder; do not infer DLC presence from the store.

A game's own version file can lag the binary it ships with (observed: a
text version file one revision behind the version the game logged at
start-up). Record `buildid` and the version the game itself reports.

## Workshop Folders

Steamworks documents `ISteamUGC::GetItemInstallInfo` as the way a game
finds a subscribed item's folder. On disk (observed):

- `<library>\steamapps\workshop\content\<appid>\<itemid>\` holds each
  installed item;
- `<library>\steamapps\workshop\downloads\<appid>\` is staging; the
  client commits downloads from it into `content`; and
- `<library>\steamapps\workshop\appworkshop_<appid>.acf` lists installed
  items with sizes and update times, and, in a details block, the
  subscribing account's ID. Do not copy that block.

Each game's items sat in the library that holds the game, and one
uninstalled game's items remained on disk (observed), so the presence of
Workshop content does not prove the game is installed. The
[Mods and Workshop](workshop.knack.md) companion
covers why this folder is Steam's, not yours.

## Per-Account Data

`<root>\userdata\<account-id>\` holds per-account client configuration
and per-game cloud caches such as
`userdata\<account-id>\<appid>\remotecache.vdf` (observed). It is personal
data: read only what a task needs, and never copy it into a repository.

## Client Logs

`<root>\logs\` holds plain-text client logs (observed). Four help most:

| Log | What it records |
| --- | --- |
| `gameprocess_log.txt` | Each tracked process: app ID, process ID, full command line, and exit code |
| `content_log.txt` | App state changes, update scheduling, and Workshop commits |
| `cloud_log.txt` | Steam Cloud synchronization, file by file, with full paths |
| `gameoverlay_renderer.txt` | Overlay injection into game processes |

A launch and an exit in `gameprocess_log.txt` look like this (observed;
the first entry is one line, wrapped here):

```text
[2026-10-13 12:00:00] AppID 9876540 adding PID 4242 as a tracked process
""C:\Program Files (x86)\Steam\steamapps\common\Example Colony\ExampleColony.exe" -marker=run-42"
[2026-10-13 12:03:10] AppID 9876540 no longer tracking PID 4242, exit code 0
```

It is free forensic evidence of what actually reached the game, including
quoting. When several instances overlapped, their exits were logged
together at one time (observed), so do not time runs from it. These logs
contain user names, save names, and account paths; redact before quoting.

## The KeyValues Text Format

Steam's `.vdf` and `.acf` text files use Valve's KeyValues format. The
Valve Developer Community describes it as nested key-value pairs with
three control characters, `{`, `}`, and `"`. Quoted and unquoted tokens
are allowed; an unquoted token ends at whitespace, a brace, or a quote;
`//` begins a line comment; and escape sequences `\n`, `\t`, `\\`, and
`\"` exist but are optional in Valve's parser (documented). Steam's client
files use them: paths appear as `C:\\Program Files (x86)\\Steam`
(observed). The format also allows duplicate keys, `#include` and
`#base` directives, and `[$WIN32]`-style conditionals, none of which
appeared in the client files above.

Some Steam files, such as `appcache\appinfo.vdf`, are binary (observed);
a text parser fails on them. For Python, the community
[`vdf`](https://github.com/ValvePython/vdf) package, not a Valve product,
reads text and binary KeyValues and offers a mapper that keeps duplicate
keys. Without a dependency, this sketch handles the client's text files;
it folds keys to lower case for defensive lookups and rejects duplicates
and unbalanced blocks rather than guessing. It parsed all 572 app and
Workshop manifests in two libraries on the observed client:

```python
import re
import winreg
from pathlib import Path

_TOKEN = re.compile(
    r'\s+|//[^\n]*'             # whitespace and line comments: skipped
    r'|"((?:\\.|[^"\\])*)"'     # quoted token, with backslash escapes
    r'|([{}])'                  # block delimiters
    r'|([^\s{}"]+)')            # unquoted token
_ESCAPES = {"n": "\n", "t": "\t", "\\": "\\", '"': '"'}


def _unescape(text):
    return re.sub(r'\\(.)',
                  lambda m: _ESCAPES.get(m.group(1), m.group(0)), text)


def parse_vdf(text):
    """Parse text KeyValues into nested dicts with lower-cased keys."""
    root, stack, key, pos = {}, [], None, 0
    node = root
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if not m:
            raise ValueError(f"unexpected character at offset {pos}")
        pos = m.end()
        quoted, brace, bare = m.groups()
        if brace == "{":
            if key is None or key in node:
                raise ValueError(f"bad or duplicate block key at {pos}")
            node[key] = {}
            stack.append(node)
            node, key = node[key], None
        elif brace == "}":
            if key is not None or not stack:
                raise ValueError(f"unbalanced block at offset {pos}")
            node = stack.pop()
        elif quoted is not None or bare is not None:
            token = _unescape(quoted) if quoted is not None else bare
            if key is None:
                key = token.lower()
            elif key in node:
                raise ValueError(f"duplicate key {key!r}")
            else:
                node[key], key = token, None
    if key is not None or stack:
        raise ValueError("file ended inside a pair or block")
    return root


def steam_root():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r"Software\Valve\Steam") as k:
        return Path(winreg.QueryValueEx(k, "SteamPath")[0])


def library_paths(root):
    vdf = root / "steamapps" / "libraryfolders.vdf"
    folders = parse_vdf(vdf.read_text(encoding="utf-8"))["libraryfolders"]
    paths = [root]
    for key, entry in folders.items():
        if key.isdigit():                  # skip other top-level keys
            path = entry.get("path") if isinstance(entry, dict) else entry
            if path and Path(path) not in paths:
                paths.append(Path(path))
    return paths


def find_app(appid):
    """Return (install folder, AppState dict), or (None, None)."""
    for library in library_paths(steam_root()):
        acf = library / "steamapps" / f"appmanifest_{appid}.acf"
        if acf.is_file():
            state = parse_vdf(acf.read_text(encoding="utf-8"))["appstate"]
            return (library / "steamapps" / "common" / state["installdir"],
                    state)
    return None, None
```

`Path` equality on Windows ignores case, so the lower-case root and the
library list's spelling of it deduplicate. A PowerShell equivalent, tested
in Windows PowerShell 5.1 and PowerShell 7, reads only flat manifest keys
and only the current library-list shape:

```powershell
function Get-SteamApp {
    param([Parameter(Mandatory)][string] $AppId)
    $steam = (Get-ItemProperty 'HKCU:\Software\Valve\Steam' -ErrorAction Stop).SteamPath
    $steam = [IO.Path]::GetFullPath($steam)   # forward slashes to backslashes
    $vdf = Get-Content -LiteralPath (Join-Path $steam 'steamapps\libraryfolders.vdf') `
        -Raw -Encoding UTF8
    $libraries = @([regex]::Matches($vdf, '"path"\s+"((?:\\.|[^"\\])*)"') |
        ForEach-Object { $_.Groups[1].Value -replace '\\(.)', '$1' }) + $steam
    foreach ($library in $libraries) {
        $acf = Join-Path $library "steamapps\appmanifest_$AppId.acf"
        if (-not (Test-Path -LiteralPath $acf)) { continue }
        $text = Get-Content -LiteralPath $acf -Raw -Encoding UTF8
        $field = { param($name)
            if ($text -match "`"$name`"\s+`"([^`"]*)`"") { $Matches[1] } }
        return [pscustomobject]@{
            Library    = $library
            InstallDir = Join-Path $library ('steamapps\common\' + (& $field 'installdir'))
            BuildId    = & $field 'buildid'
            StateFlags = [int](& $field 'StateFlags')
        }
    }
}
```

The leading quote in each key pattern keeps `"buildid"` from matching
`"TargetBuildID"`. Both sketches return nothing for an app that is not
installed; callers must treat that as a failure, not as a default path.

## Paths With Spaces

Every default Steam path contains spaces and parentheses, and install
folder names add their own. Quote paths at every layer, avoid tools that
split on whitespace (such as `xargs` without `-0`), and verify what
arrived through the game's log or `gameprocess_log.txt`.
[Agent shells](../../windows/shells/overview.knack.md)
covers quoting through Git Bash and PowerShell.

## Review Checklist

- Is the Steam root read from the registry and normalized?
- Are all libraries considered, in both list shapes?
- Is `installdir` taken from the manifest rather than the store name?
- Does the script fail, rather than guess, when the app is not found or
  `StateFlags` is not 4?
- Are client files only read, never written?
- Are account IDs, user names, and save names kept out of anything
  copied from manifests, `userdata`, or logs?

## Further Information

- Steam Support,
  [Moving a Steam Installation and Games](https://help.steampowered.com/en/faqs/view/4BD4-4528-6B2E-8327)
- Valve Developer Community,
  [KeyValues](https://developer.valvesoftware.com/wiki/KeyValues)
- Valve, [ISteamUGC::GetItemInstallInfo](https://partner.steamgames.com/doc/api/ISteamUGC#GetItemInstallInfo)
- ValvePython community project,
  [`vdf` package](https://github.com/ValvePython/vdf)
