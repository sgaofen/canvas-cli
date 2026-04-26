"""`canvas files <course>` — list files in a course (no download yet)."""

from __future__ import annotations

import json as _json
from collections import defaultdict

import typer
from canvasapi.exceptions import CanvasException, Forbidden, ResourceDoesNotExist
from rich.console import Console
from rich.tree import Tree

from ..client import get_user_courses
from ..formatters import files_table, format_relative_time, format_size
from ..matchers import resolve_course

console = Console()


def list_files(
    course: str = typer.Argument(..., help="Course short code (e.g. chem3lc) or course id"),
    flat: bool = typer.Option(False, "--flat", help="Flat table instead of folder tree"),
    json_out: bool = typer.Option(False, "--json", help="Output raw JSON"),
) -> None:
    """List files for a course."""
    courses = get_user_courses(active_only=True)
    target = resolve_course(courses, course)

    try:
        files = list(target.get_files())
    except Forbidden:
        console.print(
            f"[red]Forbidden:[/red] you don't have access to files in '{target.name}'."
        )
        raise typer.Exit(code=1)
    except CanvasException as exc:
        console.print(f"[red]Failed to fetch files:[/red] {exc}")
        raise typer.Exit(code=1)

    try:
        folders = list(target.get_folders())
    except (Forbidden, ResourceDoesNotExist, CanvasException):
        folders = []

    folder_map = {getattr(f, "id", None): f for f in folders}

    if json_out:
        console.print_json(_json.dumps(_files_json(files, folder_map)))
        return

    if not files:
        console.print(f"[yellow]No files in[/yellow] {target.name}")
        return

    course_label = f"{target.name} ({len(files)} files)"

    if flat:
        _render_flat(course_label, files, folder_map)
    else:
        _render_tree(target.name, files, folders, folder_map)


def _render_flat(title: str, files: list, folder_map: dict) -> None:
    table = files_table(title)
    for f in sorted(files, key=lambda x: (_folder_path(x, folder_map), getattr(x, "display_name", ""))):
        table.add_row(
            getattr(f, "display_name", "?") or "?",
            _folder_path(f, folder_map),
            format_size(getattr(f, "size", None)),
            format_relative_time(getattr(f, "updated_at", None)),
        )
    console.print(table)


def _render_tree(course_name: str, files: list, folders: list, folder_map: dict) -> None:
    children_by_parent: dict = defaultdict(list)
    for fld in folders:
        pid = getattr(fld, "parent_folder_id", None)
        children_by_parent[pid].append(fld)

    files_by_folder: dict = defaultdict(list)
    for f in files:
        fid = getattr(f, "folder_id", None)
        files_by_folder[fid].append(f)

    tree = Tree(f"[bold cyan]{course_name}[/bold cyan]")

    def add_contents(node: Tree, folder_id) -> None:
        for child in sorted(children_by_parent[folder_id], key=lambda x: getattr(x, "name", "")):
            sub = node.add(f"[blue]{getattr(child, 'name', '')}/[/blue]")
            add_contents(sub, getattr(child, "id", None))
        for f in sorted(files_by_folder[folder_id], key=lambda x: getattr(x, "display_name", "") or ""):
            size = format_size(getattr(f, "size", None))
            updated = format_relative_time(getattr(f, "updated_at", None))
            node.add(
                f"{getattr(f, 'display_name', '?')} "
                f"[green]({size})[/green] [dim]{updated}[/dim]"
            )

    # Root folders have parent_folder_id = None
    roots = sorted(children_by_parent[None], key=lambda x: getattr(x, "name", ""))
    if roots:
        for root in roots:
            root_node = tree.add(f"[blue]{getattr(root, 'name', '')}/[/blue]")
            add_contents(root_node, getattr(root, "id", None))
    else:
        # Folders unavailable — fall back to flat under course node
        for f in sorted(files, key=lambda x: getattr(x, "display_name", "") or ""):
            size = format_size(getattr(f, "size", None))
            updated = format_relative_time(getattr(f, "updated_at", None))
            tree.add(
                f"{getattr(f, 'display_name', '?')} "
                f"[green]({size})[/green] [dim]{updated}[/dim]"
            )

    # Files whose folder wasn't returned (orphans) get attached at the top
    if folder_map:
        orphan_ids = {fid for fid in files_by_folder if fid not in folder_map and fid is not None}
        for fid in orphan_ids:
            for f in files_by_folder[fid]:
                tree.add(
                    f"[dim](unknown folder)[/dim] {getattr(f, 'display_name', '?')} "
                    f"[green]({format_size(getattr(f, 'size', None))})[/green]"
                )

    console.print(tree)


def _folder_path(file_obj, folder_map: dict) -> str:
    fid = getattr(file_obj, "folder_id", None)
    folder = folder_map.get(fid)
    if folder is None:
        return ""
    return getattr(folder, "full_name", "") or getattr(folder, "name", "") or ""


def _files_json(files: list, folder_map: dict) -> list[dict]:
    return [
        {
            "id": getattr(f, "id", None),
            "name": getattr(f, "display_name", None),
            "filename": getattr(f, "filename", None),
            "folder": _folder_path(f, folder_map),
            "folder_id": getattr(f, "folder_id", None),
            "size": getattr(f, "size", None),
            "updated_at": getattr(f, "updated_at", None),
            "url": getattr(f, "url", None),
        }
        for f in files
    ]
