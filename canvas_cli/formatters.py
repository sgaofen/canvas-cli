"""Shared rich formatting helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from rich.table import Table


def courses_table(title: str = "Courses") -> Table:
    table = Table(title=title, header_style="bold cyan")
    table.add_column("Code", style="green", no_wrap=True)
    table.add_column("Name")
    table.add_column("Term", style="dim")
    table.add_column("ID", style="dim", justify="right")
    table.add_column("Teacher", style="yellow")
    return table


def files_table(title: str) -> Table:
    table = Table(title=title, header_style="bold cyan")
    table.add_column("Name")
    table.add_column("Folder", style="dim")
    table.add_column("Size", style="green", justify="right", no_wrap=True)
    table.add_column("Updated", style="dim", no_wrap=True)
    return table


def format_size(num_bytes: int | None) -> str:
    """Human-readable size: 4.2 KB, 12.5 MB, etc."""
    if num_bytes is None:
        return "—"
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def format_relative_time(iso_ts: str | None) -> str:
    """Convert an ISO 8601 timestamp to '3d ago' / '5h ago' / '2026-04-25'."""
    if not iso_ts:
        return "—"
    try:
        # Canvas returns "2026-04-23T19:34:12Z"
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return iso_ts

    now = datetime.now(timezone.utc)
    delta = now - dt
    secs = delta.total_seconds()

    if secs < 0:
        # Future timestamp — show absolute date
        return dt.strftime("%Y-%m-%d")
    if secs < 60:
        return "just now"
    if secs < 3600:
        return f"{int(secs // 60)}m ago"
    if secs < 86400:
        return f"{int(secs // 3600)}h ago"
    if secs < 86400 * 30:
        return f"{int(secs // 86400)}d ago"
    return dt.strftime("%Y-%m-%d")
