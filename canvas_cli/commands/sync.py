"""`canvas sync` — incremental download of Canvas files into local sync dir.

Plan / download / manifest model:

  1. Build a per-course list of `SyncItem`s (new / update / skip) by comparing
     each file's `updated_at` against the local file mtime.
  2. In `--dry-run`, print the plan and stop.
  3. Otherwise stream-download new/updated files in parallel, atomically
     replacing the destination, and stamp the local mtime to match Canvas.
  4. Write a per-course `.canvas-manifest.json` recording file_id → metadata
     for downstream commands (search, --local lookups, agents).

JSON mode (`--json`) suppresses human-readable output so the result can be
piped to `jq` / consumed by an AI agent.
"""

from __future__ import annotations

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import httpx
import typer
from canvasapi.exceptions import CanvasException, Forbidden
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from ..client import get_user_courses
from ..config import load_config
from ..formatters import format_size
from ..matchers import extract_short_code, resolve_course

console = Console()
err_console = Console(stderr=True)

MANIFEST_FILENAME = ".canvas-manifest.json"

Action = Literal["new", "update", "skip"]


@dataclass
class SyncItem:
    file_id: int
    display_name: str
    rel_path: str
    abs_path: str
    size: int
    updated_at: str | None
    url: str
    action: Action


def sync(
    course: str | None = typer.Argument(
        None, help="Course short code or id; omit to sync all academic courses"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview only, no download"),
    since: str | None = typer.Option(
        None, "--since", help="Only consider files updated on/after YYYY-MM-DD"
    ),
    concurrency: int = typer.Option(5, "--concurrency", "-j", help="Parallel downloads"),
    include_all: bool = typer.Option(
        False,
        "--include-all",
        help="Also sync non-academic courses (Orientation, advising, etc.)",
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
) -> None:
    """Download / update Canvas files into the local sync directory."""
    config = load_config()
    sync_root = Path(config["sync_dir"]).expanduser()

    since_dt: datetime | None = None
    if since:
        try:
            since_dt = datetime.strptime(since, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            _fail(f"Invalid --since date: {since!r} (expected YYYY-MM-DD)", json_out)

    courses = get_user_courses(active_only=True)
    if course:
        targets = [resolve_course(courses, course)]
    elif include_all:
        targets = courses
    else:
        targets = [c for c in courses if extract_short_code(getattr(c, "name", "") or "")]

    if not targets:
        if json_out:
            print(json.dumps({"sync_root": str(sync_root), "courses": []}))
        else:
            console.print("[yellow]No courses to sync.[/yellow]")
        return

    sync_root.mkdir(parents=True, exist_ok=True)

    results = []
    for c in targets:
        result = _sync_one_course(c, sync_root, since_dt, concurrency, dry_run, json_out)
        results.append(result)

    if json_out:
        print(json.dumps({
            "sync_root": str(sync_root),
            "dry_run": dry_run,
            "since": since,
            "courses": results,
        }, default=str))
    else:
        _print_summary(results)


def _sync_one_course(
    course, sync_root: Path, since_dt: datetime | None,
    concurrency: int, dry_run: bool, json_out: bool,
) -> dict:
    name = getattr(course, "name", "") or ""
    short = extract_short_code(name) or _safe_name(name)[:60]
    course_dir = sync_root / short

    if not json_out:
        console.print(f"\n[bold cyan]{short}[/bold cyan] — {name}")

    files, module_only_files, files_status = _gather_files(course)

    if not files and files_status == "forbidden":
        if not json_out:
            console.print("  [yellow]Skipped:[/yellow] no file access (Files + Modules both unavailable)")
        return {
            "course": short, "name": name, "course_id": getattr(course, "id", None),
            "status": "forbidden", "items": [],
        }

    try:
        folders = list(course.get_folders())
    except CanvasException:
        folders = []
    folder_map = {getattr(f, "id", None): f for f in folders}

    items = _build_plan(files, folder_map, course_dir, since_dt, module_only_files)

    new_n = sum(1 for i in items if i.action == "new")
    upd_n = sum(1 for i in items if i.action == "update")
    skp_n = sum(1 for i in items if i.action == "skip")

    if not json_out:
        console.print(
            f"  [green]{new_n} new[/green], "
            f"[yellow]{upd_n} updated[/yellow], "
            f"[dim]{skp_n} unchanged[/dim] / {len(items)} total"
        )

    if dry_run:
        if not json_out:
            for i in items:
                if i.action == "skip":
                    continue
                tag = "[green]+[/green]" if i.action == "new" else "[yellow]~[/yellow]"
                console.print(
                    f"    {tag} {i.rel_path} [dim]({format_size(i.size)})[/dim]"
                )
    else:
        to_download = [i for i in items if i.action != "skip"]
        if to_download:
            _download_items(to_download, concurrency, json_out)
        if items:
            _write_manifest(course_dir, course, items)

    return {
        "course": short,
        "name": name,
        "course_id": getattr(course, "id", None),
        "status": "dry-run" if dry_run else "ok",
        "course_dir": str(course_dir),
        "counts": {"new": new_n, "updated": upd_n, "skipped": skp_n, "total": len(items)},
        "items": [_item_to_dict(i) for i in items] if json_out else [],
    }


def _build_plan(
    files: list, folder_map: dict, course_dir: Path, since_dt: datetime | None,
    module_only_files: dict | None = None,
) -> list[SyncItem]:
    """Build sync plan. `module_only_files` maps file_id → module_name for files
    that came from Modules walk rather than the Files API; they're placed under
    `Modules/<module_name>/` since they have no folder context."""
    module_only_files = module_only_files or {}
    items: list[SyncItem] = []
    for f in files:
        updated_at = getattr(f, "updated_at", None)
        if since_dt and updated_at:
            try:
                ts = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                if ts < since_dt:
                    continue
            except ValueError:
                pass

        fid = getattr(f, "id", 0)
        if fid in module_only_files:
            rel = _module_rel_path(f, module_only_files[fid])
        else:
            rel = _build_rel_path(f, folder_map)
        abs_path = course_dir / rel
        action = _decide_action(abs_path, updated_at)
        items.append(SyncItem(
            file_id=fid,
            display_name=getattr(f, "display_name", "?") or "?",
            rel_path=str(rel),
            abs_path=str(abs_path),
            size=getattr(f, "size", 0) or 0,
            updated_at=updated_at,
            url=getattr(f, "url", "") or "",
            action=action,
        ))
    return items


def _gather_files(course) -> tuple[list, dict[int, str], str]:
    """Combine Files API + Modules walk for File items.

    Returns (files_list, module_only_map, status) where:
      - files_list: deduplicated File objects
      - module_only_map: {file_id: module_name} for files NOT in Files API
      - status: "ok" | "files-only" | "modules-only" | "forbidden"
    """
    files_by_id: dict[int, object] = {}
    module_only: dict[int, str] = {}
    files_ok = False
    modules_ok = False

    # 1. Try Files API
    try:
        for f in course.get_files():
            fid = getattr(f, "id", None)
            if fid is not None:
                files_by_id[fid] = f
        files_ok = True
    except (Forbidden, CanvasException):
        pass

    # 2. Walk Modules for File items not already gathered
    canvas = None
    try:
        for m in course.get_modules():
            modules_ok = True
            try:
                m_items = list(m.get_module_items())
            except CanvasException:
                continue
            for item in m_items:
                if getattr(item, "type", "") != "File":
                    continue
                cid = getattr(item, "content_id", None)
                if cid is None or cid in files_by_id:
                    continue
                if canvas is None:
                    from ..client import get_canvas as _gc
                    canvas = _gc()
                try:
                    f = canvas.get_file(cid)
                except CanvasException:
                    continue
                files_by_id[cid] = f
                module_only[cid] = getattr(m, "name", "?") or "?"
    except (Forbidden, CanvasException):
        pass

    if files_ok and modules_ok:
        status = "ok"
    elif files_ok:
        status = "files-only"
    elif modules_ok:
        status = "modules-only"
    else:
        status = "forbidden"
    return list(files_by_id.values()), module_only, status


def _module_rel_path(file_obj, module_name: str) -> Path:
    """Place Module-only files under `Modules/<module>/<filename>`."""
    name = getattr(file_obj, "display_name", "?") or "?"
    return Path("Modules") / _safe_name(module_name) / _safe_name(name)


def _build_rel_path(file_obj, folder_map: dict) -> Path:
    folder = folder_map.get(getattr(file_obj, "folder_id", None))
    name = getattr(file_obj, "display_name", "?") or "?"
    if folder is None:
        return Path(_safe_name(name))
    full_name = getattr(folder, "full_name", "") or ""
    parts = [p for p in full_name.split("/") if p]
    if parts and parts[0].lower() == "course files":
        parts = parts[1:]
    safe_parts = [_safe_name(p) for p in parts]
    safe_parts.append(_safe_name(name))
    return Path(*safe_parts) if safe_parts else Path(_safe_name(name))


def _safe_name(s: str) -> str:
    cleaned = re.sub(r'[/\\:*?"<>|]+', "_", s).strip().strip(".")
    return cleaned or "_"


def _decide_action(local_path: Path, canvas_updated_at: str | None) -> Action:
    if not local_path.exists():
        return "new"
    if not canvas_updated_at:
        return "skip"
    try:
        canvas_ts = datetime.fromisoformat(
            canvas_updated_at.replace("Z", "+00:00")
        ).timestamp()
    except ValueError:
        return "skip"
    local_ts = local_path.stat().st_mtime
    return "update" if canvas_ts > local_ts + 2 else "skip"


def _download_items(items: list[SyncItem], concurrency: int, json_out: bool) -> None:
    show_progress = not json_out
    with httpx.Client(
        timeout=httpx.Timeout(30.0, read=300.0),
        follow_redirects=True,
    ) as client:
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
                console=console,
                transient=False,
            ) as progress:
                task = progress.add_task("  Downloading", total=len(items))
                _run_pool(client, items, concurrency, progress, task)
        else:
            _run_pool(client, items, concurrency, None, None)


def _run_pool(client, items, concurrency, progress, task) -> None:
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futs = {pool.submit(_download_one, client, i): i for i in items}
        for fut in as_completed(futs):
            item = futs[fut]
            try:
                fut.result()
            except Exception as exc:
                err_console.print(f"  [red]Failed[/red] {item.display_name}: {exc}")
            if progress is not None and task is not None:
                progress.update(task, advance=1)


def _download_one(client: httpx.Client, item: SyncItem) -> None:
    if not item.url:
        raise RuntimeError("no download URL")
    abs_path = Path(item.abs_path)
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = abs_path.with_suffix(abs_path.suffix + ".partial")

    with client.stream("GET", item.url) as resp:
        resp.raise_for_status()
        with open(tmp, "wb") as fh:
            for chunk in resp.iter_bytes(chunk_size=64 * 1024):
                fh.write(chunk)

    tmp.replace(abs_path)

    if item.updated_at:
        try:
            ts = datetime.fromisoformat(item.updated_at.replace("Z", "+00:00")).timestamp()
            os.utime(abs_path, (ts, ts))
        except ValueError:
            pass


def _write_manifest(course_dir: Path, course, items: list[SyncItem]) -> None:
    course_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": 1,
        "synced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "course": {
            "id": getattr(course, "id", None),
            "name": getattr(course, "name", None),
            "short_code": extract_short_code(getattr(course, "name", "") or ""),
        },
        "files": {
            str(item.file_id): {
                "name": item.display_name,
                "path": item.rel_path,
                "size": item.size,
                "updated_at": item.updated_at,
            }
            for item in items
        },
    }
    (course_dir / MANIFEST_FILENAME).write_text(json.dumps(manifest, indent=2))


def _print_summary(results: list[dict]) -> None:
    console.print()
    table = Table(title="Sync summary", header_style="bold cyan")
    table.add_column("Course", style="green")
    table.add_column("Status", justify="center")
    table.add_column("New", justify="right", style="green")
    table.add_column("Updated", justify="right", style="yellow")
    table.add_column("Skipped", justify="right", style="dim")

    status_styled = {
        "ok": "[green]ok[/green]",
        "dry-run": "[cyan]dry-run[/cyan]",
        "forbidden": "[yellow]forbidden[/yellow]",
        "error": "[red]error[/red]",
    }

    for r in results:
        counts = r.get("counts", {"new": 0, "updated": 0, "skipped": 0})
        table.add_row(
            r["course"],
            status_styled.get(r["status"], r["status"]),
            str(counts.get("new", 0)),
            str(counts.get("updated", 0)),
            str(counts.get("skipped", 0)),
        )
    console.print(table)


def _item_to_dict(item: SyncItem) -> dict:
    d = asdict(item)
    d.pop("url", None)  # URL has expiring verifier, don't expose
    return d


def _fail(msg: str, json_out: bool) -> None:
    if json_out:
        print(json.dumps({"error": msg}))
    else:
        console.print(f"[red]{msg}[/red]")
    sys.exit(1)
