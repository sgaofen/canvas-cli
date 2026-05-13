"""`canvas submit <course> <assignment>` — submit an assignment from the terminal.

Supports the three submission types most UCI homework uses:
  --text / --text-file       online_text_entry (Markdown auto-rendered to HTML)
  --url <URL>                online_url
  --file <path>              online_upload (repeatable; uploads then attaches)

Submission is irreversible from the student side, so the command shows a
preview and prompts for confirmation unless `--yes` is passed. `--dry-run`
shows the preview and exits without contacting Canvas.
"""

from __future__ import annotations

import html as _html
import json as _json
from pathlib import Path
from typing import List, Optional

import typer
from canvasapi.exceptions import CanvasException
from rich.console import Console

from ..client import get_user_courses
from ..matchers import extract_short_code, resolve_assignment, resolve_course

console = Console()
err_console = Console(stderr=True)


def _text_to_html(raw: str, use_markdown: bool) -> str:
    """Render submission body. Markdown by default; --no-markdown wraps as <pre>."""
    if not use_markdown:
        return f"<pre>{_html.escape(raw)}</pre>"
    try:
        import markdown as _md
        return _md.markdown(
            raw, extensions=["fenced_code", "tables", "sane_lists", "nl2br"]
        )
    except ImportError:
        # Fallback: paragraph-wrap newlines
        paras = raw.strip().split("\n\n")
        return "\n".join(f"<p>{_html.escape(p)}</p>" for p in paras if p)


def submit(
    course: str = typer.Argument(..., help="Course short code or id"),
    assignment: str = typer.Argument(..., help="Assignment name substring or id"),
    text: Optional[str] = typer.Option(
        None, "--text", help="Inline text body (Markdown-rendered)"
    ),
    text_file: Optional[Path] = typer.Option(
        None, "--text-file", help="Read body from a file (Markdown-rendered)"
    ),
    url: Optional[str] = typer.Option(
        None, "--url", help="Submit a URL"
    ),
    files: List[Path] = typer.Option(
        [], "--file", "-f", help="File(s) to upload (repeatable)"
    ),
    comment: Optional[str] = typer.Option(
        None, "--comment", help="Optional comment to instructor"
    ),
    no_markdown: bool = typer.Option(
        False, "--no-markdown",
        help="Don't render text as Markdown; submit as preformatted text",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show preview, don't actually submit"
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Skip confirmation prompt"
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON envelope"),
) -> None:
    """Submit work to a Canvas assignment."""
    modes = [bool(text), bool(text_file), bool(url), bool(files)]
    if sum(modes) == 0:
        err_console.print(
            "[red]Specify one of --text / --text-file / --url / --file[/red]"
        )
        raise typer.Exit(code=2)
    if sum(modes) > 1:
        err_console.print(
            "[red]Pick only one submission mode[/red] (text / url / file)"
        )
        raise typer.Exit(code=2)

    courses = get_user_courses(active_only=True)
    target_course = resolve_course(courses, course)
    target_assn = resolve_assignment(target_course, assignment)

    submission_type: str
    submission_payload: dict
    summary: str
    body_source = ""

    if text is not None or text_file is not None:
        if text_file is not None:
            if not text_file.exists():
                err_console.print(f"[red]File not found:[/red] {text_file}")
                raise typer.Exit(code=2)
            body_source = text_file.read_text()
        else:
            body_source = text or ""
        rendered = _text_to_html(body_source, use_markdown=not no_markdown)
        submission_type = "online_text_entry"
        submission_payload = {"submission_type": submission_type, "body": rendered}
        summary = (
            f"text entry — {len(body_source)} chars source"
            f"{' (Markdown)' if not no_markdown else ' (raw <pre>)'}"
        )
    elif url is not None:
        submission_type = "online_url"
        submission_payload = {"submission_type": submission_type, "url": url}
        summary = f"URL: {url}"
    else:
        # Validate files exist BEFORE confirmation
        missing = [p for p in files if not p.exists()]
        if missing:
            err_console.print(
                "[red]File(s) not found:[/red] " + ", ".join(str(m) for m in missing)
            )
            raise typer.Exit(code=2)
        submission_type = "online_upload"
        submission_payload = {"submission_type": submission_type}  # file_ids added after upload
        total_bytes = sum(p.stat().st_size for p in files)
        summary = (
            f"file upload — {len(files)} file(s), "
            f"{total_bytes / 1024:.1f} KB total"
        )

    short = extract_short_code(getattr(target_course, "name", "") or "") or target_course.name
    submission_types_allowed = list(getattr(target_assn, "submission_types", []) or [])

    preview = {
        "course": short,
        "course_id": getattr(target_course, "id", None),
        "assignment": getattr(target_assn, "name", None),
        "assignment_id": getattr(target_assn, "id", None),
        "due_at": getattr(target_assn, "due_at", None),
        "points_possible": getattr(target_assn, "points_possible", None),
        "submission_type": submission_type,
        "comment": comment,
        "files": [str(p) for p in files] if files else None,
        "url": url,
        "text_chars": len(body_source) if body_source else None,
        "allowed_submission_types": submission_types_allowed,
    }

    if submission_type not in submission_types_allowed and submission_types_allowed:
        err_console.print(
            f"[red]Assignment does not accept '{submission_type}'[/red] — "
            f"allowed: {', '.join(submission_types_allowed)}"
        )
        raise typer.Exit(code=2)

    if not json_out:
        console.print(f"\n[bold]Submission preview[/bold]")
        console.print(f"  Course:     [green]{short}[/green] ([dim]id {target_course.id}[/dim])")
        console.print(f"  Assignment: {target_assn.name} ([dim]id {target_assn.id}[/dim])")
        console.print(f"  Due:        {preview['due_at'] or '—'}")
        console.print(f"  Worth:      {preview['points_possible'] or '—'} pts")
        console.print(f"  Type:       {summary}")
        if comment:
            console.print(f"  Comment:    {comment!r}")
        if files:
            for p in files:
                console.print(f"    [dim]· {p}[/dim] ({p.stat().st_size} bytes)")

    if dry_run:
        if json_out:
            print(_json.dumps({"dry_run": True, "preview": preview}))
        else:
            console.print("\n[cyan]dry-run — no API call made.[/cyan]")
        return

    if not yes and not json_out:
        if not typer.confirm(
            "\nSubmission is irreversible. Continue?", default=False
        ):
            console.print("Aborted.")
            raise typer.Exit()

    # Execute: handle file uploads first, then call submit
    try:
        if submission_type == "online_upload":
            file_ids: list[int] = []
            for fp in files:
                if not json_out:
                    console.print(f"  [dim]uploading[/dim] {fp.name} ...")
                success, response = target_assn.upload_to_submission(
                    str(fp), on_duplicate="rename"
                )
                if not success or "id" not in response:
                    err_console.print(
                        f"[red]Upload failed for {fp.name}:[/red] {response}"
                    )
                    raise typer.Exit(code=1)
                file_ids.append(int(response["id"]))
            submission_payload["file_ids"] = file_ids

        kwargs = {"submission": submission_payload}
        if comment:
            kwargs["comment"] = {"text_comment": comment}

        result = target_assn.submit(**kwargs)
    except CanvasException as exc:
        err_console.print(f"[red]Submission failed:[/red] {exc}")
        if json_out:
            print(_json.dumps({"error": str(exc), "preview": preview}))
        raise typer.Exit(code=1)

    result_dict = {
        "submission_id": getattr(result, "id", None),
        "submitted_at": getattr(result, "submitted_at", None),
        "workflow_state": getattr(result, "workflow_state", None),
        "attempt": getattr(result, "attempt", None),
        "preview_url": getattr(result, "preview_url", None),
        "submission_type": getattr(result, "submission_type", submission_type),
    }

    if json_out:
        print(_json.dumps({"ok": True, "preview": preview, "result": result_dict}))
        return

    console.print(f"\n[bold green]Submitted[/bold green]")
    console.print(f"  Submission ID: {result_dict['submission_id']}")
    console.print(f"  State:         {result_dict['workflow_state']}")
    console.print(f"  Attempt:       {result_dict['attempt']}")
    console.print(f"  At:            {result_dict['submitted_at']}")
    if result_dict["preview_url"]:
        console.print(f"  Preview:       [dim]{result_dict['preview_url']}[/dim]")
