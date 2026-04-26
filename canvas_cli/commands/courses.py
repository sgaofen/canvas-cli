"""`canvas courses` — list enrolled courses."""

from __future__ import annotations

import json as _json

import typer
from rich.console import Console

from ..client import get_user_courses
from ..formatters import courses_table
from ..matchers import extract_short_code

console = Console()


def list_courses(
    all_terms: bool = typer.Option(
        False, "--all", help="Include past/concluded courses (default: active only)"
    ),
    term: str | None = typer.Option(
        None, "--term", help="Filter by term name (substring, case-insensitive)"
    ),
    json_out: bool = typer.Option(False, "--json", help="Output raw JSON"),
) -> None:
    """List enrolled courses."""
    courses = get_user_courses(active_only=not all_terms, include=["term", "teachers"])

    if term:
        needle = term.lower()
        courses = [c for c in courses if needle in (_term_name(c) or "").lower()]

    if json_out:
        console.print_json(_json.dumps([_course_dict(c) for c in courses]))
        return

    if not courses:
        console.print("[yellow]No courses found.[/yellow]")
        return

    table = courses_table()
    for c in courses:
        name = getattr(c, "name", "") or ""
        table.add_row(
            extract_short_code(name) or "—",
            name,
            _term_name(c) or "",
            str(getattr(c, "id", "")),
            _teachers_str(c),
        )
    console.print(table)


def _term_name(course) -> str | None:
    term = getattr(course, "term", None)
    if term is None:
        return None
    if isinstance(term, dict):
        return term.get("name")
    return getattr(term, "name", None)


def _teachers_list(course) -> list[str]:
    teachers = getattr(course, "teachers", None) or []
    out: list[str] = []
    for t in teachers:
        if isinstance(t, dict):
            name = t.get("display_name") or t.get("name")
        else:
            name = getattr(t, "display_name", None) or getattr(t, "name", None)
        if name:
            out.append(name)
    return out


def _teachers_str(course) -> str:
    return ", ".join(_teachers_list(course))


def _course_dict(course) -> dict:
    name = getattr(course, "name", None)
    return {
        "id": getattr(course, "id", None),
        "code": extract_short_code(name) if name else None,
        "name": name,
        "term": _term_name(course),
        "teachers": _teachers_list(course),
    }
