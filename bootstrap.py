#!/usr/bin/env python3
"""Install lightweight Field Manual templates into this repository."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Iterable, Sequence

FIELDMANUAL_ROOT_PLACEHOLDERS = ("{{FIELDMANUAL_ROOT}}", "{$FIELDMANUAL_ROOT}")
PROJECT_SLUG_PLACEHOLDERS = ("{{PROJECT_SLUG}}", "{$PROJECT_SLUG}")
AGENTS_PATH = Path("AGENTS.md")
AGENTS_HEADER = "AGENTS-header.md"
AGENTS_FOOTER = "AGENTS-footer.md"
AGENTS_TEMPLATE_NAME = "AGENTS.md"
MANAGED_MARKERS = (
    "<!-- FIELDMANUAL_MANAGED_HEADER_START -->",
    "<!-- FIELDMANUAL_MANAGED_HEADER_END -->",
    "<!-- FIELDMANUAL_MANAGED_FOOTER_START -->",
    "<!-- FIELDMANUAL_MANAGED_FOOTER_END -->",
)


def fieldmanual_root() -> Path:
    return Path(__file__).resolve().parent


def default_project_root(manual_root: Path) -> Path:
    return manual_root.parent.resolve()


def project_slug(project_root: Path) -> str:
    name = project_root.name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", name)
    return slug.strip("-") or "project"


def infer_fieldmanual_root(project_root: Path, manual_root: Path) -> str:
    try:
        relative = manual_root.relative_to(project_root)
    except ValueError as error:
        raise RuntimeError(
            "--fieldmanual-root is required when the FieldManual directory is "
            "not inside --project-root."
        ) from error
    return relative.as_posix() or "."


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install starter files from FieldManual/templates."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help=(
            "Target project root. Defaults to the parent directory of this "
            "FieldManual checkout."
        ),
    )
    parser.add_argument(
        "--fieldmanual-root",
        default=None,
        help=(
            "Path from the target project root back to the FieldManual "
            "directory. Defaults to the relative path when it can be inferred."
        ),
    )
    parser.add_argument(
        "--template",
        action="append",
        dest="templates",
        default=None,
        help=(
            "Top-level entry under FieldManual/templates/ to install. Repeat "
            "to install multiple entries. Defaults to all installable entries."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files in the target project.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the planned writes without changing the target project.",
    )
    return parser.parse_args(argv)


def installable_entries(templates_root: Path) -> dict[str, tuple[Path, Path]]:
    return {
        path.name: (path, path.relative_to(templates_root))
        for path in sorted(templates_root.iterdir())
        if path.name not in {"README.md", AGENTS_HEADER, AGENTS_FOOTER}
    }


def selected_templates(
    templates_root: Path, requested: Iterable[str] | None
) -> tuple[list[tuple[Path, Path]], bool]:
    available = installable_entries(templates_root)
    if requested is None:
        return list(available.values()), True

    selected: list[tuple[Path, Path]] = []
    include_agents = False
    for name in requested:
        if name == AGENTS_TEMPLATE_NAME:
            include_agents = True
            continue
        path = available.get(name)
        if path is None:
            known_names = sorted(available)
            known_names.append(AGENTS_TEMPLATE_NAME)
            known = ", ".join(sorted(known_names))
            raise RuntimeError(f"Unknown template '{name}'. Available: {known}")
        selected.append(path)
    return selected, include_agents


def iter_install_files(sources: Iterable[tuple[Path, Path]]) -> list[tuple[Path, Path]]:
    planned: list[tuple[Path, Path]] = []
    for source, destination_root in sources:
        if source.is_file():
            planned.append((source, destination_root))
            continue
        for file_path in sorted(source.rglob("*")):
            if file_path.is_file():
                planned.append(
                    (file_path, destination_root / file_path.relative_to(source))
                )
    return planned


def render_file(source: Path, fieldmanual_root_value: str, slug: str) -> bytes:
    content = source.read_bytes()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return content
    for placeholder in FIELDMANUAL_ROOT_PLACEHOLDERS:
        text = text.replace(placeholder, fieldmanual_root_value)
    for placeholder in PROJECT_SLUG_PLACEHOLDERS:
        text = text.replace(placeholder, slug)
    return text.encode("utf-8")


def strip_managed_agents_sections(content: str) -> str:
    updated = content
    header_start, header_end, footer_start, footer_end = MANAGED_MARKERS

    while header_start in updated and header_end in updated:
        start = updated.index(header_start)
        end = updated.index(header_end) + len(header_end)
        updated = updated[:start] + updated[end:]

    while footer_start in updated and footer_end in updated:
        start = updated.index(footer_start)
        end = updated.index(footer_end) + len(footer_end)
        updated = updated[:start] + updated[end:]

    return updated.strip()


def install_agents_file(
    templates_root: Path,
    project_root: Path,
    fieldmanual_root_value: str,
    slug: str,
    dry_run: bool,
) -> Path:
    header = render_file(
        templates_root / AGENTS_HEADER, fieldmanual_root_value, slug
    ).decode("utf-8")
    footer = render_file(
        templates_root / AGENTS_FOOTER, fieldmanual_root_value, slug
    ).decode("utf-8")
    destination = project_root / AGENTS_PATH

    existing = ""
    if destination.exists():
        existing = destination.read_text(encoding="utf-8")

    body = strip_managed_agents_sections(existing)
    sections = [header.strip()]
    if body:
        sections.append(body)
    sections.append(footer.strip())
    content = "\n\n".join(sections) + "\n"

    if dry_run:
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    return destination


def install_templates(
    templates_root: Path,
    project_root: Path,
    fieldmanual_root_value: str,
    slug: str,
    requested: Iterable[str] | None,
    force: bool,
    dry_run: bool,
) -> list[Path]:
    sources, include_agents = selected_templates(templates_root, requested)
    files = iter_install_files(sources)
    destinations: list[Path] = []
    if include_agents:
        destinations.append(project_root / AGENTS_PATH)
    destinations.extend(project_root / relative_path for _, relative_path in files)

    conflicts = [path for path in destinations if path.exists()]
    if conflicts and not force:
        joined = ", ".join(
            path.relative_to(project_root).as_posix() for path in conflicts
        )
        raise RuntimeError(
            "Refusing to overwrite existing files without --force: " + joined
        )

    if dry_run:
        return destinations

    written: list[Path] = []
    if include_agents:
        written.append(
            install_agents_file(
                templates_root=templates_root,
                project_root=project_root,
                fieldmanual_root_value=fieldmanual_root_value,
                slug=slug,
                dry_run=False,
            )
        )
    for source, relative_path in files:
        destination = project_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(
            render_file(source, fieldmanual_root_value, slug)
        )
        os.chmod(destination, source.stat().st_mode & 0o777)
        written.append(destination)
    return written


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    manual_root = fieldmanual_root()
    templates_root = manual_root / "templates"
    project_root = (
        args.project_root.resolve()
        if args.project_root is not None
        else default_project_root(manual_root)
    )

    try:
        fieldmanual_root_value = args.fieldmanual_root or infer_fieldmanual_root(
            project_root=project_root,
            manual_root=manual_root,
        )
        slug = project_slug(project_root)
        destinations = install_templates(
            templates_root=templates_root,
            project_root=project_root,
            fieldmanual_root_value=fieldmanual_root_value,
            slug=slug,
            requested=args.templates,
            force=args.force,
            dry_run=args.dry_run,
        )
    except RuntimeError as error:
        print(f"[fieldmanual-bootstrap] FAIL: {error}", file=sys.stderr)
        return 1

    action = "would install" if args.dry_run else "installed"
    print(
        f"[fieldmanual-bootstrap] PASS: {action} {len(destinations)} files into "
        f"{project_root}"
    )
    for destination in destinations:
        print(
            "[fieldmanual-bootstrap] -> "
            f"{destination.relative_to(project_root).as_posix()}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
