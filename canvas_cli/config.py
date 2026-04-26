"""Configuration file management."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import TypedDict

import tomli_w
import typer
from rich.console import Console

console = Console()

CONFIG_DIR = Path.home() / ".config" / "canvas-cli"
CONFIG_PATH = CONFIG_DIR / "config.toml"
DEFAULT_BASE_URL = "https://canvas.eee.uci.edu"
DEFAULT_SYNC_DIR = Path.home() / "CanvasSync"


class Config(TypedDict):
    api_token: str
    base_url: str
    sync_dir: str


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        console.print(
            "[red]No config found.[/red] Run [cyan]canvas init[/cyan] first."
        )
        raise typer.Exit(code=1)

    with CONFIG_PATH.open("rb") as f:
        data = tomllib.load(f)

    required = {"api_token", "base_url", "sync_dir"}
    missing = required - data.keys()
    if missing:
        console.print(
            f"[red]Config missing fields: {', '.join(sorted(missing))}.[/red] "
            "Re-run [cyan]canvas init[/cyan]."
        )
        raise typer.Exit(code=1)

    return data  # type: ignore[return-value]


def save_config(config: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("wb") as f:
        tomli_w.dump(dict(config), f)
    CONFIG_PATH.chmod(0o600)


def init_config() -> None:
    if CONFIG_PATH.exists():
        if not typer.confirm(
            f"Config exists at {CONFIG_PATH}. Overwrite?", default=False
        ):
            raise typer.Exit()

    console.print(
        "\n[bold]Canvas CLI setup[/bold]\n\n"
        "1. Open https://canvas.eee.uci.edu/profile/settings\n"
        "2. Under 'Approved Integrations', click [cyan]+ New Access Token[/cyan]\n"
        "3. Copy the token and paste it below (input is hidden)\n"
    )

    token = typer.prompt("Canvas API token", hide_input=True).strip()
    base_url = typer.prompt("Canvas base URL", default=DEFAULT_BASE_URL).strip().rstrip("/")
    sync_dir_input = typer.prompt("Sync directory", default=str(DEFAULT_SYNC_DIR))
    sync_dir = str(Path(sync_dir_input).expanduser())

    if not token:
        console.print("[red]Token cannot be empty.[/red]")
        raise typer.Exit(code=1)

    save_config({"api_token": token, "base_url": base_url, "sync_dir": sync_dir})

    console.print(f"\n[green]Saved[/green] {CONFIG_PATH} (mode 600)")
    console.print("Verify with: [cyan]canvas courses[/cyan]\n")


def mask_token(token: str) -> str:
    if len(token) <= 8:
        return "***"
    return token[:8] + "..."
