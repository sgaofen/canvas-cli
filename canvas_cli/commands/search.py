"""`canvas search <query>` — search synced filenames or full content (FTS5)."""

from __future__ import annotations

import json as _json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..config import load_config
from ..formatters import format_size
from ..index import index_path, reindex, search_content

console = Console()
err_console = Console(stderr=True)


def search(
    query: str = typer.Argument(..., help="Substring (filenames) or FTS5 query (content)"),
    course: str | None = typer.Option(
        None, "--course", "-c", help="Limit to a course short code (substring match)"
    ),
    content: bool = typer.Option(
        False, "--content", help="Full-text search PDF/DOCX content (uses local FTS5 index)"
    ),
    reindex_first: bool = typer.Option(
        False, "--reindex", help="Force rebuild of the content index before searching"
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """Search synced files by name or content."""
    config = load_config()
    sync_root = Path(config["sync_dir"]).expanduser()
    if not sync_root.exists():
        err_console.print(f"[yellow]Sync dir doesn't exist:[/yellow] {sync_root}")
        err_console.print("Run [cyan]canvas sync[/cyan] first.")
        raise typer.Exit(code=1)

    if content:
        _search_content(sync_root, query, course, reindex_first, json_out)
    else:
        _search_filename(sync_root, query, course, json_out)


def _search_filename(sync_root: Path, query: str, course: str | None, json_out: bool) -> None:
    needle = query.lower()
    course_filter = course.lower() if course else None
    rows = []

    for manifest_path in sorted(sync_root.glob("*/.canvas-manifest.json")):
        course_dir = manifest_path.parent
        try:
            data = _json.loads(manifest_path.read_text())
        except (OSError, ValueError):
            continue
        course_meta = data.get("course", {})
        short = course_meta.get("short_code") or course_dir.name
        if course_filter and course_filter not in short.lower():
            continue
        for file_id, meta in data.get("files", {}).items():
            name = meta.get("name", "")
            path = meta.get("path", "")
            if needle not in name.lower() and needle not in path.lower():
                continue
            rows.append({
                "course": short,
                "file_id": int(file_id),
                "name": name,
                "path": path,
                "abs_path": str(course_dir / path),
                "size": meta.get("size"),
                "updated_at": meta.get("updated_at"),
            })

    if json_out:
        print(_json.dumps(rows))
        return

    if not rows:
        console.print(f"[yellow]No filename matches for[/yellow] '{query}'")
        return

    table = Table(title=f"Filename search '{query}' ({len(rows)})", header_style="bold cyan")
    table.add_column("Course", style="green", no_wrap=True)
    table.add_column("File")
    table.add_column("Folder", style="dim")
    table.add_column("Size", justify="right", style="dim", no_wrap=True)

    for r in rows:
        folder = str(Path(r["path"]).parent) if r["path"] else ""
        table.add_row(r["course"], r["name"], folder, format_size(r["size"]))
    console.print(table)


def _search_content(
    sync_root: Path, query: str, course: str | None, reindex_first: bool, json_out: bool,
) -> None:
    db = index_path(sync_root)
    if reindex_first or not db.exists():
        if not json_out:
            console.print("[dim]Building/refreshing index...[/dim]")
        stats = reindex(sync_root, db, force=reindex_first)
        if not json_out:
            console.print(
                f"[dim]Indexed: +{stats.added} added, "
                f"~{stats.updated} updated, "
                f"-{stats.removed} removed, "
                f"{stats.skipped} unchanged[/dim]"
            )
    else:
        # Auto-incremental: cheap mtime check
        stats = reindex(sync_root, db, force=False)
        if not json_out and stats.total_changed() > 0:
            console.print(f"[dim]Index updated: +{stats.added}, ~{stats.updated}[/dim]")

    hits = search_content(db, query, course=course)

    if json_out:
        print(_json.dumps(hits))
        return

    if not hits:
        console.print(f"[yellow]No content matches for[/yellow] '{query}'")
        return

    console.print(f"[bold cyan]Content search '{query}' — {len(hits)} hits[/bold cyan]\n")
    for h in hits:
        console.print(f"  [green]{h['course']}[/green] · {h['name']} [dim]({h['path']})[/dim]")
        # Render snippet markers as bold
        snip = (h["snippet"] or "").replace("<<", "[bold yellow]").replace(">>", "[/bold yellow]")
        console.print(f"    {snip}\n")
