"""CLI entry point — registers all subcommands."""

from __future__ import annotations

import typer

from .commands import announcements as announcements_cmd
from .commands import assignments as assignments_cmd
from .commands import calendar as calendar_cmd
from .commands import courses as courses_cmd
from .commands import extract as extract_cmd
from .commands import files as files_cmd
from .commands import grades as grades_cmd
from .commands import inbox as inbox_cmd
from .commands import modules as modules_cmd
from .commands import pages as pages_cmd
from .commands import read as read_cmd
from .commands import search as search_cmd
from .commands import syllabus as syllabus_cmd
from .commands import sync as sync_cmd
from .config import init_config

app = typer.Typer(
    help="Canvas CLI for UC Irvine — query courses, files, assignments, grades.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def init() -> None:
    """Set up Canvas API token and config."""
    init_config()


app.command(name="courses")(courses_cmd.list_courses)
app.command(name="files")(files_cmd.list_files)
app.command(name="sync")(sync_cmd.sync)
app.command(name="syllabus")(syllabus_cmd.syllabus)
app.command(name="assignments")(assignments_cmd.assignments)
app.command(name="modules")(modules_cmd.modules)
app.command(name="pages")(pages_cmd.pages)
app.command(name="read")(read_cmd.read)
app.command(name="grades")(grades_cmd.grades)
app.command(name="announcements")(announcements_cmd.announcements)
app.command(name="calendar")(calendar_cmd.calendar)
app.command(name="search")(search_cmd.search)
app.command(name="inbox")(inbox_cmd.inbox)
app.command(name="extract")(extract_cmd.extract)


@app.command()
def mcp() -> None:
    """Start the MCP server (stdio) so Claude Desktop / Code can use canvas tools."""
    from .mcp_server import serve
    serve()
