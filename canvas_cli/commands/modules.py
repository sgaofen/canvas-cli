"""`canvas modules <course>` — list a course's Modules and items.

Modules are how UCI faculty often expose course structure (Pages, Quizzes,
external links) when the Files tab is locked. Each ModuleItem points to
something readable — File, Page, Discussion, Assignment, Quiz, or external URL.
"""

from __future__ import annotations

import json as _json

import typer
from canvasapi.exceptions import CanvasException, Forbidden
from rich.console import Console
from rich.tree import Tree

from ..client import get_user_courses
from ..matchers import resolve_course

console = Console()


_TYPE_GLYPH = {
    "File": "[blue]\U0001f4ce[/blue]",  # paperclip
    "Page": "[green]P[/green]",
    "Discussion": "[magenta]D[/magenta]",
    "Assignment": "[yellow]A[/yellow]",
    "Quiz": "[red]Q[/red]",
    "ExternalUrl": "[cyan]→[/cyan]",
    "ExternalTool": "[cyan]T[/cyan]",
    "SubHeader": "[dim]—[/dim]",
}


def modules(
    course: str = typer.Argument(..., help="Course short code or id"),
    next_only: bool = typer.Option(False, "--next", help="Show only the next un-completed item"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """List modules and items for a course."""
    courses = get_user_courses(active_only=True)
    target = resolve_course(courses, course)

    try:
        mods = list(target.get_modules())
    except Forbidden:
        console.print("[red]Forbidden:[/red] Modules tab not accessible.")
        raise typer.Exit(code=1)
    except CanvasException as exc:
        console.print(f"[red]Failed:[/red] {exc}")
        raise typer.Exit(code=1)

    structured = []
    for m in mods:
        try:
            items = list(m.get_module_items())
        except CanvasException:
            items = []
        structured.append({
            "module_id": getattr(m, "id", None),
            "name": getattr(m, "name", "?"),
            "position": getattr(m, "position", None),
            "state": getattr(m, "state", None),
            "items": [_item_dict(i) for i in items],
        })

    if next_only:
        upcoming = _find_next(structured)
        if json_out:
            print(_json.dumps(upcoming))
        elif upcoming:
            console.print(
                f"[bold]Next:[/bold] {upcoming['type']} — {upcoming['title']}\n"
                f"  module: {upcoming['module']}\n"
                f"  url: {upcoming.get('html_url', '—')}"
            )
        else:
            console.print("[green]All module items completed (or none with completion requirements).[/green]")
        return

    if json_out:
        print(_json.dumps(structured))
        return

    tree = Tree(f"[bold cyan]{target.name}[/bold cyan]")
    if not structured:
        tree.add("[dim](no modules)[/dim]")
    for m in structured:
        node = tree.add(f"[bold]{m['name']}[/bold] [dim]({m['state'] or '?'})[/dim]")
        for item in m["items"]:
            glyph = _TYPE_GLYPH.get(item["type"], item["type"])
            done = "[green]✓[/green] " if item.get("completed") else "  "
            line = f"{done}{glyph} {item['title']}"
            if item.get("html_url"):
                line += f" [dim]{item['html_url']}[/dim]"
            node.add(line)
    console.print(tree)


def _item_dict(item) -> dict:
    return {
        "item_id": getattr(item, "id", None),
        "title": getattr(item, "title", "?"),
        "type": getattr(item, "type", "?"),
        "content_id": getattr(item, "content_id", None),
        "page_url": getattr(item, "page_url", None),
        "html_url": getattr(item, "html_url", None),
        "external_url": getattr(item, "external_url", None),
        "completed": _is_completed(item),
    }


def _is_completed(item) -> bool | None:
    cr = getattr(item, "completion_requirement", None)
    if isinstance(cr, dict):
        return bool(cr.get("completed"))
    return None


def _find_next(structured: list[dict]) -> dict | None:
    for m in structured:
        for item in m["items"]:
            if item.get("type") == "SubHeader":
                continue
            if item.get("completed") is False:
                return {**item, "module": m["name"]}
    return None
