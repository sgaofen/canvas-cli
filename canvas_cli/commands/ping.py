"""`canvas ping` — diagnose Canvas API reachability + auth state."""

from __future__ import annotations

import json as _json

import typer
from rich.console import Console

from ..health import check_api

console = Console()


def ping(
    json_out: bool = typer.Option(False, "--json", help="Emit JSON envelope"),
) -> None:
    """Check Canvas API reachability and token auth."""
    status = check_api()

    if json_out:
        print(_json.dumps(status.to_dict()))
        raise typer.Exit(code=0 if status.reachable else 1)

    console.print(f"\n[bold]Canvas API check[/bold]")
    console.print(f"  base_url:  {status.base_url}")
    console.print(f"  token:     [dim]{status.masked_token}[/dim]")
    console.print(f"  endpoint:  /api/v1/users/self")

    if status.reachable:
        console.print(
            f"  result:    [green]OK[/green] (HTTP {status.status_code}, "
            f"auth as [cyan]{status.user_name}[/cyan] id={status.user_id})"
        )
        raise typer.Exit(code=0)

    code = status.status_code if status.status_code is not None else "—"
    console.print(f"  result:    [red]FAIL[/red] (HTTP {code})")
    if status.final_url:
        console.print(f"  landed on: [dim]{status.final_url}[/dim]")
    if status.content_type:
        console.print(f"  content:   {status.content_type}")
    if status.error:
        console.print(f"\n[yellow]{status.error}[/yellow]")
    raise typer.Exit(code=1)
