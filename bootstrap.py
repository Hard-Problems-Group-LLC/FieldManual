#!/usr/bin/env python3
"""Create the filesystem skeleton declared by FieldManual.

The bootstrap is intentionally self-contained and compatible with stock
Python 3.9 or newer. It performs no network, Git, package-management,
environment-management, hook, shell-profile, or user-home operations.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


MANIFEST_NAME = "FieldManual-layout.toml"
CONFIG_VERSION = 1
LAYOUT_VERSION = 1
CONFIG_KEYS = {
    "FieldManual_ConfigVersion",
    "FieldManual_FrameworkRoot",
    "FieldManual_ProjectRoot",
}
LAYOUT_KEYS = {
    "FieldManual_LayoutVersion",
    "required_directories",
    "private_directories",
    "template_roots",
    "template_files",
    "project_config_template",
    "local_config_template",
    "project_config_path",
    "local_config_path",
    "agents_header_template",
    "agents_footer_template",
    "agents_path",
    "gitignore_path",
    "gitignore_entries",
}
AGENTS_MARKERS = (
    "<!-- FIELDMANUAL_MANAGED_HEADER_START -->",
    "<!-- FIELDMANUAL_MANAGED_HEADER_END -->",
    "<!-- FIELDMANUAL_MANAGED_FOOTER_START -->",
    "<!-- FIELDMANUAL_MANAGED_FOOTER_END -->",
)
GITIGNORE_START = "# BEGIN FieldManual managed local state"
GITIGNORE_END = "# END FieldManual managed local state"
ROOT_PLACEHOLDERS = ("{{FIELDMANUAL_ROOT}}", "{$FIELDMANUAL_ROOT}")
TOML_ROOT_PLACEHOLDERS = (
    "{{FIELDMANUAL_ROOT_TOML}}",
    "{$FIELDMANUAL_ROOT_TOML}",
)
UNRESOLVED_PLACEHOLDER = re.compile(
    r"(?:\{\{FIELDMANUAL_[A-Z0-9_]+\}\}|\{\$FIELDMANUAL_[A-Z0-9_]+\})"
)
KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
INTEGER_PATTERN = re.compile(r"^[+-]?(?:0|[1-9][0-9]*)$")


ANCHORED_MUTATIONS_AVAILABLE = (
    os.name == "posix"
    and hasattr(os, "O_DIRECTORY")
    and hasattr(os, "O_NOFOLLOW")
    and os.open in os.supports_dir_fd
    and os.mkdir in os.supports_dir_fd
    and os.link in os.supports_dir_fd
    and os.rename in os.supports_dir_fd
    and os.unlink in os.supports_dir_fd
)


class BootstrapError(RuntimeError):
    """Report a configuration, layout, or safety-contract failure."""


@dataclass(frozen=True)
class Layout:
    """Hold the validated, framework-owned installation declaration."""

    required_directories: Tuple[str, ...]
    private_directories: frozenset
    template_roots: Tuple[str, ...]
    template_files: Tuple[str, ...]
    project_config_template: str
    local_config_template: str
    project_config_path: str
    local_config_path: str
    agents_header_template: str
    agents_footer_template: str
    agents_path: str
    gitignore_path: str
    gitignore_entries: Tuple[str, ...]


@dataclass(frozen=True)
class WriteOperation:
    """Describe one preflighted atomic file creation or managed update."""

    relative_path: str
    destination: Path
    content: bytes
    mode: int
    expected_exists: bool
    expected_content: Optional[bytes]
    managed_update: bool


@dataclass(frozen=True)
class DirectoryOperation:
    """Describe one preflighted directory creation."""

    relative_path: str
    destination: Path
    mode: int


class Plan:
    """Accumulate a fully validated, non-destructive bootstrap plan."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        root_status = project_root.stat()
        self.root_identity = (root_status.st_dev, root_status.st_ino)
        self.directories: List[DirectoryOperation] = []
        self.writes: List[WriteOperation] = []
        self.preserved_identical = 0
        self.preserved_different: List[str] = []
        self.preserved_managed = 0

    def add_directory(self, relative_path: str, destination: Path, mode: int) -> None:
        """Queue a directory that was absent during preflight."""

        self.directories.append(
            DirectoryOperation(
                relative_path=relative_path,
                destination=destination,
                mode=mode,
            )
        )

    def add_write(
        self,
        relative_path: str,
        destination: Path,
        content: bytes,
        mode: int,
        expected_exists: bool,
        expected_content: Optional[bytes],
        managed_update: bool,
    ) -> None:
        """Queue one file creation or managed replacement."""

        self.writes.append(
            WriteOperation(
                relative_path=relative_path,
                destination=destination,
                content=content,
                mode=mode,
                expected_exists=expected_exists,
                expected_content=expected_content,
                managed_update=managed_update,
            )
        )


def strip_toml_comment(line: str) -> str:
    """Remove a TOML-subset comment while respecting quoted strings."""

    quote: Optional[str] = None
    escaped = False
    for index, character in enumerate(line):
        if quote is not None:
            if quote == '"' and escaped:
                escaped = False
                continue
            if quote == '"' and character == "\\":
                escaped = True
                continue
            if character == quote:
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
            continue
        if character == "#":
            return line[:index]
    if quote is not None:
        raise BootstrapError("unterminated string in TOML input")
    return line


def bracket_balance(text: str) -> int:
    """Count array brackets outside quoted strings."""

    balance = 0
    quote: Optional[str] = None
    escaped = False
    for character in text:
        if quote is not None:
            if quote == '"' and escaped:
                escaped = False
                continue
            if quote == '"' and character == "\\":
                escaped = True
                continue
            if character == quote:
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
        elif character == "[":
            balance += 1
        elif character == "]":
            balance -= 1
            if balance < 0:
                return balance
    return balance


def find_assignment(text: str) -> int:
    """Locate the one assignment separator outside quoted strings."""

    quote: Optional[str] = None
    escaped = False
    for index, character in enumerate(text):
        if quote is not None:
            if quote == '"' and escaped:
                escaped = False
                continue
            if quote == '"' and character == "\\":
                escaped = True
                continue
            if character == quote:
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
        elif character == "=":
            return index
    return -1


def split_array_items(value: str) -> List[str]:
    """Split a subset array into scalar tokens without losing quoted commas."""

    inner = value[1:-1].strip()
    if not inner:
        return []

    items: List[str] = []
    start = 0
    quote: Optional[str] = None
    escaped = False
    for index, character in enumerate(inner):
        if quote is not None:
            if quote == '"' and escaped:
                escaped = False
                continue
            if quote == '"' and character == "\\":
                escaped = True
                continue
            if character == quote:
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
        elif character == ",":
            token = inner[start:index].strip()
            if not token:
                raise BootstrapError("empty item in TOML array")
            items.append(token)
            start = index + 1

    if quote is not None:
        raise BootstrapError("unterminated string in TOML array")
    tail = inner[start:].strip()
    if tail:
        items.append(tail)
    elif not inner.rstrip().endswith(","):
        raise BootstrapError("empty final item in TOML array")
    return items


def parse_basic_toml_string(token: str) -> str:
    """Parse a single-line TOML basic string without accepting JSON extensions."""

    if len(token) < 2 or not token.endswith('"'):
        raise BootstrapError("invalid double-quoted TOML string")
    result: List[str] = []
    escapes = {
        "b": "\b",
        "t": "\t",
        "n": "\n",
        "f": "\f",
        "r": "\r",
        '"': '"',
        "\\": "\\",
    }
    index = 1
    end = len(token) - 1
    while index < end:
        character = token[index]
        if character == '"':
            raise BootstrapError("unescaped quote in double-quoted TOML string")
        if character != "\\":
            if ord(character) < 0x20 and character != "\t":
                raise BootstrapError("control character in TOML string")
            result.append(character)
            index += 1
            continue

        index += 1
        if index >= end:
            raise BootstrapError("incomplete escape in TOML string")
        escape = token[index]
        if escape in escapes:
            result.append(escapes[escape])
            index += 1
            continue
        if escape not in {"u", "U"}:
            raise BootstrapError(f"unsupported TOML string escape '\\{escape}'")
        digits = 4 if escape == "u" else 8
        encoded = token[index + 1 : index + 1 + digits]
        if len(encoded) != digits or not all(
            character in "0123456789abcdefABCDEF" for character in encoded
        ):
            raise BootstrapError("malformed Unicode escape in TOML string")
        codepoint = int(encoded, 16)
        if codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
            raise BootstrapError("invalid Unicode scalar in TOML string")
        result.append(chr(codepoint))
        index += digits + 1
    return "".join(result)


def parse_toml_value(value: str) -> Any:
    """Parse one value from FieldManual's documented TOML subset."""

    token = value.strip()
    if not token:
        raise BootstrapError("missing TOML value")
    if token.startswith("["):
        if not token.endswith("]") or bracket_balance(token) != 0:
            raise BootstrapError("malformed TOML array")
        parsed_items = [
            parse_toml_value(item) for item in split_array_items(token)
        ]
        if any(isinstance(item, list) for item in parsed_items):
            raise BootstrapError("nested TOML arrays are not supported")
        return parsed_items
    if token.startswith('"'):
        return parse_basic_toml_string(token)
    if token.startswith("'"):
        if len(token) < 2 or not token.endswith("'") or "'" in token[1:-1]:
            raise BootstrapError("invalid single-quoted TOML string")
        parsed = token[1:-1]
        if any(ord(character) < 0x20 and character != "\t" for character in parsed):
            raise BootstrapError("control character in TOML string")
        return parsed
    if token == "true":
        return True
    if token == "false":
        return False
    if INTEGER_PATTERN.fullmatch(token):
        return int(token, 10)
    raise BootstrapError(
        "unsupported TOML value; use a string, integer, boolean, or array"
    )


def parse_toml_lines(lines: Sequence[str], source: Path) -> Dict[str, Any]:
    """Parse lines from a strict, version-independent TOML subset."""

    values: Dict[str, Any] = {}
    folded_keys: Set[str] = set()
    statement = ""
    statement_line = 0

    for line_number, raw_line in enumerate(lines, start=1):
        try:
            cleaned = strip_toml_comment(raw_line).strip()
        except BootstrapError as error:
            raise BootstrapError(f"{source}:{line_number}: {error}") from error
        if not cleaned:
            continue
        if statement:
            statement = f"{statement} {cleaned}"
        else:
            statement = cleaned
            statement_line = line_number

        balance = bracket_balance(statement)
        if balance > 0:
            continue
        if balance < 0:
            raise BootstrapError(
                f"{source}:{statement_line}: unexpected closing array bracket"
            )

        separator = find_assignment(statement)
        if separator < 1:
            raise BootstrapError(
                f"{source}:{statement_line}: expected a top-level key assignment"
            )
        key = statement[:separator].strip()
        raw_value = statement[separator + 1 :].strip()
        if not KEY_PATTERN.fullmatch(key):
            raise BootstrapError(
                f"{source}:{statement_line}: unsupported or malformed key '{key}'"
            )
        folded = key.casefold()
        if folded in folded_keys:
            raise BootstrapError(
                f"{source}:{statement_line}: duplicate or case-colliding key '{key}'"
            )
        try:
            values[key] = parse_toml_value(raw_value)
        except BootstrapError as error:
            raise BootstrapError(f"{source}:{statement_line}: {error}") from error
        folded_keys.add(folded)
        statement = ""

    if statement:
        raise BootstrapError(
            f"{source}:{statement_line}: unterminated multiline TOML value"
        )
    return values


def parse_toml_subset(path: Path) -> Dict[str, Any]:
    """Load a strict, version-independent subset of a TOML document."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeError as error:
        raise BootstrapError(f"{path}: expected UTF-8 text") from error
    return parse_toml_lines(lines, path)


def require_exact_keys(values: Dict[str, Any], expected: Set[str], path: Path) -> None:
    """Reject missing and unknown keys in a versioned FieldManual document."""

    missing = sorted(expected - set(values))
    unknown = sorted(set(values) - expected)
    details: List[str] = []
    if missing:
        details.append("missing " + ", ".join(missing))
    if unknown:
        details.append("unknown " + ", ".join(unknown))
    if details:
        raise BootstrapError(f"{path}: invalid keys ({'; '.join(details)})")


def require_string(values: Dict[str, Any], key: str, path: Path) -> str:
    """Return one required nonempty string value."""

    value = values[key]
    if not isinstance(value, str) or not value:
        raise BootstrapError(f"{path}: {key} must be a nonempty string")
    return value


def require_string_list(
    values: Dict[str, Any],
    key: str,
    path: Path,
) -> Tuple[str, ...]:
    """Return one required array containing only nonempty strings."""

    value = values[key]
    if not isinstance(value, list):
        raise BootstrapError(f"{path}: {key} must be an array of strings")
    result: List[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            raise BootstrapError(
                f"{path}: {key}[{index}] must be a nonempty string"
            )
        result.append(item)
    return tuple(result)


def validate_relative_path(value: str, label: str) -> str:
    """Validate one portable project- or template-relative path."""

    if "\x00" in value or "\\" in value:
        raise BootstrapError(f"{label}: path must use portable forward slashes")
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise BootstrapError(f"{label}: absolute paths are not allowed")
    components = value.split("/")
    if not components or any(component in {"", ".", ".."} for component in components):
        raise BootstrapError(f"{label}: empty, '.' and '..' components are forbidden")
    if any(":" in component for component in components):
        raise BootstrapError(f"{label}: ':' is not portable in declared paths")
    return "/".join(components)


def validate_config(values: Dict[str, Any], path: Path) -> Dict[str, Any]:
    """Validate a tracked or local root-configuration mapping."""

    require_exact_keys(values, CONFIG_KEYS, path)
    version = values["FieldManual_ConfigVersion"]
    if isinstance(version, bool) or not isinstance(version, int):
        raise BootstrapError(f"{path}: FieldManual_ConfigVersion must be an integer")
    if version != CONFIG_VERSION:
        raise BootstrapError(
            f"{path}: unsupported FieldManual_ConfigVersion {version}"
        )
    require_string(values, "FieldManual_FrameworkRoot", path)
    require_string(values, "FieldManual_ProjectRoot", path)
    return values


def load_layout(framework_root: Path) -> Layout:
    """Load and validate the explicit framework filesystem contract."""

    manifest_path = framework_root / MANIFEST_NAME
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise BootstrapError(f"missing regular framework manifest: {manifest_path}")
    values = parse_toml_subset(manifest_path)
    require_exact_keys(values, LAYOUT_KEYS, manifest_path)

    version = values["FieldManual_LayoutVersion"]
    if isinstance(version, bool) or not isinstance(version, int):
        raise BootstrapError(
            f"{manifest_path}: FieldManual_LayoutVersion must be an integer"
        )
    if version != LAYOUT_VERSION:
        raise BootstrapError(
            f"{manifest_path}: unsupported FieldManual_LayoutVersion {version}"
        )

    required = require_string_list(
        values, "required_directories", manifest_path
    )
    private = require_string_list(values, "private_directories", manifest_path)
    template_roots = require_string_list(
        values, "template_roots", manifest_path
    )
    templates = require_string_list(values, "template_files", manifest_path)
    gitignore_entries = require_string_list(
        values, "gitignore_entries", manifest_path
    )
    scalar_keys = (
        "project_config_template",
        "local_config_template",
        "project_config_path",
        "local_config_path",
        "agents_header_template",
        "agents_footer_template",
        "agents_path",
        "gitignore_path",
    )
    scalars = {
        key: require_string(values, key, manifest_path) for key in scalar_keys
    }

    required = tuple(
        validate_relative_path(item, f"{manifest_path}: required_directories")
        for item in required
    )
    private = tuple(
        validate_relative_path(item, f"{manifest_path}: private_directories")
        for item in private
    )
    template_roots = tuple(
        validate_relative_path(item, f"{manifest_path}: template_roots")
        for item in template_roots
    )
    templates = tuple(
        validate_relative_path(item, f"{manifest_path}: template_files")
        for item in templates
    )
    for key, item in list(scalars.items()):
        scalars[key] = validate_relative_path(item, f"{manifest_path}: {key}")

    ensure_unique_paths(required, "required directories", manifest_path)
    ensure_unique_paths(private, "private directories", manifest_path)
    ensure_unique_paths(template_roots, "template roots", manifest_path)
    ensure_unique_paths(templates, "template files", manifest_path)
    if not set(private).issubset(set(required)):
        raise BootstrapError(
            f"{manifest_path}: every private directory must also be required"
        )

    required_folded = {item.casefold() for item in required}
    if not template_roots:
        raise BootstrapError(f"{manifest_path}: template_roots cannot be empty")
    for template_root in template_roots:
        if template_root.casefold() not in required_folded:
            raise BootstrapError(
                f"{manifest_path}: template root is not a required directory: "
                f"{template_root}"
            )
    for directory in required:
        parent = directory.rpartition("/")[0]
        if parent and parent.casefold() not in required_folded:
            raise BootstrapError(
                f"{manifest_path}: required directory parent is not declared: "
                f"{directory}"
            )

    file_destinations = list(templates) + [
        scalars["project_config_path"],
        scalars["local_config_path"],
        scalars["agents_path"],
        scalars["gitignore_path"],
    ]
    ensure_unique_paths(file_destinations, "file destinations", manifest_path)
    for file_path in file_destinations:
        if file_path.casefold() in required_folded:
            raise BootstrapError(
                f"{manifest_path}: path is both a file and directory: {file_path}"
            )
        file_prefix = file_path.casefold() + "/"
        descendant_directory = next(
            (
                directory
                for directory in required
                if directory.casefold().startswith(file_prefix)
            ),
            None,
        )
        if descendant_directory is not None:
            raise BootstrapError(
                f"{manifest_path}: file destination {file_path!r} is an ancestor "
                f"of required directory {descendant_directory!r}"
            )
    for index, file_path in enumerate(file_destinations):
        file_prefix = file_path.casefold() + "/"
        descendant_file = next(
            (
                other
                for other in file_destinations[index + 1 :]
                if other.casefold().startswith(file_prefix)
                or file_path.casefold().startswith(other.casefold() + "/")
            ),
            None,
        )
        if descendant_file is not None:
            raise BootstrapError(
                f"{manifest_path}: file destinations cannot contain one another: "
                f"{file_path!r} and {descendant_file!r}"
            )

    for template in templates:
        if not any(
            template.casefold().startswith(root.casefold() + "/")
            for root in template_roots
        ):
            raise BootstrapError(
                f"{manifest_path}: template is outside allowed template roots: "
                f"{template}"
            )
        parent = template.rpartition("/")[0]
        if parent and parent.casefold() not in required_folded:
            raise BootstrapError(
                f"{manifest_path}: template parent is not a required directory: "
                f"{template}"
            )
    for special_path in (
        scalars["local_config_path"],
        scalars["agents_path"],
        scalars["gitignore_path"],
        scalars["project_config_path"],
    ):
        parent = special_path.rpartition("/")[0]
        if parent and parent.casefold() not in required_folded:
            raise BootstrapError(
                f"{manifest_path}: file parent is not a required directory: "
                f"{special_path}"
            )

    if not gitignore_entries:
        raise BootstrapError(f"{manifest_path}: gitignore_entries cannot be empty")
    if any(
        "\n" in entry or "\r" in entry or not entry.strip()
        for entry in gitignore_entries
    ):
        raise BootstrapError(
            f"{manifest_path}: gitignore entries must be nonempty single lines"
        )
    if len({entry.casefold() for entry in gitignore_entries}) != len(
        gitignore_entries
    ):
        raise BootstrapError(
            f"{manifest_path}: duplicate or case-colliding gitignore entries"
        )

    return Layout(
        required_directories=required,
        private_directories=frozenset(private),
        template_roots=template_roots,
        template_files=templates,
        project_config_template=scalars["project_config_template"],
        local_config_template=scalars["local_config_template"],
        project_config_path=scalars["project_config_path"],
        local_config_path=scalars["local_config_path"],
        agents_header_template=scalars["agents_header_template"],
        agents_footer_template=scalars["agents_footer_template"],
        agents_path=scalars["agents_path"],
        gitignore_path=scalars["gitignore_path"],
        gitignore_entries=gitignore_entries,
    )


def ensure_unique_paths(paths: Sequence[str], label: str, source: Path) -> None:
    """Reject exact and case-folded path collisions for portability."""

    seen: Dict[str, str] = {}
    for path in paths:
        folded = path.casefold()
        previous = seen.get(folded)
        if previous is not None:
            raise BootstrapError(
                f"{source}: duplicate or case-colliding {label}: "
                f"{previous!r} and {path!r}"
            )
        seen[folded] = path


def is_within(path: Path, root: Path) -> bool:
    """Return whether a canonical path is equal to or below a root."""

    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def validate_actual_placement(project_root: Path, framework_root: Path) -> None:
    """Enforce self-maintenance or strict in-project framework placement."""

    if framework_root == project_root:
        return
    if not is_within(framework_root, project_root):
        raise BootstrapError(
            "FieldManual_FrameworkRoot must equal FieldManual_ProjectRoot while "
            "maintaining FieldManual, or be a strict descendant in a consuming "
            "project"
        )


def discover_project_root(
    framework_root: Path, layout: Layout, explicit: Optional[Path]
) -> Path:
    """Choose a project root without relying on the ambient working directory."""

    if explicit is not None:
        candidate = explicit.expanduser()
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as error:
            raise BootstrapError(
                f"--project-root does not resolve to an existing directory: {candidate}"
            ) from error
        if not resolved.is_dir():
            raise BootstrapError(f"--project-root is not a directory: {resolved}")
        return resolved

    for candidate in framework_root.parents:
        config_path = candidate / layout.project_config_path
        if config_path.is_symlink():
            raise BootstrapError(
                f"refusing symlinked parent FieldManual configuration: {config_path}"
            )
        if config_path.is_file():
            return candidate.resolve(strict=True)

    git_marker = framework_root / ".git"
    if git_marker.is_file():
        for candidate in framework_root.parents:
            if (candidate / ".git").exists():
                return candidate.resolve(strict=True)
        raise BootstrapError(
            "FieldManual appears to be in a worktree or submodule, but no project "
            "root can be inferred; pass --project-root explicitly"
        )

    return framework_root


def relative_framework_value(project_root: Path, framework_root: Path) -> str:
    """Render the canonical framework path stored in generated configurations."""

    if project_root == framework_root:
        return "."
    return framework_root.relative_to(project_root).as_posix()


def resolve_configured_root(value: str, project_root: Path, key: str) -> Path:
    """Resolve one configured root against the tracked project directory."""

    if "\x00" in value:
        raise BootstrapError(f"{key} contains a NUL character")
    configured = Path(value)
    if not configured.is_absolute():
        configured = project_root / configured
    try:
        resolved = configured.resolve(strict=True)
    except OSError as error:
        raise BootstrapError(
            f"{key} does not resolve to an existing path: {value}"
        ) from error
    if not resolved.is_dir():
        raise BootstrapError(f"{key} does not resolve to a directory: {value}")
    return resolved


def validate_effective_roots(
    values: Dict[str, Any], project_root: Path, framework_root: Path
) -> None:
    """Ensure configuration identifies the selected project and running manual."""

    configured_project = resolve_configured_root(
        values["FieldManual_ProjectRoot"],
        project_root,
        "FieldManual_ProjectRoot",
    )
    configured_framework = resolve_configured_root(
        values["FieldManual_FrameworkRoot"],
        project_root,
        "FieldManual_FrameworkRoot",
    )
    if configured_project != project_root:
        raise BootstrapError(
            "FieldManual_ProjectRoot disagrees with the selected project root: "
            f"{configured_project} != {project_root}"
        )
    if configured_framework != framework_root:
        raise BootstrapError(
            "FieldManual_FrameworkRoot disagrees with the running bootstrap: "
            f"{configured_framework} != {framework_root}"
        )
    validate_actual_placement(configured_project, configured_framework)


def target_path(project_root: Path, relative_path: str) -> Path:
    """Return a confined destination after rejecting symlink traversal."""

    destination = project_root.joinpath(*relative_path.split("/"))
    current = project_root
    components = relative_path.split("/")
    for index, component in enumerate(components):
        current = current / component
        if current.is_symlink():
            raise BootstrapError(
                f"destination traversal through symlink is forbidden: {current}"
            )
        if current.exists() and index < len(components) - 1 and not current.is_dir():
            raise BootstrapError(
                f"destination parent is not a directory: {current}"
            )
    canonical = destination.resolve(strict=False)
    if not is_within(canonical, project_root):
        raise BootstrapError(f"destination escapes project root: {relative_path}")
    return destination


def source_path(templates_root: Path, relative_path: str) -> Path:
    """Return one explicit regular template without following symlinks."""

    source = templates_root.joinpath(*relative_path.split("/"))
    current = templates_root
    for component in relative_path.split("/"):
        current = current / component
        if current.is_symlink():
            raise BootstrapError(
                f"template traversal through symlink is forbidden: {current}"
            )
    if not source.is_file():
        raise BootstrapError(f"declared template is not a regular file: {source}")
    canonical_root = templates_root.resolve(strict=True)
    canonical_source = source.resolve(strict=True)
    if not is_within(canonical_source, canonical_root):
        raise BootstrapError(f"template escapes framework template root: {source}")
    return source


def render_template(source: Path, framework_value: str) -> bytes:
    """Render only the allowlisted FieldManual root placeholder."""

    try:
        text = source.read_text(encoding="utf-8")
    except UnicodeError as error:
        raise BootstrapError(f"template must be UTF-8 text: {source}") from error
    toml_value = json.dumps(framework_value, ensure_ascii=False)[1:-1]
    for placeholder in TOML_ROOT_PLACEHOLDERS:
        text = text.replace(placeholder, toml_value)
    for placeholder in ROOT_PLACEHOLDERS:
        text = text.replace(placeholder, framework_value)
    unresolved = UNRESOLVED_PLACEHOLDER.search(text)
    if unresolved is not None:
        raise BootstrapError(
            f"unresolved FieldManual placeholder in {source}: {unresolved.group(0)}"
        )
    return text.encode("utf-8")


def read_existing_file(path: Path, label: str) -> Optional[bytes]:
    """Read a destination file, rejecting directories and symlinks."""

    if path.is_symlink():
        raise BootstrapError(f"refusing symlinked {label}: {path}")
    if not path.exists():
        return None
    if not path.is_file():
        raise BootstrapError(f"{label} is not a regular file: {path}")
    return path.read_bytes()


def add_create_only_file(
    plan: Plan,
    relative_path: str,
    destination: Path,
    content: bytes,
    mode: int = 0o644,
) -> None:
    """Create a missing skeleton and preserve every existing regular file."""

    existing = read_existing_file(destination, "create-only destination")
    if existing is None:
        plan.add_write(
            relative_path,
            destination,
            content,
            mode,
            expected_exists=False,
            expected_content=None,
            managed_update=False,
        )
    elif existing == content:
        plan.preserved_identical += 1
    else:
        plan.preserved_different.append(relative_path)


def decode_utf8(content: bytes, path: Path) -> str:
    """Decode a managed text destination with an actionable error."""

    try:
        return content.decode("utf-8")
    except UnicodeError as error:
        raise BootstrapError(f"managed file must be UTF-8 text: {path}") from error


def managed_intervals(content: str, path: Path) -> List[Tuple[int, int, str]]:
    """Validate and locate optional prior AGENTS managed sections."""

    header_start, header_end, footer_start, footer_end = AGENTS_MARKERS
    pairs = (
        (header_start, header_end, "header"),
        (footer_start, footer_end, "footer"),
    )
    intervals: List[Tuple[int, int, str]] = []
    for start_marker, end_marker, label in pairs:
        start_count = content.count(start_marker)
        end_count = content.count(end_marker)
        if start_count == 0 and end_count == 0:
            continue
        if start_count != 1 or end_count != 1:
            raise BootstrapError(
                f"{path}: malformed or duplicate FieldManual {label} markers"
            )
        start = content.index(start_marker)
        end_start = content.index(end_marker)
        if end_start < start:
            raise BootstrapError(
                f"{path}: FieldManual {label} end marker precedes start marker"
            )
        intervals.append((start, end_start + len(end_marker), label))

    labels = {item[2] for item in intervals}
    if labels not in (set(), {"header", "footer"}):
        raise BootstrapError(
            f"{path}: managed AGENTS header and footer must both be present"
        )

    intervals.sort(key=lambda item: item[0])
    for previous, current in zip(intervals, intervals[1:]):
        if previous[1] > current[0]:
            raise BootstrapError(f"{path}: overlapping FieldManual managed sections")
        if previous[2] == "footer" and current[2] == "header":
            raise BootstrapError(f"{path}: managed footer precedes managed header")
    return intervals


def build_agents_content(
    existing: Optional[bytes],
    destination: Path,
    header: str,
    footer: str,
) -> bytes:
    """Wrap the preserved project body in refreshed managed sections."""

    header_start, header_end, footer_start, footer_end = AGENTS_MARKERS
    if header.count(header_start) != 1 or header.count(header_end) != 1:
        raise BootstrapError("AGENTS header template must contain one marker pair")
    if footer.count(footer_start) != 1 or footer.count(footer_end) != 1:
        raise BootstrapError("AGENTS footer template must contain one marker pair")
    if header.index(header_start) > header.index(header_end):
        raise BootstrapError("AGENTS header template markers are misordered")
    if footer.index(footer_start) > footer.index(footer_end):
        raise BootstrapError("AGENTS footer template markers are misordered")
    if footer_start in header or footer_end in header:
        raise BootstrapError("AGENTS header template contains footer markers")
    if header_start in footer or header_end in footer:
        raise BootstrapError("AGENTS footer template contains header markers")

    current = "" if existing is None else decode_utf8(existing, destination)
    intervals = managed_intervals(current, destination)
    body = current
    if intervals:
        header_interval, footer_interval = intervals
        prefix = current[: header_interval[0]]
        between = current[header_interval[1] : footer_interval[0]]
        suffix = current[footer_interval[1] :]

        # Remove only separators written by this function. Project-owned
        # whitespace inside the wrapped body remains byte-for-byte intact.
        if between.startswith("\n\n"):
            between = between[2:]
        if between.endswith("\n\n"):
            between = between[:-2]
        if suffix.startswith("\n"):
            suffix = suffix[1:]
        body = prefix + between + suffix

    sections = [header.strip("\r\n")]
    if body:
        sections.append(body)
    sections.append(footer.strip("\r\n"))
    return ("\n\n".join(sections) + "\n").encode("utf-8")


def build_gitignore_content(
    existing: Optional[bytes],
    destination: Path,
    entries: Sequence[str],
) -> bytes:
    """Ensure required ignores while preserving every unmanaged line."""

    current = "" if existing is None else decode_utf8(existing, destination)
    start_count = current.count(GITIGNORE_START)
    end_count = current.count(GITIGNORE_END)
    if start_count != end_count or start_count > 1:
        raise BootstrapError(
            f"{destination}: malformed or duplicate FieldManual gitignore markers"
        )

    newline = "\r\n" if "\r\n" in current else "\n"
    block = newline.join((GITIGNORE_START, *entries, GITIGNORE_END))
    if start_count == 1:
        start = current.index(GITIGNORE_START)
        end_start = current.index(GITIGNORE_END)
        if end_start < start:
            raise BootstrapError(
                f"{destination}: FieldManual gitignore end marker precedes start"
            )
        end = end_start + len(GITIGNORE_END)
        updated = current[:start] + block + current[end:]
        if current.endswith(("\n", "\r")) and not updated.endswith(("\n", "\r")):
            updated += newline
        if not gitignore_entries_effective(updated, entries):
            raise BootstrapError(
                f"{destination}: project-authored rules after the managed block "
                "negate a required FieldManual ignore"
            )
        return updated.encode("utf-8")

    if gitignore_entries_effective(current, entries):
        return current.encode("utf-8")

    if not current:
        updated = f"{block}{newline}"
    elif current.endswith(newline + newline):
        updated = f"{current}{block}{newline}"
    elif current.endswith(newline):
        updated = f"{current}{newline}{block}{newline}"
    else:
        updated = f"{current}{newline}{newline}{block}{newline}"
    return updated.encode("utf-8")


def gitignore_entries_effective(content: str, entries: Sequence[str]) -> bool:
    """Check exact required lines while respecting later exact negations."""

    states = {entry: False for entry in entries}
    for line in content.splitlines():
        rule = line.strip()
        if not rule or rule.startswith("#"):
            continue
        if rule in states:
            states[rule] = True
        elif rule.startswith("!") and rule[1:] in states:
            states[rule[1:]] = False
    return all(states.values())


def plan_managed_file(
    plan: Plan,
    relative_path: str,
    destination: Path,
    content: bytes,
    existing: Optional[bytes],
    mode: int = 0o644,
) -> None:
    """Queue a managed creation or update only when bytes differ."""

    if existing == content:
        plan.preserved_managed += 1
        return
    plan.add_write(
        relative_path,
        destination,
        content,
        mode,
        expected_exists=existing is not None,
        expected_content=existing,
        managed_update=existing is not None,
    )


def load_or_plan_configuration(
    plan: Plan,
    layout: Layout,
    templates_root: Path,
    project_root: Path,
    framework_root: Path,
) -> Dict[str, Any]:
    """Validate existing configs or plan complete tracked and local skeletons."""

    framework_value = relative_framework_value(project_root, framework_root)
    specifications = (
        (
            layout.project_config_path,
            layout.project_config_template,
            0o644,
            "tracked FieldManual configuration",
        ),
        (
            layout.local_config_path,
            layout.local_config_template,
            0o600,
            "local FieldManual configuration",
        ),
    )
    loaded: List[Dict[str, Any]] = []
    local_config_existed = False
    for relative_path, template_name, mode, label in specifications:
        destination = target_path(project_root, relative_path)
        source = source_path(templates_root, template_name)
        rendered = render_template(source, framework_value)
        existing = read_existing_file(destination, label)
        if relative_path == layout.local_config_path:
            local_config_existed = existing is not None
        if existing is None:
            try:
                rendered_text = rendered.decode("utf-8")
            except UnicodeError as error:
                raise BootstrapError(
                    f"configuration template is not UTF-8: {source}"
                ) from error
            values = parse_toml_text_for_validation(rendered_text, source)
            add_create_only_file(plan, relative_path, destination, rendered, mode)
        else:
            values = parse_toml_subset(destination)
            plan.preserved_identical += 1
        loaded.append(validate_config(values, destination))

    # A generated local file must not silently repair a stale tracked config.
    # An existing local file, however, is specifically allowed to override
    # checkout-dependent root values from the distributed configuration.
    if not local_config_existed:
        validate_effective_roots(loaded[0], project_root, framework_root)
    effective = dict(loaded[0])
    effective.update(loaded[1])
    validate_effective_roots(effective, project_root, framework_root)
    return effective


def parse_toml_text_for_validation(text: str, source: Path) -> Dict[str, Any]:
    """Validate rendered TOML through the same parser without filesystem writes."""

    return parse_toml_lines(text.splitlines(), source)


def build_plan(
    layout: Layout,
    project_root: Path,
    framework_root: Path,
) -> Plan:
    """Preflight the complete declared layout before the first write."""

    templates_root = framework_root / "templates"
    if templates_root.is_symlink() or not templates_root.is_dir():
        raise BootstrapError(f"missing regular template directory: {templates_root}")

    plan = Plan(project_root)
    for relative_path in layout.required_directories:
        destination = target_path(project_root, relative_path)
        if destination.exists():
            if not destination.is_dir():
                raise BootstrapError(
                    f"required directory collides with non-directory: {destination}"
                )
            continue
        mode = 0o700 if relative_path in layout.private_directories else 0o755
        plan.add_directory(relative_path, destination, mode)

    load_or_plan_configuration(
        plan=plan,
        layout=layout,
        templates_root=templates_root,
        project_root=project_root,
        framework_root=framework_root,
    )
    framework_value = relative_framework_value(project_root, framework_root)

    for relative_path in layout.template_files:
        source = source_path(templates_root, relative_path)
        destination = target_path(project_root, relative_path)
        content = render_template(source, framework_value)
        add_create_only_file(plan, relative_path, destination, content)

    header_source = source_path(templates_root, layout.agents_header_template)
    footer_source = source_path(templates_root, layout.agents_footer_template)
    header = render_template(header_source, framework_value).decode("utf-8")
    footer = render_template(footer_source, framework_value).decode("utf-8")
    agents_destination = target_path(project_root, layout.agents_path)
    agents_existing = read_existing_file(agents_destination, "AGENTS destination")
    agents_content = build_agents_content(
        agents_existing,
        agents_destination,
        header,
        footer,
    )
    plan_managed_file(
        plan,
        layout.agents_path,
        agents_destination,
        agents_content,
        agents_existing,
    )

    gitignore_destination = target_path(project_root, layout.gitignore_path)
    gitignore_existing = read_existing_file(
        gitignore_destination, ".gitignore destination"
    )
    gitignore_content = build_gitignore_content(
        gitignore_existing,
        gitignore_destination,
        layout.gitignore_entries,
    )
    plan_managed_file(
        plan,
        layout.gitignore_path,
        gitignore_destination,
        gitignore_content,
        gitignore_existing,
    )
    return plan


def directory_open_flags() -> int:
    """Return flags for opening an anchored directory without following links."""

    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    return flags


def open_project_anchor(plan: Plan) -> int:
    """Open and identity-check the project root used for anchored mutations."""

    try:
        descriptor = os.open(str(plan.project_root), directory_open_flags())
    except OSError as error:
        raise BootstrapError(
            f"could not anchor project root safely: {plan.project_root}"
        ) from error
    status = os.fstat(descriptor)
    if (status.st_dev, status.st_ino) != plan.root_identity:
        os.close(descriptor)
        raise BootstrapError(
            f"project root changed after preflight: {plan.project_root}"
        )
    return descriptor


def open_anchored_parent(
    project_descriptor: int,
    relative_path: str,
) -> Tuple[int, str]:
    """Open a destination parent component-by-component without symlinks."""

    components = relative_path.split("/")
    current = os.dup(project_descriptor)
    try:
        for component in components[:-1]:
            following = os.open(
                component,
                directory_open_flags(),
                dir_fd=current,
            )
            os.close(current)
            current = following
    except OSError as error:
        os.close(current)
        raise BootstrapError(
            f"destination parent changed or is unsafe: {relative_path}"
        ) from error
    return current, components[-1]


def read_anchored_file(
    parent_descriptor: int,
    name: str,
    display_path: Path,
) -> Optional[bytes]:
    """Read a regular file by directory descriptor without following symlinks."""

    flags = os.O_RDONLY | os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    try:
        descriptor = os.open(name, flags, dir_fd=parent_descriptor)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise BootstrapError(
            f"destination changed type or became unsafe: {display_path}"
        ) from error

    try:
        status = os.fstat(descriptor)
        if not stat.S_ISREG(status.st_mode):
            raise BootstrapError(
                f"destination is not a regular file: {display_path}"
            )
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = -1
            return handle.read()
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def create_anchored_temporary(
    parent_descriptor: int,
    destination_name: str,
    mode: int,
) -> Tuple[int, str]:
    """Create an exclusive same-directory temporary file by anchored name."""

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    for _attempt in range(16):
        name = (
            f".{destination_name}.fieldmanual-"
            f"{os.getpid()}-{secrets.token_hex(8)}"
        )
        try:
            descriptor = os.open(
                name,
                flags,
                mode,
                dir_fd=parent_descriptor,
            )
        except FileExistsError:
            continue
        return descriptor, name
    raise BootstrapError(
        f"could not allocate a temporary file for {destination_name}"
    )


def fsync_directory(descriptor: int) -> None:
    """Request directory-entry durability where the filesystem supports it."""

    try:
        os.fsync(descriptor)
    except OSError:
        # Some otherwise safe filesystems do not permit directory fsync.
        pass


def create_directory_anchored(
    operation: DirectoryOperation,
    project_descriptor: int,
) -> None:
    """Create a directory relative to the anchored project root."""

    parent_descriptor, name = open_anchored_parent(
        project_descriptor,
        operation.relative_path,
    )
    try:
        try:
            os.mkdir(name, operation.mode, dir_fd=parent_descriptor)
        except FileExistsError as error:
            raise BootstrapError(
                "directory destination changed after preflight: "
                f"{operation.destination}"
            ) from error
        fsync_directory(parent_descriptor)
    finally:
        os.close(parent_descriptor)


def atomic_write_anchored(
    operation: WriteOperation,
    project_descriptor: int,
) -> None:
    """Publish one file beneath an anchored root without symlink traversal."""

    parent_descriptor, name = open_anchored_parent(
        project_descriptor,
        operation.relative_path,
    )
    temporary_name: Optional[str] = None
    try:
        existing = read_anchored_file(
            parent_descriptor,
            name,
            operation.destination,
        )
        if (existing is not None) != operation.expected_exists:
            raise BootstrapError(
                "destination changed after preflight; refusing write: "
                f"{operation.destination}"
            )
        if existing is not None and existing != operation.expected_content:
            raise BootstrapError(
                f"destination content changed after preflight: "
                f"{operation.destination}"
            )

        descriptor, temporary_name = create_anchored_temporary(
            parent_descriptor,
            name,
            operation.mode,
        )
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(operation.content)
            handle.flush()
            os.fchmod(handle.fileno(), operation.mode)
            os.fsync(handle.fileno())

        if operation.expected_exists:
            current = read_anchored_file(
                parent_descriptor,
                name,
                operation.destination,
            )
            if current != operation.expected_content:
                raise BootstrapError(
                    "destination content changed during write; refusing update: "
                    f"{operation.destination}"
                )
            os.rename(
                temporary_name,
                name,
                src_dir_fd=parent_descriptor,
                dst_dir_fd=parent_descriptor,
            )
            temporary_name = None
        else:
            try:
                os.link(
                    temporary_name,
                    name,
                    src_dir_fd=parent_descriptor,
                    dst_dir_fd=parent_descriptor,
                    follow_symlinks=False,
                )
            except FileExistsError as error:
                raise BootstrapError(
                    "destination appeared during write; refusing overwrite: "
                    f"{operation.destination}"
                ) from error
            os.unlink(temporary_name, dir_fd=parent_descriptor)
            temporary_name = None
        fsync_directory(parent_descriptor)
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name, dir_fd=parent_descriptor)
            except FileNotFoundError:
                pass
        os.close(parent_descriptor)


def atomic_write_portable(operation: WriteOperation, project_root: Path) -> None:
    """Portable fallback for platforms without safe directory descriptors."""

    destination = operation.destination
    if target_path(project_root, operation.relative_path) != destination:
        raise BootstrapError(
            f"destination no longer resolves as preflighted: {destination}"
        )
    if destination.is_symlink():
        raise BootstrapError(f"destination became a symlink: {destination}")
    exists_now = destination.exists()
    if exists_now != operation.expected_exists:
        raise BootstrapError(
            f"destination changed after preflight; refusing write: {destination}"
        )
    if exists_now:
        if not destination.is_file():
            raise BootstrapError(
                f"destination changed type after preflight: {destination}"
            )
        current = destination.read_bytes()
        if current != operation.expected_content:
            raise BootstrapError(
                f"destination content changed after preflight: {destination}"
            )

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.fieldmanual-",
        dir=str(destination.parent),
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(operation.content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, operation.mode)
        if operation.expected_exists:
            current = read_existing_file(destination, "managed destination")
            if current != operation.expected_content:
                raise BootstrapError(
                    f"destination content changed during write: {destination}"
                )
            os.replace(str(temporary), str(destination))
        else:
            try:
                if os.name == "nt":
                    # Windows rename is a no-replace operation.
                    os.rename(str(temporary), str(destination))
                else:
                    os.link(str(temporary), str(destination))
            except OSError as error:
                if destination.exists() or destination.is_symlink():
                    raise BootstrapError(
                        "destination appeared during write; refusing overwrite: "
                        f"{destination}"
                    ) from error
                raise
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def atomic_write(
    operation: WriteOperation,
    project_root: Path,
    project_descriptor: Optional[int],
) -> None:
    """Apply one preflighted write using the strongest available primitives."""

    if project_descriptor is not None:
        atomic_write_anchored(operation, project_descriptor)
    else:
        atomic_write_portable(operation, project_root)


def apply_plan(plan: Plan, dry_run: bool) -> None:
    """Print and optionally apply a preflighted installation plan."""

    project_descriptor: Optional[int] = None
    if not dry_run and ANCHORED_MUTATIONS_AVAILABLE:
        project_descriptor = open_project_anchor(plan)

    directory_operations = sorted(
        plan.directories,
        key=lambda operation: len(operation.destination.parts),
    )
    try:
        for operation in directory_operations:
            action = "WOULD CREATE" if dry_run else "CREATE"
            print(
                f"[fieldmanual-bootstrap] {action} directory "
                f"{operation.relative_path}"
            )
            if dry_run:
                continue
            if (
                target_path(plan.project_root, operation.relative_path)
                != operation.destination
            ):
                raise BootstrapError(
                    "directory no longer resolves as preflighted: "
                    f"{operation.destination}"
                )
            if project_descriptor is not None:
                create_directory_anchored(operation, project_descriptor)
            else:
                if (
                    operation.destination.exists()
                    or operation.destination.is_symlink()
                ):
                    raise BootstrapError(
                        "directory destination changed after preflight: "
                        f"{operation.destination}"
                    )
                operation.destination.mkdir(mode=operation.mode)

        for operation in plan.writes:
            if dry_run:
                action = (
                    "WOULD UPDATE"
                    if operation.managed_update
                    else "WOULD CREATE"
                )
            else:
                action = "UPDATE" if operation.managed_update else "CREATE"
            print(f"[fieldmanual-bootstrap] {action} file {operation.relative_path}")
            if not dry_run:
                atomic_write(
                    operation,
                    plan.project_root,
                    project_descriptor,
                )

        for relative_path in plan.preserved_different:
            print(
                "[fieldmanual-bootstrap] PRESERVE project-owned file "
                f"{relative_path} (content differs from starter)"
            )

        verb = "planned" if dry_run else "completed"
        print(
            "[fieldmanual-bootstrap] PASS: "
            f"{verb}; {len(plan.directories)} directories, "
            f"{len(plan.writes)} writes, "
            f"{plan.preserved_identical} create-only files preserved, "
            f"{plan.preserved_managed} managed files unchanged, "
            f"{len(plan.preserved_different)} differing project-owned files "
            "preserved"
        )
    finally:
        if project_descriptor is not None:
            os.close(project_descriptor)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse the intentionally small bootstrap command-line interface."""

    parser = argparse.ArgumentParser(
        description=(
            "Create the conservative project skeleton declared by "
            "FieldManual-layout.toml."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help=(
            "Project root to initialize. Strongly recommended on the first "
            "consuming-project run."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preflight and print the complete plan without writing.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run preflight and apply the FieldManual filesystem contract."""

    args = parse_args(argv)
    try:
        framework_root = Path(__file__).resolve(strict=True).parent
        layout = load_layout(framework_root)
        project_root = discover_project_root(
            framework_root=framework_root,
            layout=layout,
            explicit=args.project_root,
        )
        validate_actual_placement(project_root, framework_root)
        plan = build_plan(
            layout=layout,
            project_root=project_root,
            framework_root=framework_root,
        )
        apply_plan(plan, dry_run=args.dry_run)
    except BootstrapError as error:
        print(f"[fieldmanual-bootstrap] FAIL: {error}", file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as error:
        print(
            f"[fieldmanual-bootstrap] FAIL: filesystem or encoding error: {error}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
