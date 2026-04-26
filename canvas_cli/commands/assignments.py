"""`canvas assignments [course]` — list assignments with due dates and submission state."""

from __future__ import annotations

import json as _json
from datetime import datetime, timedelta, timezone

import typer
from canvasapi.exceptions import CanvasException
from rich.console import Console
from rich.table import Table

from ..client import get_user_courses
from ..matchers import extract_short_code, resolve_course

console = Console()
err_console = Console(stderr=True)


def assignments(
    course: str | None = typer.Argument(
        None, help="Course short code/id; omit for upcoming across all academic courses"
    ),
    upcoming: int = typer.Option(
        14, "--upcoming", help="Days ahead window for default cross-course view"
    ),
    all_assignments: bool = typer.Option(
        False, "--all", help="Include past + future, no time filter"
    ),
    overdue: bool = typer.Option(
        False, "--overdue", help="Only past-due unsubmitted"
    ),
    submitted_only: bool = typer.Option(
        False, "--submitted", help="Only submitted/graded"
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """List assignments across one or all courses."""
    courses = get_user_courses(active_only=True)
    if course:
        targets = [resolve_course(courses, course)]
    else:
        targets = [c for c in courses if extract_short_code(getattr(c, "name", "") or "")]

    now = datetime.now(timezone.utc)
    upcoming_cutoff = now + timedelta(days=upcoming)

    rows: list[dict] = []
    for c in targets:
        try:
            assigns = list(c.get_assignments(include=["submission"]))
        except CanvasException as exc:
            err_console.print(f"[yellow]Skip {getattr(c, 'name', '?')}:[/yellow] {exc}")
            continue

        for a in assigns:
            due = _parse_iso(getattr(a, "due_at", None))
            sub = getattr(a, "submission", None) or {}
            sub_state = sub.get("workflow_state") if isinstance(sub, dict) else None
            is_submitted = sub_state in ("submitted", "graded", "complete")

            if not _passes_filter(
                due, is_submitted, sub_state,
                course=course, all_=all_assignments, overdue=overdue,
                submitted_only=submitted_only, now=now, cutoff=upcoming_cutoff,
            ):
                continue

            short = extract_short_code(getattr(c, "name", "") or "") or getattr(c, "name", "?")
            rows.append({
                "course": short,
                "course_id": getattr(c, "id", None),
                "name": getattr(a, "name", "?"),
                "assignment_id": getattr(a, "id", None),
                "due_at": getattr(a, "due_at", None),
                "due_relative": _due_relative(due, now),
                "points": getattr(a, "points_possible", None),
                "submitted": is_submitted,
                "submission_state": sub_state,
                "html_url": getattr(a, "html_url", None),
            })

    rows.sort(key=lambda r: r["due_at"] or "9999")

    if json_out:
        print(_json.dumps(rows))
        return

    if not rows:
        console.print("[yellow]No assignments matching filters.[/yellow]")
        return

    table = Table(title=f"Assignments ({len(rows)})", header_style="bold cyan")
    table.add_column("Course", style="green", no_wrap=True)
    table.add_column("Assignment")
    table.add_column("Due", style="yellow", no_wrap=True)
    table.add_column("Pts", justify="right", style="dim", no_wrap=True)
    table.add_column("Status", justify="center", no_wrap=True)

    for r in rows:
        pts = f"{r['points']:.0f}" if isinstance(r["points"], (int, float)) else "—"
        table.add_row(
            r["course"], r["name"], r["due_relative"], pts, _status_label(r, now),
        )
    console.print(table)


def _passes_filter(
    due, is_submitted, sub_state, *, course, all_, overdue, submitted_only, now, cutoff
) -> bool:
    if overdue:
        return bool(due and due < now and not is_submitted)
    if submitted_only:
        return is_submitted
    if all_:
        return True
    if course is None:
        # default cross-course view: upcoming within window
        return bool(due and now <= due <= cutoff)
    # single course default: hide assignments that are >14d past AND submitted
    if due and due < now - timedelta(days=14) and is_submitted:
        return False
    return True


def _parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _due_relative(due: datetime | None, now: datetime) -> str:
    if not due:
        return "no due date"
    delta = due - now
    secs = int(delta.total_seconds())
    if abs(secs) < 3600:
        m = abs(secs) // 60
        return f"in {m}m" if secs > 0 else f"{m}m ago"
    if abs(secs) < 86400:
        h = abs(secs) // 3600
        return f"in {h}h" if secs > 0 else f"{h}h ago"
    days = abs(secs) // 86400
    date = due.strftime("%m-%d")
    return f"in {days}d ({date})" if secs > 0 else f"{days}d ago ({date})"


def _status_label(r: dict, now: datetime) -> str:
    if r["submission_state"] == "graded":
        return "[green]graded[/green]"
    if r["submitted"]:
        return "[green]submitted[/green]"
    due = _parse_iso(r["due_at"])
    if due and due < now:
        return "[red]overdue[/red]"
    return "[dim]pending[/dim]"
