"""`canvas calendar` — upcoming due dates, with optional .ics export."""

from __future__ import annotations

import json as _json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import typer
from canvasapi.exceptions import CanvasException
from icalendar import Calendar, Event
from rich.console import Console
from rich.table import Table

from ..client import get_user_courses
from ..matchers import extract_short_code

console = Console()
err_console = Console(stderr=True)


def calendar(
    days: int = typer.Option(30, "--days", help="Look-ahead window in days"),
    ical: bool = typer.Option(False, "--ical", help="Output iCalendar (.ics) format"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Write .ics to file (use with --ical)"
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """Show upcoming due dates across all academic courses."""
    courses = get_user_courses(active_only=True)
    targets = [c for c in courses if extract_short_code(getattr(c, "name", "") or "")]

    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=days)

    events = []
    for c in targets:
        try:
            assigns = list(c.get_assignments())
        except CanvasException as exc:
            err_console.print(f"[yellow]Skip {c.name}:[/yellow] {exc}")
            continue
        short = extract_short_code(c.name) or c.name
        for a in assigns:
            due_str = getattr(a, "due_at", None)
            if not due_str:
                continue
            try:
                due = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
            except ValueError:
                continue
            if not (now <= due <= cutoff):
                continue
            events.append({
                "course": short,
                "course_id": c.id,
                "assignment_id": getattr(a, "id", None),
                "title": getattr(a, "name", "?"),
                "due_at": due_str,
                "due": due,
                "points": getattr(a, "points_possible", None),
                "url": getattr(a, "html_url", None),
            })

    events.sort(key=lambda e: e["due"])

    if ical:
        ics_bytes = _build_ics(events)
        if output:
            output.expanduser().write_bytes(ics_bytes)
            console.print(f"[green]Wrote[/green] {output} ({len(events)} events)")
        else:
            import sys as _sys
            _sys.stdout.buffer.write(ics_bytes)
        return

    if json_out:
        print(_json.dumps([
            {k: v for k, v in e.items() if k != "due"} for e in events
        ]))
        return

    if not events:
        console.print(f"[yellow]No due dates in next {days} days.[/yellow]")
        return

    table = Table(title=f"Upcoming due dates (next {days}d)", header_style="bold cyan")
    table.add_column("Course", style="green", no_wrap=True)
    table.add_column("When", style="yellow", no_wrap=True)
    table.add_column("Pts", justify="right", style="dim", no_wrap=True)
    table.add_column("Assignment")
    for e in events:
        when = e["due"].astimezone().strftime("%a %m-%d %H:%M")
        pts = f"{e['points']:.0f}" if isinstance(e["points"], (int, float)) else "—"
        table.add_row(e["course"], when, pts, e["title"])
    console.print(table)


def _build_ics(events: list[dict]) -> bytes:
    cal = Calendar()
    cal.add("prodid", "-//canvas-cli//uci.edu//EN")
    cal.add("version", "2.0")
    for e in events:
        ev = Event()
        ev.add("summary", f"[{e['course']}] {e['title']}")
        ev.add("dtstart", e["due"])
        ev.add("dtend", e["due"] + timedelta(minutes=15))
        ev.add("dtstamp", datetime.now(timezone.utc))
        ev.add("uid", f"canvas-{e['assignment_id']}@uci.edu")
        if e.get("url"):
            ev.add("url", e["url"])
        if isinstance(e.get("points"), (int, float)):
            ev.add("description", f"{e['points']:.0f} points · {e.get('url', '')}")
        cal.add_component(ev)
    return cal.to_ical()
