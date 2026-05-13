"""Canvas API client wrapper (singleton + friendly error handling)."""

from __future__ import annotations

from canvasapi import Canvas
from canvasapi.exceptions import CanvasException, InvalidAccessToken, Unauthorized
from requests.exceptions import JSONDecodeError as _RequestsJSONDecodeError
import typer
from rich.console import Console

from .config import load_config

console = Console()

_canvas: Canvas | None = None


def get_canvas() -> Canvas:
    global _canvas
    if _canvas is None:
        config = load_config()
        _canvas = Canvas(config["base_url"], config["api_token"])
    return _canvas


def get_current_user():
    canvas = get_canvas()
    try:
        return canvas.get_current_user()
    except (InvalidAccessToken, Unauthorized):
        console.print(
            "[red]Authentication failed.[/red] "
            "Token may be invalid or expired. Run [cyan]canvas init[/cyan] to update."
        )
        raise typer.Exit(code=1)
    except _RequestsJSONDecodeError:
        console.print(
            "[red]Canvas API returned non-JSON.[/red] "
            "Server may be down or redirecting to a status page. "
            "Run [cyan]canvas ping[/cyan] to diagnose."
        )
        raise typer.Exit(code=1)
    except CanvasException as exc:
        console.print(f"[red]Canvas API error:[/red] {exc}")
        raise typer.Exit(code=1)


def get_user_courses(active_only: bool = True, include: list[str] | None = None) -> list:
    """Fetch courses for the current user, filtered to those with a real name.

    Canvas can return placeholder/restricted entries with no name; we drop them
    so downstream code can safely assume `course.name` is present.
    """
    user = get_current_user()
    kwargs: dict = {}
    if active_only:
        kwargs["enrollment_state"] = "active"
    if include:
        kwargs["include"] = include
    try:
        courses = list(user.get_courses(**kwargs))
    except _RequestsJSONDecodeError:
        console.print(
            "[red]Canvas API returned non-JSON.[/red] "
            "Run [cyan]canvas ping[/cyan] to diagnose."
        )
        raise typer.Exit(code=1)
    except CanvasException as exc:
        console.print(f"[red]Failed to fetch courses:[/red] {exc}")
        raise typer.Exit(code=1)
    return [c for c in courses if getattr(c, "name", None)]
