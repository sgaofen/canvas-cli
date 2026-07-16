"""MCP server exposing canvas-cli commands as native tools.

Lets Claude Desktop / Claude Code call canvas operations directly without
shelling out. Each tool returns a JSON string that the agent can parse.

Run via:  canvas mcp
Wire into Claude Desktop:  ~/Library/Application Support/Claude/claude_desktop_config.json
  {"mcpServers": {"canvas": {"command": "/abs/path/canvas", "args": ["mcp"]}}}
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import __version__
from .client import get_canvas, get_user_courses
from .config import load_config
from .extract import extract_links, extract_pdf, extract_docx, to_markdown
from .index import index_path, reindex, search_content
from .matchers import extract_short_code, resolve_course

mcp = FastMCP("canvas-cli")


def _course_to_dict(c) -> dict:
    name = getattr(c, "name", None)
    return {
        "id": getattr(c, "id", None),
        "code": extract_short_code(name) if name else None,
        "name": name,
        "term": (getattr(c, "term", {}) or {}).get("name") if isinstance(getattr(c, "term", None), dict) else None,
    }


@mcp.tool()
def courses(active_only: bool = True) -> str:
    """List the user's Canvas courses.

    Args:
      active_only: if true (default) only return current-term enrollments.

    Returns: JSON list of {id, code, name, term}.
    """
    cs = get_user_courses(active_only=active_only, include=["term"])
    return json.dumps([_course_to_dict(c) for c in cs])


@mcp.tool()
def files(course: str) -> str:
    """List all files in a course (combines Files API + Modules walk).

    Args:
      course: short code (e.g. 'chem3lc'), course id, or substring of name.
    """
    from canvasapi.exceptions import CanvasException, Forbidden
    cs = get_user_courses(active_only=True)
    target = resolve_course(cs, course)
    rows = []
    try:
        for f in target.get_files():
            rows.append({
                "file_id": f.id,
                "name": getattr(f, "display_name", None),
                "size": getattr(f, "size", None),
                "updated_at": getattr(f, "updated_at", None),
                "folder_id": getattr(f, "folder_id", None),
                "source": "files",
            })
    except (Forbidden, CanvasException):
        pass
    return json.dumps(rows)


@mcp.tool()
def modules(course: str) -> str:
    """List a course's Modules and the items inside each."""
    from canvasapi.exceptions import CanvasException
    cs = get_user_courses(active_only=True)
    target = resolve_course(cs, course)
    out = []
    try:
        for m in target.get_modules():
            try:
                items = list(m.get_module_items())
            except CanvasException:
                items = []
            out.append({
                "module_id": m.id, "name": m.name, "state": getattr(m, "state", None),
                "items": [
                    {
                        "item_id": i.id, "title": getattr(i, "title", None),
                        "type": getattr(i, "type", None),
                        "content_id": getattr(i, "content_id", None),
                        "page_url": getattr(i, "page_url", None),
                        "external_url": getattr(i, "external_url", None),
                        "html_url": getattr(i, "html_url", None),
                    } for i in items
                ],
            })
    except CanvasException as e:
        return json.dumps({"error": str(e)})
    return json.dumps(out)


@mcp.tool()
def pages(course: str) -> str:
    """List Pages in a course (titles + url-slugs)."""
    from canvasapi.exceptions import CanvasException
    cs = get_user_courses(active_only=True)
    target = resolve_course(cs, course)
    try:
        ps = list(target.get_pages())
    except CanvasException:
        return json.dumps([])
    return json.dumps([
        {"title": p.title, "url": getattr(p, "url", None),
         "updated_at": getattr(p, "updated_at", None)}
        for p in ps
    ])


@mcp.tool()
def syllabus(course: str) -> str:
    """Fetch a course's syllabus_body (raw HTML + rendered Markdown)."""
    from canvasapi.exceptions import CanvasException
    cs = get_user_courses(active_only=True)
    target = resolve_course(cs, course)
    canvas_obj = get_canvas()
    try:
        full = canvas_obj.get_course(target.id, include=["syllabus_body"])
    except CanvasException as e:
        return json.dumps({"error": str(e)})
    html = getattr(full, "syllabus_body", "") or ""
    md = to_markdown(html)
    return json.dumps({
        "course": target.name,
        "html": html, "markdown": md,
        "links": extract_links(md),
        "has_content": bool(html.strip()),
    })


@mcp.tool()
def read_file(file_id: int) -> str:
    """Extract text from a Canvas file (PDF / DOCX / TXT). Local-first if synced."""
    from canvasapi.exceptions import CanvasException, ResourceDoesNotExist
    import httpx
    canvas_obj = get_canvas()
    try:
        f = canvas_obj.get_file(file_id)
    except (ResourceDoesNotExist, CanvasException) as e:
        return json.dumps({"error": str(e)})
    name = getattr(f, "display_name", "?") or "?"

    # Try local first
    try:
        cfg = load_config()
        sync_root = Path(cfg["sync_dir"]).expanduser()
        for manifest_path in sync_root.glob("*/.canvas-manifest.json"):
            try:
                data = json.loads(manifest_path.read_text())
            except (OSError, ValueError):
                continue
            meta = data.get("files", {}).get(str(file_id))
            if meta:
                local = manifest_path.parent / meta.get("path", "")
                if local.exists():
                    raw = local.read_bytes()
                    text = _extract_by_name(name, raw)
                    return json.dumps({
                        "source": f"local:{local}", "title": name,
                        "size": len(raw), "text": text,
                        "extracted_chars": len(text),
                        "links": extract_links(text),
                    })
    except Exception:
        # Local cache lookup is best-effort. Any failure here — including the
        # typer.Exit that load_config() raises when no config exists (typer.Exit
        # subclasses RuntimeError, NOT SystemExit) — falls through to the
        # authoritative remote download below.
        pass

    url = getattr(f, "url", "")
    with httpx.Client(timeout=httpx.Timeout(30.0, read=120.0), follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        raw = resp.content
    text = _extract_by_name(name, raw)
    return json.dumps({
        "source": f"canvas:file:{file_id}", "title": name,
        "size": len(raw), "text": text,
        "extracted_chars": len(text), "links": extract_links(text),
    })


@mcp.tool()
def read_page(course: str, page_url: str) -> str:
    """Read a course Page by its url-slug. Use `pages(course)` to discover slugs."""
    from canvasapi.exceptions import CanvasException, ResourceDoesNotExist
    cs = get_user_courses(active_only=True)
    target = resolve_course(cs, course)
    try:
        p = target.get_page(page_url)
    except (ResourceDoesNotExist, CanvasException) as e:
        return json.dumps({"error": str(e)})
    html = getattr(p, "body", "") or ""
    md = to_markdown(html)
    return json.dumps({
        "title": p.title, "url": page_url,
        "text": md, "extracted_chars": len(md),
        "links": extract_links(md),
    })


@mcp.tool()
def read_url(url: str) -> str:
    """Fetch any external URL (Google Docs, public PDF, HTML) and extract text.

    Google Docs /edit URLs are auto-rewritten to /export endpoints.
    """
    import re
    import httpx
    gdocs = re.match(
        r"^(https://docs\.google\.com/(document|spreadsheets|presentation)/d/[^/]+)(/(edit|view|preview)?)?(\?.*)?$",
        url,
    )
    fetch_url = url
    if gdocs:
        fmt = {"document": "txt", "spreadsheets": "csv", "presentation": "txt"}[gdocs.group(2)]
        fetch_url = f"{gdocs.group(1)}/export?format={fmt}"
    try:
        with httpx.Client(
            timeout=httpx.Timeout(20.0, read=60.0), follow_redirects=True,
            headers={"User-Agent": f"canvas-cli-mcp/{__version__}"},
        ) as client:
            resp = client.get(fetch_url)
            resp.raise_for_status()
            raw = resp.content
            ct = resp.headers.get("content-type", "").lower()
    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}", "url": fetch_url})
    except httpx.HTTPError as e:
        return json.dumps({"error": str(e), "url": fetch_url})

    lower = fetch_url.lower()
    if "application/pdf" in ct or lower.endswith(".pdf"):
        text, kind = extract_pdf(raw), "pdf"
    elif "officedocument.wordprocessingml" in ct or lower.endswith(".docx"):
        text, kind = extract_docx(raw), "docx"
    elif "text/csv" in ct or "tsv" in ct:
        text, kind = raw.decode("utf-8", errors="replace"), "csv"
    elif "html" in ct:
        text, kind = to_markdown(raw.decode("utf-8", errors="replace")), "html"
    else:
        text, kind = raw.decode("utf-8", errors="replace") if "text/" in ct else "", "text"
    return json.dumps({
        "url": fetch_url, "requested_url": url,
        "content_type": ct, "kind": kind,
        "size": len(raw), "text": text,
        "extracted_chars": len(text), "links": extract_links(text),
    })


@mcp.tool()
def assignments(course: str | None = None, upcoming_days: int = 14) -> str:
    """List assignments. With course=None, returns upcoming across all academic courses."""
    from canvasapi.exceptions import CanvasException
    cs = get_user_courses(active_only=True)
    if course:
        targets = [resolve_course(cs, course)]
    else:
        targets = [c for c in cs if extract_short_code(getattr(c, "name", "") or "")]
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=upcoming_days)
    rows = []
    for c in targets:
        try:
            for a in c.get_assignments(include=["submission"]):
                due_str = getattr(a, "due_at", None)
                due = None
                if due_str:
                    try:
                        due = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
                    except ValueError:
                        pass
                if not course and (not due or due < now or due > cutoff):
                    continue
                sub = getattr(a, "submission", None) or {}
                if not isinstance(sub, dict):
                    sub = {}
                rows.append({
                    "course": extract_short_code(c.name) or c.name,
                    "assignment_id": a.id,
                    "name": getattr(a, "name", None),
                    "due_at": due_str,
                    "points_possible": getattr(a, "points_possible", None),
                    "submission_state": sub.get("workflow_state"),
                    "score": sub.get("score"),
                    "html_url": getattr(a, "html_url", None),
                })
        except CanvasException:
            continue
    return json.dumps(rows)


@mcp.tool()
def grades(course: str | None = None) -> str:
    """Course totals (no arg) or per-assignment grades for one course."""
    from canvasapi.exceptions import CanvasException
    if course:
        cs = get_user_courses(active_only=True)
        target = resolve_course(cs, course)
        try:
            assigns = list(target.get_assignments(include=["submission"]))
        except CanvasException as e:
            return json.dumps({"error": str(e)})
        return json.dumps([
            {
                "name": getattr(a, "name", None),
                "points_possible": getattr(a, "points_possible", None),
                "score": (a.submission or {}).get("score") if isinstance(getattr(a, "submission", None), dict) else None,
                "grade": (a.submission or {}).get("grade") if isinstance(getattr(a, "submission", None), dict) else None,
                "submission_state": (a.submission or {}).get("workflow_state") if isinstance(getattr(a, "submission", None), dict) else None,
                "due_at": getattr(a, "due_at", None),
            } for a in assigns
        ])
    else:
        cs = get_user_courses(active_only=True, include=["total_scores"])
        out = []
        for c in cs:
            if not extract_short_code(getattr(c, "name", "") or ""):
                continue
            es = getattr(c, "enrollments", None) or []
            e = es[0] if es and isinstance(es, list) and isinstance(es[0], dict) else {}
            out.append({
                "course": extract_short_code(c.name) or c.name,
                "current_score": e.get("computed_current_score"),
                "current_grade": e.get("computed_current_grade"),
                "final_score": e.get("computed_final_score"),
            })
        return json.dumps(out)


@mcp.tool()
def announcements(days: int = 7, course: str | None = None) -> str:
    """Recent announcements (last N days) across all academic courses or one."""
    from canvasapi.exceptions import CanvasException
    cs = get_user_courses(active_only=True)
    if course:
        targets = [resolve_course(cs, course)]
    else:
        targets = [c for c in cs if extract_short_code(getattr(c, "name", "") or "")]
    canvas_obj = get_canvas()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    try:
        anns = list(canvas_obj.get_announcements(
            context_codes=[f"course_{t.id}" for t in targets],
            start_date=cutoff.date().isoformat(),
        ))
    except CanvasException as e:
        return json.dumps({"error": str(e)})
    course_by_id = {t.id: t for t in targets}
    out = []
    for a in anns:
        ctx = getattr(a, "context_code", "")
        cid = int(ctx.replace("course_", "")) if ctx.startswith("course_") else None
        c = course_by_id.get(cid)
        out.append({
            "course": extract_short_code(getattr(c, "name", "") or "") if c else "?",
            "title": a.title,
            "posted_at": getattr(a, "posted_at", None) or getattr(a, "created_at", None),
            "url": getattr(a, "html_url", None),
            "body": to_markdown(getattr(a, "message", "") or ""),
        })
    return json.dumps(out)


@mcp.tool()
def calendar(days: int = 14) -> str:
    """Upcoming due dates across all academic courses."""
    return assignments(course=None, upcoming_days=days)


@mcp.tool()
def search(query: str, content: bool = False, course: str | None = None) -> str:
    """Search synced files. `content=True` does FTS5 over PDF/DOCX text."""
    cfg = load_config()
    sync_root = Path(cfg["sync_dir"]).expanduser()
    if not sync_root.exists():
        return json.dumps({"error": "sync directory does not exist; run `canvas sync` first"})

    if content:
        db = index_path(sync_root)
        reindex(sync_root, db, force=False)  # incremental
        return json.dumps(search_content(db, query, course=course))

    needle = query.lower()
    rows = []
    for manifest_path in sorted(sync_root.glob("*/.canvas-manifest.json")):
        try:
            data = json.loads(manifest_path.read_text())
        except (OSError, ValueError):
            continue
        short = (data.get("course", {}) or {}).get("short_code") or manifest_path.parent.name
        if course and course.lower() not in short.lower():
            continue
        for fid, meta in data.get("files", {}).items():
            if needle in meta.get("name", "").lower() or needle in meta.get("path", "").lower():
                rows.append({
                    "course": short, "file_id": int(fid),
                    "name": meta.get("name"), "path": meta.get("path"),
                    "size": meta.get("size"),
                })
    return json.dumps(rows)


@mcp.tool()
def inbox(unread_only: bool = True, limit: int = 30) -> str:
    """List Canvas conversations / private messages."""
    from canvasapi.exceptions import CanvasException
    canvas_obj = get_canvas()
    scope = "unread" if unread_only else "inbox"
    try:
        convos = []
        for c in canvas_obj.get_conversations(scope=scope):
            convos.append(c)
            if len(convos) >= limit:
                break
    except CanvasException as e:
        return json.dumps({"error": str(e)})
    return json.dumps([
        {
            "id": c.id, "subject": getattr(c, "subject", None),
            "last_message": getattr(c, "last_message", None),
            "last_message_at": getattr(c, "last_message_at", None),
            "context_name": getattr(c, "context_name", None),
            "workflow_state": getattr(c, "workflow_state", None),
            "participants": [p.get("name") for p in (getattr(c, "participants", None) or []) if isinstance(p, dict)],
        } for c in convos
    ])


@mcp.tool()
def extract_course(course: str, follow_links: bool = False) -> str:
    """Build a comprehensive knowledge base for one course (syllabus + pages +
    modules + files + assignments + announcements). With `follow_links=True`,
    also fetches every external URL referenced. May be large.
    """
    from .commands.extract import (
        _fetch_syllabus, _fetch_all_pages, _fetch_all_modules,
        _list_files as _ext_list_files, _list_assignments as _ext_list_assignments,
        _list_announcements as _ext_list_announcements, _fetch_external,
    )
    cs = get_user_courses(active_only=True)
    target = resolve_course(cs, course)
    short = extract_short_code(getattr(target, "name", "") or "") or "?"

    bundle = {
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "course": {"id": target.id, "name": target.name, "short_code": short},
        "syllabus": _fetch_syllabus(target, True),
        "pages": _fetch_all_pages(target, True),
        "modules": _fetch_all_modules(target, True),
        "files": _ext_list_files(target, True),
        "assignments": _ext_list_assignments(target, True),
        "announcements": _ext_list_announcements(target, True),
    }
    urls = set()
    if bundle["syllabus"] and bundle["syllabus"].get("markdown"):
        urls.update(extract_links(bundle["syllabus"]["markdown"]))
    for p in bundle["pages"]:
        urls.update(extract_links(p.get("markdown", "")))
    for m in bundle["modules"]:
        for it in m.get("items", []):
            if it.get("type") == "ExternalUrl" and it.get("external_url"):
                urls.add(it["external_url"])
    external = sorted(
        u for u in urls if not any(x in u for x in [
            "canvas.eee.uci.edu/courses/", "mailto:", "fonts.googleapis",
        ])
    )
    bundle["external_urls"] = external
    if follow_links:
        bundle["external_content"] = [_fetch_external(u) for u in external]
    return json.dumps(bundle, default=str)


def _extract_by_name(name: str, raw: bytes) -> str:
    lower = name.lower()
    if lower.endswith(".pdf"):
        return extract_pdf(raw)
    if lower.endswith(".docx"):
        return extract_docx(raw)
    if lower.endswith((".html", ".htm")):
        return to_markdown(raw.decode("utf-8", errors="replace"))
    if lower.endswith((".txt", ".md", ".csv", ".json", ".log")):
        return raw.decode("utf-8", errors="replace")
    return ""


def serve() -> None:
    """Start the MCP stdio server."""
    mcp.run("stdio")
