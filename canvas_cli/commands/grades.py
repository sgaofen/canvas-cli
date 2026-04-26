"""`canvas grades [course]` — show course totals or per-assignment grades.

Also supports `--what-if`: compute hypothetical final by plugging assumed
scores into ungraded assignments (uses Canvas assignment_groups weighting).
"""

from __future__ import annotations

import json as _json

import typer
from canvasapi.exceptions import CanvasException
from rich.console import Console
from rich.table import Table

from ..client import get_user_courses
from ..matchers import extract_short_code, resolve_course

console = Console()


def grades(
    course: str | None = typer.Argument(None, help="Course; omit for all-course totals"),
    what_if: bool = typer.Option(
        False, "--what-if", help="Hypothetical-grade calculator (requires <course>)"
    ),
    score_inputs: list[str] = typer.Option(
        [], "--score",
        help='Hypothetical score in form "Assignment Name=85" or "<id>=85" (repeatable)',
    ),
    assume_pct: float | None = typer.Option(
        None, "--assume-all",
        help="Hypothetical: assume this percentage on all ungraded assignments",
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """Show grades."""
    if what_if:
        if not course:
            console.print("[red]--what-if requires a course argument[/red]")
            raise typer.Exit(code=2)
        _what_if(course, score_inputs, assume_pct, json_out)
    elif course:
        _course_detail(course, json_out)
    else:
        _all_courses_overview(json_out)


def _all_courses_overview(json_out: bool) -> None:
    courses = get_user_courses(active_only=True, include=["total_scores"])
    rows = []
    for c in courses:
        if not extract_short_code(getattr(c, "name", "") or ""):
            continue
        # canvasapi attaches enrollment summary on the Course object when
        # include=total_scores. The shape varies; check both attribute paths.
        enrollments = getattr(c, "enrollments", None) or []
        if enrollments and isinstance(enrollments, list):
            e = enrollments[0]
            current = e.get("computed_current_score") if isinstance(e, dict) else None
            current_grade = e.get("computed_current_grade") if isinstance(e, dict) else None
            final = e.get("computed_final_score") if isinstance(e, dict) else None
        else:
            current = current_grade = final = None
        rows.append({
            "course": extract_short_code(c.name) or c.name,
            "course_id": c.id,
            "name": c.name,
            "current_score": current,
            "current_grade": current_grade,
            "final_score": final,
        })

    if json_out:
        print(_json.dumps(rows))
        return

    if not rows:
        console.print("[yellow]No graded courses found.[/yellow]")
        return

    table = Table(title="Course grades", header_style="bold cyan")
    table.add_column("Code", style="green")
    table.add_column("Current %", justify="right", style="yellow")
    table.add_column("Letter", justify="center")
    table.add_column("Final %", justify="right", style="dim")
    table.add_column("Name", style="dim")

    for r in rows:
        cur = f"{r['current_score']:.1f}" if isinstance(r["current_score"], (int, float)) else "—"
        fin = f"{r['final_score']:.1f}" if isinstance(r["final_score"], (int, float)) else "—"
        table.add_row(r["course"], cur, r["current_grade"] or "—", fin, r["name"])
    console.print(table)


def _course_detail(course: str, json_out: bool) -> None:
    courses = get_user_courses(active_only=True)
    target = resolve_course(courses, course)
    try:
        assigns = list(target.get_assignments(include=["submission"]))
    except CanvasException as exc:
        console.print(f"[red]Failed:[/red] {exc}")
        raise typer.Exit(code=1)

    rows = []
    for a in assigns:
        sub = getattr(a, "submission", None) or {}
        if not isinstance(sub, dict):
            sub = {}
        rows.append({
            "assignment": getattr(a, "name", "?"),
            "assignment_id": getattr(a, "id", None),
            "points_possible": getattr(a, "points_possible", None),
            "score": sub.get("score"),
            "grade": sub.get("grade"),
            "submission_state": sub.get("workflow_state"),
            "graded_at": sub.get("graded_at"),
            "due_at": getattr(a, "due_at", None),
        })

    if json_out:
        print(_json.dumps(rows))
        return

    if not rows:
        console.print(f"[yellow]No assignments in[/yellow] {target.name}")
        return

    table = Table(title=f"Grades — {target.name}", header_style="bold cyan")
    table.add_column("Assignment")
    table.add_column("Score", justify="right", style="yellow")
    table.add_column("Possible", justify="right", style="dim")
    table.add_column("Grade", justify="center")
    table.add_column("State", justify="center", style="dim")

    for r in rows:
        score = f"{r['score']:.1f}" if isinstance(r["score"], (int, float)) else "—"
        poss = f"{r['points_possible']:.0f}" if isinstance(r["points_possible"], (int, float)) else "—"
        table.add_row(
            r["assignment"], score, poss, r["grade"] or "—", r["submission_state"] or "—",
        )
    console.print(table)


def _what_if(
    course: str, score_inputs: list[str], assume_pct: float | None, json_out: bool,
) -> None:
    """Hypothetical-final calculator using Canvas assignment_group weights."""
    courses = get_user_courses(active_only=True)
    target = resolve_course(courses, course)

    try:
        groups = list(target.get_assignment_groups(include=["assignments", "submission"]))
    except CanvasException as exc:
        console.print(f"[red]Failed to fetch assignment groups:[/red] {exc}")
        raise typer.Exit(code=1)

    # Parse explicit score inputs
    by_name: dict[str, float] = {}
    by_id: dict[int, float] = {}
    for raw in score_inputs:
        if "=" not in raw:
            console.print(f"[yellow]Skipping malformed --score:[/yellow] {raw}")
            continue
        key, val = raw.split("=", 1)
        try:
            score = float(val.strip())
        except ValueError:
            console.print(f"[yellow]Bad score in --score {raw!r}[/yellow]")
            continue
        key = key.strip()
        if key.isdigit():
            by_id[int(key)] = score
        else:
            by_name[key.lower()] = score

    breakdown = []
    total_weighted = 0.0
    total_weight_used = 0.0

    for g in groups:
        gname = getattr(g, "name", "?") or "?"
        gweight = getattr(g, "group_weight", 0) or 0
        assigns = getattr(g, "assignments", None) or []
        # canvasapi can return assignments as raw dicts when fetched via include
        graded_pts = 0.0
        graded_max = 0.0
        hypo_pts = 0.0
        hypo_max = 0.0
        items = []
        for a in assigns:
            if isinstance(a, dict):
                aid = a.get("id")
                aname = a.get("name", "?")
                pmax = a.get("points_possible") or 0
                sub = a.get("submission") or {}
            else:
                aid = getattr(a, "id", None)
                aname = getattr(a, "name", "?")
                pmax = getattr(a, "points_possible", 0) or 0
                sub = getattr(a, "submission", None) or {}
                if not isinstance(sub, dict):
                    sub = {}
            actual = sub.get("score")
            if actual is not None:
                graded_pts += actual
                graded_max += pmax
                items.append({"name": aname, "actual": actual, "max": pmax, "kind": "actual"})
            else:
                hypo = by_id.get(aid) if aid is not None else None
                if hypo is None:
                    hypo = by_name.get((aname or "").lower())
                if hypo is None and assume_pct is not None:
                    hypo = pmax * (assume_pct / 100.0)
                if hypo is not None:
                    hypo_pts += hypo
                    hypo_max += pmax
                    items.append({"name": aname, "hypothetical": hypo, "max": pmax, "kind": "hypothetical"})
                else:
                    items.append({"name": aname, "max": pmax, "kind": "ungraded"})

        used_pts = graded_pts + hypo_pts
        used_max = graded_max + hypo_max
        if used_max > 0 and gweight > 0:
            pct = used_pts / used_max
            total_weighted += pct * gweight
            total_weight_used += gweight
        breakdown.append({
            "group": gname,
            "weight": gweight,
            "graded": {"score": graded_pts, "max": graded_max},
            "hypothetical": {"score": hypo_pts, "max": hypo_max},
            "items": items,
        })

    projected = (total_weighted / total_weight_used * 100) if total_weight_used > 0 else None

    result = {
        "course": extract_short_code(target.name) or target.name,
        "course_id": target.id,
        "weights_used": total_weight_used,
        "projected_percentage": projected,
        "breakdown": breakdown,
    }

    if json_out:
        print(_json.dumps(result, default=str))
        return

    console.print(f"\n[bold cyan]What-if for[/bold cyan] {target.name}\n")
    if total_weight_used <= 0:
        console.print("[yellow]No weighted assignment groups (course may use total points or unweighted).[/yellow]")
    else:
        console.print(f"  weights covered: {total_weight_used:.0f}%")
        if projected is not None:
            console.print(f"  [bold green]projected: {projected:.2f}%[/bold green]\n")

    table = Table(header_style="bold cyan")
    table.add_column("Group", style="green")
    table.add_column("Weight%", justify="right", style="dim")
    table.add_column("Graded", justify="right")
    table.add_column("Hypothetical", justify="right", style="yellow")
    table.add_column("Ungraded (no input)", justify="right", style="dim")

    for b in breakdown:
        graded_n = sum(1 for i in b["items"] if i["kind"] == "actual")
        hypo_n = sum(1 for i in b["items"] if i["kind"] == "hypothetical")
        ungrd_n = sum(1 for i in b["items"] if i["kind"] == "ungraded")
        graded_str = (
            f"{b['graded']['score']:.0f}/{b['graded']['max']:.0f} ({graded_n})"
            if graded_n else "—"
        )
        hypo_str = (
            f"{b['hypothetical']['score']:.0f}/{b['hypothetical']['max']:.0f} ({hypo_n})"
            if hypo_n else "—"
        )
        table.add_row(
            b["group"], f"{b['weight']:.0f}",
            graded_str, hypo_str, str(ungrd_n) if ungrd_n else "—",
        )
    console.print(table)

    # List ungraded with no input so user knows what they could plug
    ungraded = [i for b in breakdown for i in b["items"] if i["kind"] == "ungraded"]
    if ungraded:
        console.print(f"\n[dim]{len(ungraded)} ungraded with no hypothetical:[/dim]")
        for i in ungraded[:10]:
            console.print(f"  [dim]· {i['name']} ({i['max']:.0f} pts)[/dim]")
        if len(ungraded) > 10:
            console.print(f"  [dim]... +{len(ungraded) - 10} more[/dim]")
        console.print(
            "\n[dim]Pass --score \"Name=85\" or --assume-all 90 to fill them in.[/dim]"
        )
