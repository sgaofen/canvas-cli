"""`canvas announcements [course]` — recent course announcements."""

from __future__ import annotations

import json as _json
from datetime import datetime, timedelta, timezone

import html2text
import typer
from canvasapi.exceptions import CanvasException
from rich.console import Console
from rich.table import Table

from ..client import get_canvas, get_user_courses
from ..formatters import format_relative_time
from ..matchers import extract_short_code, resolve_course

console = Console()


def _to_text(html: str) -> str:
    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_images = True
    return h.handle(html).strip() if html else ""


def announcements(
    course: str | None = typer.Argument(None, help="Course; omit for all academic courses"),
    days: int = typer.Option(7, "--days", help="Look-back window in days"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON"),
    full: bool = typer.Option(False, "--full", help="Include announcement body text"),
) -> None:
    """List recent announcements."""
    courses = get_user_courses(active_only=True)
    if course:
        targets = [resolve_course(courses, course)]
    else:
        targets = [c for c in courses if extract_short_code(getattr(c, "name", "") or "")]

    canvas = get_canvas()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    context_codes = [f"course_{c.id}" for c in targets]

    try:
        anns = list(canvas.get_announcements(
            context_codes=context_codes,
            start_date=cutoff.date().isoformat(),
        ))
    except CanvasException as exc:
        console.print(f"[red]Failed:[/red] {exc}")
        raise typer.Exit(code=1)

    course_by_id = {c.id: c for c in targets}
    rows = []
    for a in anns:
        cid = _course_id_from_context(getattr(a, "context_code", ""))
        c = course_by_id.get(cid)
        short = extract_short_code(getattr(c, "name", "") or "") if c else None
        body_html = getattr(a, "message", "") or ""
        rows.append({
            "id": getattr(a, "id", None),
            "course": short or (getattr(c, "name", "?") if c else "?"),
            "course_id": cid,
            "title": getattr(a, "title", "?"),
            "posted_at": getattr(a, "posted_at", None) or getattr(a, "created_at", None),
            "url": getattr(a, "html_url", None),
            "body_text": _to_text(body_html) if full or json_out else None,
        })

    rows.sort(key=lambda r: r["posted_at"] or "", reverse=True)

    if json_out:
        print(_json.dumps(rows))
        return

    if not rows:
        console.print(f"[yellow]No announcements in last {days} days.[/yellow]")
        return

    table = Table(title=f"Announcements (last {days}d)", header_style="bold cyan")
    table.add_column("Course", style="green", no_wrap=True)
    table.add_column("Posted", style="dim", no_wrap=True)
    table.add_column("Title")

    for r in rows:
        table.add_row(r["course"], format_relative_time(r["posted_at"]), r["title"])
    console.print(table)

    if full:
        for r in rows:
            console.print(f"\n[bold cyan]{r['course']}[/bold cyan] — {r['title']}")
            console.print(f"[dim]{format_relative_time(r['posted_at'])} · {r['url']}[/dim]")
            console.print(r["body_text"] or "[dim](empty)[/dim]")


def _course_id_from_context(ctx: str) -> int | None:
    # ctx like "course_81951"
    if ctx.startswith("course_"):
        try:
            return int(ctx[len("course_"):])
        except ValueError:
            return None
    return None
