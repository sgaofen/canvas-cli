"""Course code extraction and fuzzy matching.

UCI's `course_code` field from Canvas is essentially a truncated copy of
`name` (e.g. "CHEM M3LC - Ardo - Spring 2026"), not a clean SIS code like
"CHEM M3LC". We extract the real short code from `name` via regex.

Match inputs supported:
    chem3lc, chemm3lc, "chem m3lc", CHEMM3LC  →  CHEM M3LC
    physics7c, phys7c                          →  PHYSICS 7C  (substring)
    82901                                      →  course id exact
"""

from __future__ import annotations

import re

import typer
from rich.console import Console

console = Console()

# Dept (1-2 alpha words) + course number (optional letter prefix, digits, optional suffix).
# Examples matched: "CHEM M3LC", "PHYSICS 7LC", "UNI STU 87", "Bio Sci 94".
_CODE_RE = re.compile(
    r"^([A-Za-z]{2,}(?:\s+[A-Za-z]{2,})?)\s+([A-Z]?\d+[A-Z]*)\b",
    re.IGNORECASE,
)


def extract_short_code(name: str) -> str | None:
    """Extract a clean course short code from a Canvas course name."""
    if not name:
        return None
    m = _CODE_RE.match(name)
    if not m:
        return None
    dept = re.sub(r"\s+", " ", m.group(1).strip()).upper()
    num = m.group(2).upper()
    return f"{dept} {num}"


def normalize(s: str) -> str:
    """Lowercase and strip non-alphanumerics for fuzzy comparison."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def code_aliases(short_code: str) -> set[str]:
    """All reasonable normalized spellings of a short code.

    "CHEM M3LC" → {"chemm3lc", "chem3lc"}
    "PHYSICS 7C" → {"physics7c"}
    """
    parts = short_code.split()
    aliases: set[str] = {normalize(short_code)}
    if len(parts) >= 2:
        dept = "".join(parts[:-1])
        num = parts[-1]
        aliases.add(normalize(f"{dept}{num}"))
        # Drop letter prefix from number ("M3LC" → "3LC") for inputs like "chem3lc"
        num_no_prefix = re.sub(r"^[A-Z]+", "", num)
        if num_no_prefix and num_no_prefix != num:
            aliases.add(normalize(f"{dept}{num_no_prefix}"))
    return aliases


def _course_matches(course, needle: str) -> bool:
    name = getattr(course, "name", "") or ""
    short = extract_short_code(name)
    if short:
        for alias in code_aliases(short):
            if needle in alias:
                return True
    # Fallback: substring match on full name
    return needle in normalize(name)


def find_courses(courses: list, query: str) -> list:
    """Return all courses matching `query`. Empty list if none."""
    # Course id exact match (Canvas IDs are large ints, safe to assume digits = id)
    if query.isdigit():
        cid = int(query)
        for c in courses:
            if getattr(c, "id", None) == cid:
                return [c]

    needle = normalize(query)
    if not needle:
        return []
    return [c for c in courses if _course_matches(c, needle)]


def resolve_course(courses: list, query: str):
    """Find a single course or interactively disambiguate.

    Exits with code 1 if no match. Prompts user to pick if multiple matches.
    """
    matches = find_courses(courses, query)

    if not matches:
        console.print(f"[red]No course matches[/red] '[bold]{query}[/bold]'.")
        console.print("[dim]Available short codes:[/dim]")
        for c in courses:
            code = extract_short_code(getattr(c, "name", "") or "") or "—"
            console.print(f"  [green]{code:<14}[/green] {getattr(c, 'name', '')}")
        raise typer.Exit(code=1)

    if len(matches) == 1:
        return matches[0]

    console.print(f"[yellow]Multiple courses match[/yellow] '[bold]{query}[/bold]':")
    for i, c in enumerate(matches, 1):
        code = extract_short_code(getattr(c, "name", "") or "") or "—"
        console.print(f"  [cyan]{i}[/cyan]. [green]{code:<14}[/green] {getattr(c, 'name', '')}")

    choice = typer.prompt("Pick number", type=int)
    if not 1 <= choice <= len(matches):
        console.print("[red]Invalid choice.[/red]")
        raise typer.Exit(code=1)
    return matches[choice - 1]


def resolve_assignment(course, query: str):
    """Find an assignment within a course by numeric id or name substring.

    Same disambiguation flow as resolve_course: exact id wins; otherwise
    substring match; multiple matches prompt the user to pick.
    """
    from canvasapi.exceptions import CanvasException, ResourceDoesNotExist

    if query.isdigit():
        try:
            return course.get_assignment(int(query))
        except (ResourceDoesNotExist, CanvasException):
            pass  # fall through

    needle = query.lower().strip()
    try:
        assigns = list(course.get_assignments())
    except CanvasException as exc:
        console.print(f"[red]Failed to fetch assignments:[/red] {exc}")
        raise typer.Exit(code=1)

    matches = [a for a in assigns if needle in (getattr(a, "name", "") or "").lower()]

    if not matches:
        console.print(f"[red]No assignment matches[/red] '[bold]{query}[/bold]'.")
        console.print("[dim]Available assignments:[/dim]")
        for a in assigns[:20]:
            console.print(f"  {getattr(a, 'id', '?')}  {getattr(a, 'name', '?')}")
        if len(assigns) > 20:
            console.print(f"  [dim]... +{len(assigns) - 20} more[/dim]")
        raise typer.Exit(code=1)

    if len(matches) == 1:
        return matches[0]

    console.print(f"[yellow]Multiple assignments match[/yellow] '[bold]{query}[/bold]':")
    for i, a in enumerate(matches, 1):
        due = getattr(a, "due_at", None) or "—"
        console.print(f"  [cyan]{i}[/cyan]. {getattr(a, 'name', '?')} (id={a.id}, due={due})")
    choice = typer.prompt("Pick number", type=int)
    if not 1 <= choice <= len(matches):
        console.print("[red]Invalid choice.[/red]")
        raise typer.Exit(code=1)
    return matches[choice - 1]
