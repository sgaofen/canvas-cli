"""`canvas pages <course> [<page>]` — list or read course Pages (wiki-style content)."""

from __future__ import annotations

import json as _json

import html2text
import typer
from canvasapi.exceptions import CanvasException, Forbidden, ResourceDoesNotExist
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from ..client import get_user_courses
from ..formatters import format_relative_time
from ..matchers import resolve_course

console = Console()


def _to_markdown(html: str) -> str:
    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_images = False
    return h.handle(html).strip() if html else ""


def pages(
    course: str = typer.Argument(..., help="Course short code or id"),
    page: str | None = typer.Argument(None, help="Page url or id; omit to list all pages"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON"),
    raw: bool = typer.Option(False, "--raw", help="Print raw HTML (when reading one page)"),
) -> None:
    """List Pages, or read a specific Page's body."""
    courses = get_user_courses(active_only=True)
    target = resolve_course(courses, course)

    if page is None:
        _list_pages(target, json_out)
    else:
        _show_page(target, page, json_out, raw)


def _list_pages(target, json_out: bool) -> None:
    try:
        pgs = list(target.get_pages())
    except (Forbidden, ResourceDoesNotExist, CanvasException) as exc:
        if json_out:
            print(_json.dumps([]))
            return
        # Most common: Pages tab disabled by faculty → API returns 404
        msg = "Pages tab not accessible (likely disabled in course settings)"
        console.print(f"[yellow]{msg}[/yellow] [dim]({exc})[/dim]")
        raise typer.Exit(code=1)

    rows = [
        {
            "page_id": getattr(p, "page_id", None),
            "title": getattr(p, "title", "?"),
            "url": getattr(p, "url", None),
            "updated_at": getattr(p, "updated_at", None),
            "published": getattr(p, "published", None),
            "front_page": getattr(p, "front_page", False),
        }
        for p in pgs
    ]

    if json_out:
        print(_json.dumps(rows))
        return

    if not rows:
        console.print(f"[yellow]No pages in[/yellow] {target.name}")
        return

    table = Table(title=f"Pages — {target.name} ({len(rows)})", header_style="bold cyan")
    table.add_column("Title")
    table.add_column("URL slug", style="green")
    table.add_column("Updated", style="dim", no_wrap=True)
    table.add_column("Front", justify="center")
    for r in rows:
        front = "[yellow]★[/yellow]" if r["front_page"] else ""
        table.add_row(
            r["title"], r["url"] or "", format_relative_time(r["updated_at"]), front,
        )
    console.print(table)


def _show_page(target, page_ref: str, json_out: bool, raw: bool) -> None:
    try:
        p = target.get_page(page_ref)
    except ResourceDoesNotExist:
        console.print(f"[red]Page not found:[/red] {page_ref}")
        raise typer.Exit(code=1)
    except CanvasException as exc:
        console.print(f"[red]Failed:[/red] {exc}")
        raise typer.Exit(code=1)

    html = getattr(p, "body", "") or ""
    title = getattr(p, "title", "?")

    if json_out:
        print(_json.dumps({
            "page_id": getattr(p, "page_id", None),
            "title": title,
            "url": getattr(p, "url", None),
            "updated_at": getattr(p, "updated_at", None),
            "body_html": html,
            "body_markdown": _to_markdown(html),
        }))
        return

    if raw:
        print(html)
        return

    if not html.strip():
        console.print(f"[yellow]Empty page:[/yellow] {title}")
        return

    console.print(Panel(Markdown(_to_markdown(html)), title=title, border_style="cyan"))
