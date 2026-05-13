"""`canvas quizzes` + `canvas quiz` — list, inspect, and take Canvas quizzes.

The Quizzes tab can be hidden by faculty (`/courses/:id/quizzes` returns 404),
but individual quizzes are still accessible by id via the assignment-level
`quiz_id`. We fall back to walking assignments when the listing endpoint 404s.

Supported question types in `quiz take`:
  multiple_choice_question      → letter (A/B/C/...) or option index
  true_false_question           → "true"/"false"
  short_answer_question         → free text
  essay_question                → free text (treated as paragraph)
  multiple_answers_question     → comma-separated letters (A,C)

Other types (numerical, calculated, matching, fill_in_*, file_upload) print a
notice and skip the question. Use the Canvas web UI for those.
"""

from __future__ import annotations

import html as _html
import json as _json
import re
from pathlib import Path
from typing import Optional

import html2text
import typer
from canvasapi.exceptions import CanvasException, ResourceDoesNotExist
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from ..client import get_user_courses
from ..matchers import extract_short_code, resolve_course

console = Console()
err_console = Console(stderr=True)


def _html_to_text(html: str) -> str:
    if not html:
        return ""
    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_images = True
    return h.handle(html).strip()


def _list_quizzes_for_course(target) -> list[dict]:
    """Return quizzes via Quizzes API, falling back to assignment quiz_id walk."""
    rows: list[dict] = []

    # Try Quizzes API first
    try:
        for q in target.get_quizzes():
            rows.append({
                "quiz_id": getattr(q, "id", None),
                "title": getattr(q, "title", None),
                "quiz_type": getattr(q, "quiz_type", None),
                "question_count": getattr(q, "question_count", None),
                "points_possible": getattr(q, "points_possible", None),
                "due_at": getattr(q, "due_at", None),
                "lock_at": getattr(q, "lock_at", None),
                "locked_for_user": getattr(q, "locked_for_user", None),
                "allowed_attempts": getattr(q, "allowed_attempts", None),
                "time_limit": getattr(q, "time_limit", None),
                "_via": "quizzes-api",
            })
        return rows
    except (ResourceDoesNotExist, CanvasException):
        pass

    # Fallback: walk assignments
    try:
        assigns = list(target.get_assignments(include=["submission"]))
    except CanvasException:
        return rows

    for a in assigns:
        qid = getattr(a, "quiz_id", None)
        if not qid:
            continue
        sub = getattr(a, "submission", None) or {}
        if not isinstance(sub, dict):
            sub = {}
        try:
            q = target.get_quiz(qid)
        except (ResourceDoesNotExist, CanvasException):
            continue
        rows.append({
            "quiz_id": qid,
            "assignment_id": getattr(a, "id", None),
            "title": getattr(q, "title", None) or getattr(a, "name", None),
            "quiz_type": getattr(q, "quiz_type", None),
            "question_count": getattr(q, "question_count", None),
            "points_possible": getattr(q, "points_possible", None),
            "due_at": getattr(q, "due_at", None) or getattr(a, "due_at", None),
            "lock_at": getattr(q, "lock_at", None),
            "locked_for_user": getattr(q, "locked_for_user", None),
            "allowed_attempts": getattr(q, "allowed_attempts", None),
            "time_limit": getattr(q, "time_limit", None),
            "current_score": sub.get("score"),
            "submission_state": sub.get("workflow_state"),
            "_via": "assignment-fallback",
        })
    return rows


def quizzes(
    course: str = typer.Argument(..., help="Course short code or id"),
    open_only: bool = typer.Option(
        False, "--open", help="Show only quizzes not locked + not yet completed"
    ),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """List quizzes in a course."""
    courses_ = get_user_courses(active_only=True)
    target = resolve_course(courses_, course)
    rows = _list_quizzes_for_course(target)

    if open_only:
        # "open" = not locked AND haven't earned full credit yet. A graded_survey
        # can have submission_state="graded" with score=0 if the user never
        # actually submitted answers — that's still open.
        def _is_open(r: dict) -> bool:
            if r.get("locked_for_user"):
                return False
            score = r.get("current_score")
            max_pts = r.get("points_possible")
            if isinstance(score, (int, float)) and isinstance(max_pts, (int, float)):
                return score < max_pts
            return True  # unknown → keep
        rows = [r for r in rows if _is_open(r)]

    if json_out:
        print(_json.dumps(rows))
        return

    if not rows:
        console.print(f"[yellow]No quizzes in[/yellow] {target.name}")
        return

    table = Table(
        title=f"Quizzes — {target.name} ({len(rows)})",
        header_style="bold cyan",
    )
    table.add_column("quiz_id", style="dim", no_wrap=True)
    table.add_column("Title")
    table.add_column("Type", style="dim", no_wrap=True)
    table.add_column("Qs", justify="right", no_wrap=True)
    table.add_column("Pts", justify="right", no_wrap=True)
    table.add_column("Score", justify="right", style="yellow", no_wrap=True)
    table.add_column("Locked", justify="center", no_wrap=True)

    for r in rows:
        score = r.get("current_score")
        score_str = f"{score:.0f}" if isinstance(score, (int, float)) else "—"
        locked = "[red]✓[/red]" if r.get("locked_for_user") else "[dim]·[/dim]"
        table.add_row(
            str(r.get("quiz_id", "?")),
            r.get("title") or "?",
            r.get("quiz_type") or "?",
            str(r.get("question_count") or "?"),
            str(r.get("points_possible") or "?"),
            score_str,
            locked,
        )
    console.print(table)


def _resolve_quiz(target, query: str):
    """Resolve a quiz by numeric id or title substring."""
    if query.isdigit():
        try:
            return target.get_quiz(int(query))
        except (ResourceDoesNotExist, CanvasException):
            pass

    rows = _list_quizzes_for_course(target)
    needle = query.lower().strip()
    matches = [r for r in rows if needle in (r.get("title") or "").lower()]
    if not matches:
        err_console.print(f"[red]No quiz matches[/red] '{query}'")
        raise typer.Exit(code=1)
    if len(matches) == 1:
        return target.get_quiz(matches[0]["quiz_id"])

    err_console.print(f"[yellow]Multiple quizzes match '{query}':[/yellow]")
    for i, r in enumerate(matches, 1):
        err_console.print(f"  {i}. {r['title']} (id={r['quiz_id']})")
    choice = typer.prompt("Pick number", type=int)
    return target.get_quiz(matches[choice - 1]["quiz_id"])


def quiz(
    course: str = typer.Argument(..., help="Course short code or id"),
    quiz_ref: str = typer.Argument(..., help="Quiz id or title substring"),
    take: bool = typer.Option(False, "--take", help="Start interactive answering"),
    answers: Optional[Path] = typer.Option(
        None, "--answers",
        help="JSON file mapping question_id → answer, for non-interactive submit",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="With --take: preview answers, don't complete"
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Skip the final 'complete attempt' confirmation"
    ),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Inspect a quiz, or take it interactively with --take."""
    courses_ = get_user_courses(active_only=True)
    target = resolve_course(courses_, course)
    q = _resolve_quiz(target, quiz_ref)

    info = {
        "quiz_id": q.id,
        "title": getattr(q, "title", None),
        "quiz_type": getattr(q, "quiz_type", None),
        "question_count": getattr(q, "question_count", None),
        "points_possible": getattr(q, "points_possible", None),
        "due_at": getattr(q, "due_at", None),
        "lock_at": getattr(q, "lock_at", None),
        "locked_for_user": getattr(q, "locked_for_user", None),
        "allowed_attempts": getattr(q, "allowed_attempts", None),
        "time_limit": getattr(q, "time_limit", None),
    }

    if not take:
        if json_out:
            print(_json.dumps(info))
            return
        console.print(Panel(
            "\n".join(f"  {k:<18} {v}" for k, v in info.items()),
            title=info["title"] or "?",
            border_style="cyan",
        ))
        if info["locked_for_user"]:
            console.print("\n[red]Locked for you.[/red] Run with --take after instructor unlocks.")
        else:
            console.print("\nRun [cyan]canvas quiz <course> <id> --take[/cyan] to start an attempt.")
        return

    # --- TAKE flow ---
    if info["locked_for_user"]:
        err_console.print("[red]Quiz is locked for you — cannot start a new attempt.[/red]")
        raise typer.Exit(code=1)

    answer_map: dict[int, object] = {}
    if answers is not None:
        if not answers.exists():
            err_console.print(f"[red]Answers file not found:[/red] {answers}")
            raise typer.Exit(code=2)
        try:
            answer_map = {int(k): v for k, v in _json.loads(answers.read_text()).items()}
        except (ValueError, OSError) as exc:
            err_console.print(f"[red]Failed to parse answers JSON:[/red] {exc}")
            raise typer.Exit(code=2)

    # Resume existing untaken submission if any, else start new
    submission = None
    try:
        for s in q.get_submissions():
            if getattr(s, "workflow_state", "") == "untaken":
                submission = s
                break
    except CanvasException:
        pass
    if submission is None:
        try:
            submission = q.create_submission()
        except CanvasException as exc:
            err_console.print(f"[red]Could not start attempt:[/red] {exc}")
            raise typer.Exit(code=1)

    sub_id = submission.id
    attempt = getattr(submission, "attempt", 1)
    if not json_out:
        console.print(
            f"\n[bold]Attempt {attempt}[/bold] on [cyan]{info['title']}[/cyan] "
            f"(submission id {sub_id})"
        )

    # Fetch this attempt's questions
    try:
        questions = list(submission.get_submission_questions())
    except CanvasException as exc:
        err_console.print(f"[red]Failed to load questions:[/red] {exc}")
        raise typer.Exit(code=1)

    if not json_out:
        console.print(f"[dim]{len(questions)} question(s)[/dim]\n")

    answers_payload: list[dict] = []

    for i, qq in enumerate(questions, 1):
        qid = qq.id
        qtype = getattr(qq, "question_type", "?")
        qtext_html = getattr(qq, "question_text", "") or ""
        qtext = _html_to_text(qtext_html)
        if not json_out:
            console.print(f"[bold]Q{i}[/bold] [dim]({qtype}, id={qid})[/dim]")
            console.print(Markdown(qtext) if qtext else "[dim](no text)[/dim]")

        # text_only_question is purely informational — no answer required
        if qtype == "text_only_question":
            if not json_out:
                console.print("  [dim](informational only — no answer needed)[/dim]\n")
            continue

        # Pre-supplied answer wins
        if qid in answer_map:
            user_answer = _normalize_answer_payload(qtype, answer_map[qid])
            if not json_out:
                preview = user_answer if isinstance(user_answer, str) else str(user_answer)
                console.print(f"  → using --answers entry: {preview[:120]!r}")
        else:
            user_answer = _prompt_for_answer(qq, qtype, json_out=json_out)

        if user_answer is None:
            if not json_out:
                console.print("  [dim](skipped)[/dim]\n")
            continue

        answers_payload.append({"id": qid, "answer": user_answer})
        if not json_out:
            console.print()

    if not answers_payload:
        err_console.print("[yellow]No answers provided — aborting.[/yellow]")
        raise typer.Exit(code=1)

    if dry_run:
        result = {
            "dry_run": True, "quiz_id": q.id, "submission_id": sub_id,
            "attempt": attempt, "answers": answers_payload,
        }
        if json_out:
            print(_json.dumps(result))
        else:
            console.print(
                f"[cyan]dry-run[/cyan] — would save {len(answers_payload)} answer(s) "
                f"and complete attempt {attempt}. No write performed."
            )
            console.print(_json.dumps(answers_payload, indent=2))
        return

    # Save answers
    try:
        submission.answer_submission_questions(quiz_questions=answers_payload)
    except CanvasException as exc:
        err_console.print(f"[red]Saving answers failed:[/red] {exc}")
        raise typer.Exit(code=1)

    if not yes and not json_out:
        if not typer.confirm(
            f"\nComplete attempt and submit {len(answers_payload)} answer(s)?",
            default=False,
        ):
            console.print(
                "Answers saved but attempt left open. "
                "Re-run with --take to resume, or visit Canvas to complete."
            )
            raise typer.Exit()

    try:
        completed = submission.complete()
    except CanvasException as exc:
        err_console.print(f"[red]Complete failed:[/red] {exc}")
        raise typer.Exit(code=1)

    result = {
        "quiz_id": q.id, "submission_id": sub_id,
        "attempt": attempt,
        "answers_saved": len(answers_payload),
        "workflow_state": getattr(completed, "workflow_state", None),
        "score": getattr(completed, "score", None),
        "finished_at": getattr(completed, "finished_at", None),
    }
    if json_out:
        print(_json.dumps(result))
        return
    console.print(f"\n[bold green]Quiz submitted[/bold green]")
    for k, v in result.items():
        console.print(f"  {k:<18} {v}")


def _prompt_for_answer(qq, qtype: str, json_out: bool):
    """Render question options and prompt the user for an answer.

    Returns the answer value in the shape Canvas expects, or None to skip.
    Dispatches to per-type handlers — each handler is responsible for
    displaying its own options/blanks and returning a Canvas-shaped value.
    """
    handler = _TYPE_HANDLERS.get(qtype)
    if handler is None:
        err_console.print(
            f"  [yellow]Question type {qtype!r} not supported; "
            "use Canvas web UI for this one.[/yellow]"
        )
        return None
    return handler(qq)


def _normalize_answer_payload(qtype: str, value):
    """Convert a friendly --answers JSON value into the Canvas API shape.

    Friendly shapes accepted:
      essay_question                     str  →  <p>str</p>
      matching_question                  {answer_id: match_id} dict
                                         →  [{answer_id, match_id}, ...]
      file_upload_question               int / list[int]  →  list[int]
                                         (file ids; uploading by path is not
                                          yet supported — pre-upload + pass id)

    Anything already in Canvas shape (or a string that looks like HTML)
    is passed through unchanged.
    """
    if value is None:
        return None
    if qtype == "essay_question" and isinstance(value, str) and "<" not in value:
        return f"<p>{_html.escape(value)}</p>"
    if qtype == "matching_question" and isinstance(value, dict):
        return [
            {"answer_id": str(k), "match_id": str(v)}
            for k, v in value.items()
        ]
    if qtype == "file_upload_question":
        if isinstance(value, int):
            return [value]
        if isinstance(value, list):
            return [int(v) for v in value]
    return value


# ---------- per-type interactive prompt handlers ----------

def _prompt_mc_single(qq):
    """multiple_choice_question / true_false_question → option id (int)."""
    answers = getattr(qq, "answers", None) or []
    if not answers:
        err_console.print("  [yellow](no answer options returned)[/yellow]")
        return None
    for idx, a in enumerate(answers):
        letter = chr(ord("A") + idx)
        text = _html_to_text(a.get("html") or a.get("text") or "")
        console.print(f"  [cyan]{letter}[/cyan]. {text}  [dim](id={a.get('id')})[/dim]")
    raw = typer.prompt("  → letter or 'skip'", default="skip").strip().upper()
    if raw == "SKIP" or not raw:
        return None
    if len(raw) == 1 and "A" <= raw <= "Z":
        i = ord(raw) - ord("A")
        if 0 <= i < len(answers):
            return int(answers[i]["id"])
    err_console.print(f"  [yellow]Invalid choice {raw!r}, skipping[/yellow]")
    return None


def _prompt_mc_multi(qq):
    """multiple_answers_question → list[int] of option ids."""
    answers = getattr(qq, "answers", None) or []
    if not answers:
        return None
    for idx, a in enumerate(answers):
        letter = chr(ord("A") + idx)
        text = _html_to_text(a.get("html") or a.get("text") or "")
        console.print(f"  [cyan]{letter}[/cyan]. {text}  [dim](id={a.get('id')})[/dim]")
    raw = typer.prompt("  → letters (comma-separated) or 'skip'", default="skip").strip()
    if raw.lower() == "skip":
        return None
    picks: list[int] = []
    for token in re.split(r"[,\s]+", raw):
        token = token.strip().upper()
        if len(token) == 1 and "A" <= token <= "Z":
            i = ord(token) - ord("A")
            if 0 <= i < len(answers):
                picks.append(int(answers[i]["id"]))
    return picks or None


def _prompt_matching(qq):
    """matching_question → [{answer_id, match_id}, ...].

    Canvas returns:
      answers: [{id, text}, ...]    ← left column (prompts to match)
      matches: [{match_id, text}, ...]  ← right pool (options)
    """
    answers = getattr(qq, "answers", None) or []
    matches = getattr(qq, "matches", None) or []
    if not answers or not matches:
        err_console.print("  [yellow](missing matching data)[/yellow]")
        return None

    console.print("\n  [bold]Right-side options:[/bold]")
    for i, m in enumerate(matches):
        letter = chr(ord("A") + i)
        console.print(
            f"    [cyan]{letter}[/cyan]. {_html_to_text(m.get('text', ''))}"
            f"  [dim](match_id={m.get('match_id')})[/dim]"
        )

    pairs = []
    for left in answers:
        text = _html_to_text(left.get("text", ""))
        console.print(f"\n  Match for: [yellow]{text}[/yellow]")
        raw = typer.prompt("    → letter or 'skip'", default="skip").strip().upper()
        if raw == "SKIP" or not raw:
            continue
        if len(raw) == 1 and "A" <= raw <= "Z":
            i = ord(raw) - ord("A")
            if 0 <= i < len(matches):
                pairs.append({
                    "answer_id": str(left["id"]),
                    "match_id": str(matches[i]["match_id"]),
                })
    return pairs or None


def _prompt_short_answer(qq):
    """short_answer_question → str."""
    raw = typer.prompt("  → answer (or 'skip')", default="skip")
    return None if raw.strip().lower() == "skip" or not raw.strip() else raw


def _prompt_essay(qq):
    """essay_question → HTML string wrapped in <p>."""
    raw = typer.prompt("  → essay (or 'skip')", default="skip")
    if raw.strip().lower() == "skip" or not raw.strip():
        return None
    return f"<p>{_html.escape(raw)}</p>"


def _prompt_numerical(qq):
    """numerical_question / calculated_question → numeric string."""
    raw = typer.prompt("  → number (or 'skip')", default="skip")
    if raw.strip().lower() == "skip":
        return None
    try:
        float(raw)
    except ValueError:
        err_console.print(f"  [yellow]{raw!r} is not a number, skipping[/yellow]")
        return None
    return raw


def _prompt_fill_blanks(qq):
    """fill_in_multiple_blanks_question → {blank_name: text}.

    Canvas marks blanks inline in question_text with [blank_name] tokens.
    Discover them by inspecting the answers array: each answer has a
    `blank_id` (the blank name) and a possible canonical text.
    """
    blank_names = _blank_names_from_answers(getattr(qq, "answers", None) or [])
    if not blank_names:
        err_console.print("  [yellow](no blanks found)[/yellow]")
        return None
    out: dict[str, str] = {}
    for name in blank_names:
        raw = typer.prompt(f"  → [{name}] (or 'skip')", default="skip")
        if raw.strip().lower() == "skip" or not raw.strip():
            continue
        out[name] = raw
    return out or None


def _prompt_multi_dropdowns(qq):
    """multiple_dropdowns_question → {blank_name: option_id}.

    Each answer item has blank_id (which dropdown) + id (option id) + text.
    Group by blank_id, show options letter-indexed within each group.
    """
    answers = getattr(qq, "answers", None) or []
    if not answers:
        return None
    by_blank: dict[str, list[dict]] = {}
    for a in answers:
        bid = a.get("blank_id") or a.get("blank_name") or "default"
        by_blank.setdefault(bid, []).append(a)

    out: dict[str, int] = {}
    for blank, opts in by_blank.items():
        console.print(f"\n  Blank [yellow][{blank}][/yellow]:")
        for i, a in enumerate(opts):
            letter = chr(ord("A") + i)
            text = _html_to_text(a.get("text", ""))
            console.print(
                f"    [cyan]{letter}[/cyan]. {text}  [dim](id={a.get('id')})[/dim]"
            )
        raw = typer.prompt("    → letter or 'skip'", default="skip").strip().upper()
        if raw == "SKIP" or not raw:
            continue
        if len(raw) == 1 and "A" <= raw <= "Z":
            i = ord(raw) - ord("A")
            if 0 <= i < len(opts):
                out[blank] = int(opts[i]["id"])
    return out or None


def _prompt_file_upload(qq):
    """file_upload_question → list[int] of pre-uploaded file ids.

    Uploading from local path inline is not yet wired up here — Canvas
    requires a two-step upload via the submission's own files endpoint,
    which differs from the assignment upload path. For now, ask the user
    for already-uploaded file IDs (or use the Canvas web UI).
    """
    raw = typer.prompt(
        "  → file id(s), comma-separated (or 'skip', or 'web' to use Canvas web UI)",
        default="skip",
    ).strip().lower()
    if raw in ("skip", "web", ""):
        if raw == "web":
            console.print(
                "  [dim]File upload via terminal not yet implemented — "
                "upload via Canvas web and re-run with --answers JSON.[/dim]"
            )
        return None
    ids: list[int] = []
    for tok in re.split(r"[,\s]+", raw):
        if tok.isdigit():
            ids.append(int(tok))
    return ids or None


def _blank_names_from_answers(answers: list[dict]) -> list[str]:
    seen: list[str] = []
    for a in answers:
        name = a.get("blank_id") or a.get("blank_name")
        if name and name not in seen:
            seen.append(name)
    return seen


_TYPE_HANDLERS: dict[str, callable] = {
    "multiple_choice_question": _prompt_mc_single,
    "true_false_question": _prompt_mc_single,
    "multiple_answers_question": _prompt_mc_multi,
    "matching_question": _prompt_matching,
    "short_answer_question": _prompt_short_answer,
    "essay_question": _prompt_essay,
    "numerical_question": _prompt_numerical,
    "calculated_question": _prompt_numerical,
    "fill_in_multiple_blanks_question": _prompt_fill_blanks,
    "multiple_dropdowns_question": _prompt_multi_dropdowns,
    "file_upload_question": _prompt_file_upload,
}
