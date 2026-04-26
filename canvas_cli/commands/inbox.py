"""`canvas inbox` — Canvas conversations (messages from instructors / TAs / classmates)."""

from __future__ import annotations

import json as _json

import typer
from canvasapi.exceptions import CanvasException
from rich.console import Console
from rich.table import Table

from ..client import get_canvas
from ..formatters import format_relative_time

console = Console()


def inbox(
    all_msgs: bool = typer.Option(
        False, "--all", help="Include read messages (default: unread only)"
    ),
    limit: int = typer.Option(50, "--limit", help="Max conversations to fetch"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """List Canvas conversations / messages."""
    canvas = get_canvas()
    scope = "inbox" if all_msgs else "unread"

    try:
        convos = []
        for c in canvas.get_conversations(scope=scope):
            convos.append(c)
            if len(convos) >= limit:
                break
    except CanvasException as exc:
        console.print(f"[red]Failed:[/red] {exc}")
        raise typer.Exit(code=1)

    rows = [_convo_dict(c) for c in convos]

    if json_out:
        print(_json.dumps(rows))
        return

    if not rows:
        suffix = "" if all_msgs else " (unread)"
        console.print(f"[green]Inbox empty{suffix}.[/green]")
        return

    table = Table(
        title=f"Inbox ({len(rows)}{' unread' if not all_msgs else ''})",
        header_style="bold cyan",
    )
    table.add_column("Last", style="dim", no_wrap=True)
    table.add_column("From", style="yellow", no_wrap=True)
    table.add_column("Course", style="green", no_wrap=True)
    table.add_column("Subject")
    table.add_column("State", justify="center", no_wrap=True)

    for r in rows:
        sender = ", ".join(r["participants"][:2]) or "—"
        if len(r["participants"]) > 2:
            sender += f" +{len(r['participants']) - 2}"
        state = r["workflow_state"] or "?"
        state_styled = "[red]unread[/red]" if state == "unread" else f"[dim]{state}[/dim]"
        table.add_row(
            format_relative_time(r["last_message_at"]),
            sender,
            r["context_name"] or "—",
            r["subject"] or "(no subject)",
            state_styled,
        )
    console.print(table)


def _convo_dict(c) -> dict:
    participants = []
    for p in getattr(c, "participants", None) or []:
        if isinstance(p, dict):
            name = p.get("name") or p.get("full_name")
        else:
            name = getattr(p, "name", None) or getattr(p, "full_name", None)
        if name:
            participants.append(name)
    return {
        "id": getattr(c, "id", None),
        "subject": getattr(c, "subject", None),
        "last_message": getattr(c, "last_message", None),
        "last_message_at": getattr(c, "last_message_at", None),
        "context_name": getattr(c, "context_name", None),
        "context_code": getattr(c, "context_code", None),
        "participants": participants,
        "workflow_state": getattr(c, "workflow_state", None),
        "message_count": getattr(c, "message_count", None),
    }
