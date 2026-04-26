"""`canvas extract <course>` — autonomous course knowledge base.

In one command, gathers everything an AI agent would need to "understand" a
course: syllabus, all Pages, all Modules + items, file metadata, assignments.
With `--follow-links`, also fetches every external URL referenced (Google Docs,
public PDFs) and embeds the extracted content.

Output is a single JSON blob (or saved to <sync_dir>/<course>/.extract.json).
"""

from __future__ import annotations

import json as _json
from datetime import datetime, timezone
from pathlib import Path

import html2text
import httpx
import typer
from canvasapi.exceptions import CanvasException, Forbidden, ResourceDoesNotExist
from rich.console import Console

from ..client import get_canvas, get_user_courses
from ..config import load_config
from ..extract import extract_by_filename, extract_links, to_markdown
from ..matchers import extract_short_code, resolve_course

console = Console()
err_console = Console(stderr=True)


_GDOCS_RE = __import__("re").compile(
    r"^(https://docs\.google\.com/(document|spreadsheets|presentation)/d/[^/]+)(/(edit|view|preview)?)?(\?.*)?$"
)


def _normalize_gdocs(url: str) -> str:
    m = _GDOCS_RE.match(url)
    if not m:
        return url
    base, kind = m.group(1), m.group(2)
    fmt = {"document": "txt", "spreadsheets": "csv", "presentation": "txt"}[kind]
    return f"{base}/export?format={fmt}"


def extract(
    course: str = typer.Argument(..., help="Course short code or id"),
    follow_links: bool = typer.Option(
        False, "--follow-links", help="Also fetch external URLs (Google Docs, PDFs, etc.)"
    ),
    save: bool = typer.Option(
        False, "--save", help="Write to <sync_dir>/<short_code>/.extract.json"
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON to stdout"),
) -> None:
    """Build a comprehensive knowledge base for one course."""
    courses = get_user_courses(active_only=True)
    target = resolve_course(courses, course)
    short = extract_short_code(getattr(target, "name", "") or "") or "?"

    if not json_out:
        console.print(f"[bold cyan]Extracting[/bold cyan] {short} — {target.name}")

    bundle: dict = {
        "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "course": {
            "id": getattr(target, "id", None),
            "name": getattr(target, "name", None),
            "short_code": short,
        },
        "syllabus": _fetch_syllabus(target, json_out),
        "pages": _fetch_all_pages(target, json_out),
        "modules": _fetch_all_modules(target, json_out),
        "files": _list_files(target, json_out),
        "assignments": _list_assignments(target, json_out),
        "announcements": _list_announcements(target, json_out),
    }

    # Sweep external URLs from all text-bearing fields
    urls = set()
    if bundle["syllabus"] and bundle["syllabus"].get("markdown"):
        urls.update(extract_links(bundle["syllabus"]["markdown"]))
    for p in bundle["pages"]:
        if p.get("markdown"):
            urls.update(extract_links(p["markdown"]))
    for m in bundle["modules"]:
        for item in m.get("items", []):
            if item.get("type") == "ExternalUrl" and item.get("external_url"):
                urls.add(item["external_url"])

    # Filter out internal Canvas URLs and noise
    external = sorted(
        u for u in urls
        if not any(x in u for x in [
            "canvas.eee.uci.edu/courses/", "mailto:",
            "fonts.googleapis", "fonts.gstatic",
        ])
    )
    bundle["external_urls"] = external

    if follow_links:
        if not json_out:
            console.print(f"  [dim]following {len(external)} external URLs...[/dim]")
        bundle["external_content"] = [_fetch_external(u) for u in external]

    counts = {
        "pages": len(bundle["pages"]),
        "modules": len(bundle["modules"]),
        "module_items": sum(len(m.get("items", [])) for m in bundle["modules"]),
        "files": len(bundle["files"]),
        "assignments": len(bundle["assignments"]),
        "announcements": len(bundle["announcements"]),
        "external_urls": len(external),
    }
    bundle["counts"] = counts

    if save:
        config = load_config()
        sync_root = Path(config["sync_dir"]).expanduser()
        course_dir = sync_root / short
        course_dir.mkdir(parents=True, exist_ok=True)
        out_path = course_dir / ".extract.json"
        out_path.write_text(_json.dumps(bundle, indent=2, default=str))
        if not json_out:
            console.print(f"  [green]saved[/green] {out_path}")

    if json_out:
        print(_json.dumps(bundle, default=str))
    else:
        console.print(f"\n[bold]Summary[/bold]")
        for k, v in counts.items():
            console.print(f"  {k:<20} {v}")
        if bundle["syllabus"] and bundle["syllabus"].get("has_content"):
            console.print(f"  syllabus_chars       {len(bundle['syllabus']['markdown'])}")


def _fetch_syllabus(target, quiet: bool) -> dict | None:
    canvas = get_canvas()
    try:
        full = canvas.get_course(target.id, include=["syllabus_body"])
    except CanvasException as exc:
        if not quiet:
            err_console.print(f"  [yellow]syllabus failed:[/yellow] {exc}")
        return None
    html = getattr(full, "syllabus_body", "") or ""
    return {
        "html": html,
        "markdown": to_markdown(html),
        "has_content": bool(html.strip()),
    }


def _fetch_all_pages(target, quiet: bool) -> list[dict]:
    try:
        page_list = list(target.get_pages())
    except (Forbidden, ResourceDoesNotExist, CanvasException):
        return []
    out: list[dict] = []
    for p in page_list:
        url = getattr(p, "url", None)
        if not url:
            continue
        try:
            full = target.get_page(url)
        except CanvasException:
            continue
        html = getattr(full, "body", "") or ""
        out.append({
            "page_id": getattr(full, "page_id", None),
            "title": getattr(full, "title", None),
            "url": url,
            "updated_at": getattr(full, "updated_at", None),
            "front_page": getattr(full, "front_page", False),
            "html": html,
            "markdown": to_markdown(html),
        })
    return out


def _fetch_all_modules(target, quiet: bool) -> list[dict]:
    try:
        mods = list(target.get_modules())
    except (Forbidden, CanvasException):
        return []
    out: list[dict] = []
    for m in mods:
        try:
            items = list(m.get_module_items())
        except CanvasException:
            items = []
        out.append({
            "module_id": getattr(m, "id", None),
            "name": getattr(m, "name", None),
            "position": getattr(m, "position", None),
            "state": getattr(m, "state", None),
            "items": [
                {
                    "item_id": getattr(i, "id", None),
                    "title": getattr(i, "title", None),
                    "type": getattr(i, "type", None),
                    "content_id": getattr(i, "content_id", None),
                    "page_url": getattr(i, "page_url", None),
                    "html_url": getattr(i, "html_url", None),
                    "external_url": getattr(i, "external_url", None),
                }
                for i in items
            ],
        })
    return out


def _list_files(target, quiet: bool) -> list[dict]:
    try:
        files = list(target.get_files())
    except (Forbidden, CanvasException):
        return []
    try:
        folders = list(target.get_folders())
    except CanvasException:
        folders = []
    folder_map = {getattr(f, "id", None): f for f in folders}
    out = []
    for f in files:
        folder = folder_map.get(getattr(f, "folder_id", None))
        out.append({
            "file_id": getattr(f, "id", None),
            "name": getattr(f, "display_name", None),
            "size": getattr(f, "size", None),
            "updated_at": getattr(f, "updated_at", None),
            "folder": getattr(folder, "full_name", None) if folder else None,
        })
    return out


def _list_assignments(target, quiet: bool) -> list[dict]:
    try:
        assigns = list(target.get_assignments(include=["submission"]))
    except CanvasException:
        return []
    out = []
    for a in assigns:
        sub = getattr(a, "submission", None) or {}
        if not isinstance(sub, dict):
            sub = {}
        desc_html = getattr(a, "description", "") or ""
        out.append({
            "assignment_id": getattr(a, "id", None),
            "name": getattr(a, "name", None),
            "due_at": getattr(a, "due_at", None),
            "points_possible": getattr(a, "points_possible", None),
            "submission_state": sub.get("workflow_state"),
            "score": sub.get("score"),
            "description_markdown": to_markdown(desc_html),
            "html_url": getattr(a, "html_url", None),
        })
    return out


def _list_announcements(target, quiet: bool) -> list[dict]:
    canvas = get_canvas()
    try:
        anns = list(canvas.get_announcements(context_codes=[f"course_{target.id}"]))
    except CanvasException:
        return []
    out = []
    for a in anns:
        body = getattr(a, "message", "") or ""
        out.append({
            "id": getattr(a, "id", None),
            "title": getattr(a, "title", None),
            "posted_at": getattr(a, "posted_at", None) or getattr(a, "created_at", None),
            "url": getattr(a, "html_url", None),
            "body_markdown": to_markdown(body),
        })
    return out


def _fetch_external(url: str) -> dict:
    fetch_url = _normalize_gdocs(url)
    try:
        with httpx.Client(
            timeout=httpx.Timeout(20.0, read=60.0),
            follow_redirects=True,
            headers={"User-Agent": "canvas-cli-extract/0.1"},
        ) as client:
            resp = client.get(fetch_url)
            resp.raise_for_status()
            data = resp.content
            ct = resp.headers.get("content-type", "").lower()
    except httpx.HTTPError as exc:
        return {"requested_url": url, "fetched_url": fetch_url, "error": str(exc)}

    lower_url = fetch_url.lower()
    if "application/pdf" in ct or lower_url.endswith(".pdf"):
        from ..extract import extract_pdf
        text, kind = extract_pdf(data), "pdf"
    elif "officedocument.wordprocessingml" in ct or lower_url.endswith(".docx"):
        from ..extract import extract_docx
        text, kind = extract_docx(data), "docx"
    elif "text/csv" in ct or "tsv" in ct:
        text, kind = data.decode("utf-8", errors="replace"), "csv"
    elif "text/html" in ct or "html" in ct:
        try:
            html = data.decode(resp.encoding or "utf-8", errors="replace")
        except (LookupError, AttributeError):
            html = data.decode("utf-8", errors="replace")
        h = html2text.HTML2Text()
        h.body_width = 0
        text, kind = h.handle(html).strip(), "html"
    elif "text/" in ct:
        text, kind = data.decode("utf-8", errors="replace"), "text"
    else:
        text, kind = "", "unknown"

    return {
        "requested_url": url,
        "fetched_url": fetch_url,
        "content_type": ct,
        "kind": kind,
        "size": len(data),
        "text": text,
        "extracted_chars": len(text),
    }
