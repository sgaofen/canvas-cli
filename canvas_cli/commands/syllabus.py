"""`canvas syllabus <course>` — fetch a course's syllabus body.

Canvas stores syllabi as HTML on the course resource (`syllabus_body`).
We render to Markdown for terminal/agent consumption; `--raw` keeps HTML.
"""

from __future__ import annotations

import json as _json

import html2text
import typer
from canvasapi.exceptions import CanvasException
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from ..client import get_canvas, get_user_courses
from ..matchers import extract_short_code, resolve_course

console = Console()


def _to_markdown(html: str) -> str:
    h = html2text.HTML2Text()
    h.body_width = 0  # don't wrap
    h.ignore_images = False
    h.ignore_links = False
    return h.handle(html).strip() if html else ""


def syllabus(
    course: str = typer.Argument(..., help="Course short code or id"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON (html + markdown)"),
    raw: bool = typer.Option(False, "--raw", help="Print raw HTML"),
) -> None:
    """Fetch a course's syllabus body."""
    courses = get_user_courses(active_only=True)
    target = resolve_course(courses, course)

    canvas = get_canvas()
    try:
        full = canvas.get_course(target.id, include=["syllabus_body"])
    except CanvasException as exc:
        console.print(f"[red]Failed to fetch course:[/red] {exc}")
        raise typer.Exit(code=1)

    html = getattr(full, "syllabus_body", "") or ""
    short = extract_short_code(target.name) or target.name

    if json_out:
        print(_json.dumps({
            "course_id": target.id,
            "name": target.name,
            "short_code": extract_short_code(target.name) if target.name else None,
            "syllabus_html": html,
            "syllabus_markdown": _to_markdown(html),
            "has_content": bool(html.strip()),
        }))
        return

    if raw:
        print(html)
        return

    if not html.strip():
        console.print(f"[yellow]No syllabus content for[/yellow] {target.name}")
        return

    md = _to_markdown(html)
    console.print(Panel(Markdown(md), title=short, border_style="cyan"))
