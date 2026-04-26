# canvas-cli

Command-line tool for UC Irvine Canvas (`canvas.eee.uci.edu`).

Built primarily for **AI agent consumption** — every command supports `--json`
for piping, structured output for tools like `jq`, and stable exit codes.
Doubles as a fast human CLI: rich tables, fuzzy course matching, local sync.

## Install

```bash
cd canvas-cli
uv venv --python 3.11
uv pip install -e .
```

## First-time setup

```bash
canvas init
```

Generate a token at <https://canvas.eee.uci.edu/profile/settings> →
**+ New Access Token**. Stored at `~/.config/canvas-cli/config.toml`
(mode `0600`).

## Commands

### Discovery
```bash
canvas courses                       # active enrollments
canvas courses --all --json          # include past, JSON output
canvas courses --term "Spring 2026"
```

### Course materials
```bash
canvas files <course>                # tree view, fuzzy course match
canvas files chem3lc --flat --json   # flat list, agent-friendly JSON
canvas modules <course>              # course Modules + items (use when Files locked)
canvas modules <course> --next       # next un-completed item
canvas pages <course>                # course Pages (wiki-style)
canvas pages <course> <url-slug>     # read one Page body as Markdown
canvas syllabus <course>             # syllabus_body → rendered Markdown
canvas syllabus <course> --raw       # raw HTML
```

### Local sync
```bash
canvas sync                          # all academic courses → ~/CanvasSync/
canvas sync chem2c                   # one course
canvas sync --dry-run                # preview, no download
canvas sync --since 2026-04-01       # only files updated since
canvas sync --include-all            # also sync Orientation/SHAPE
canvas sync --json                   # structured plan + result
```

### Read content (for AI agents)
```bash
canvas read --file 35537575          # extract text: PDF (pypdf), DOCX (python-docx)
canvas read --page chem2c syllabus   # fetch Page body as Markdown
canvas read --assignment 1822857 --from-course physics7c
canvas read --file <id> --json       # envelope: {source, title, text, ...}
```
Local-first: if the file is in `~/CanvasSync/`, reads from disk; otherwise downloads.

### Tracking
```bash
canvas assignments                   # upcoming 14d across all courses
canvas assignments chem2c --all
canvas assignments --overdue
canvas assignments --submitted
canvas grades                        # course totals + letter grades
canvas grades physics7c              # per-assignment scores
canvas calendar --days 14            # upcoming due dates
canvas calendar --ical -o ~/canvas.ics  # export to iCalendar
canvas announcements --days 7        # recent across all courses
canvas announcements chem3lc --full  # include body text
```

### Search (offline, post-sync)
```bash
canvas search "midterm"                   # filename match across synced courses
canvas search "week" -c physics7lc        # restrict to one course
canvas search "kinetics" --content        # FTS5 search of PDF/DOCX text
canvas search '"second order"' --content  # phrase query
canvas search "newton" --content --reindex  # force-rebuild index first
canvas search "X" --json
```
The content index lives at `<sync_dir>/.search-index.sqlite` (FTS5, BM25
ranking). It refreshes incrementally — only files whose mtime is newer than
the last index pass get re-extracted.

### Inbox
```bash
canvas inbox                         # unread Canvas messages
canvas inbox --all --limit 20
canvas inbox --json
```

### Extract — full course knowledge base in one shot
```bash
canvas extract chem3lc                  # syllabus + pages + modules + files + assignments + announcements
canvas extract physics7c --save         # also write to ~/CanvasSync/<course>/.extract.json
canvas extract chem3lc --follow-links   # also fetch every external URL (Google Docs etc.)
canvas extract chem3lc --json
```
Designed for AI agents that want a single dump of "everything about this
course" without 8 separate API calls.

### What-if grade calculator
```bash
canvas grades physics7c --what-if --assume-all 90       # if I get 90% on all remaining
canvas grades chem3lc --what-if --score "Final Exam=85" --score "Quiz 5=23"
```
Uses Canvas's assignment-group weights for the projection.

### MCP server (Claude Desktop / Code integration)
```bash
canvas mcp     # starts MCP stdio server
```
Wire into Claude Desktop at `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "canvas": {
      "command": "/Users/stephenyu/Applications/untitled folder/canvas-cli/.venv/bin/canvas",
      "args": ["mcp"]
    }
  }
}
```
Exposes 15 tools: `courses`, `files`, `modules`, `pages`, `syllabus`,
`read_file`, `read_page`, `read_url`, `assignments`, `grades`,
`announcements`, `calendar`, `search`, `inbox`, `extract_course`.

### Read external content (Google Docs, public PDFs, etc.)
```bash
canvas read --url "https://docs.google.com/document/d/.../pub"
canvas read --url "https://docs.google.com/spreadsheets/d/X/edit?usp=sharing"
# /edit URLs auto-rewrite to /export?format=txt|csv
canvas read --url "https://example.com/syllabus.pdf"
```
Every `canvas read` JSON envelope includes a `links` field with all
`http(s)://` URLs found in the extracted text — so an agent can chain
fetches (Page → Google Doc → embedded PDF) without parsing markdown itself.

## Course matching

`<course>` accepts:
- short code: `chem3lc`, `physics7c`, `unistu87`
- short code with M-prefix: `chemm3lc` works for `CHEM M3LC`
- course id: `82901`
- substring of name: `chem`, `physics` (prompts to disambiguate)

## Layout after `canvas sync`

```
~/CanvasSync/
├── CHEM M2C/
│   ├── .canvas-manifest.json     # file_id → metadata
│   ├── Discussion Questions/
│   ├── Exams/Midterm 1/
│   └── Lectures/
├── PHYSICS 7LC/
│   └── ...
└── manifest.json                 # global (TBD)
```

Incremental: re-running `canvas sync` only re-downloads files whose Canvas
`updated_at` is newer than local mtime. Local mtimes are stamped to match
Canvas, so the comparison is stable.

## Why so many commands?

The Canvas API surfaces course materials through several different tabs
(Files, Modules, Pages, Syllabus, Assignments). Different professors use
different tabs:

- **CHEM M2C** (Mandelshtam): Files + syllabus_body + Announcements (Discussion PDFs)
- **CHEM M3LC** (Ardo): syllabus_body + Modules (Files locked)
- **PHYSICS 7C** (Xin): Modules only (Files locked, syllabus is a Google Doc link)
- **PHYSICS 7LC** (Tavakol): Files + syllabus_body

For an AI agent to autonomously find course materials, it needs to fall
through all these tabs. The CLI provides one entry point per tab, plus
`canvas read` to extract content from anything addressable.

## Known limits

- `canvas search --content` (FTS5 over PDF text) not yet implemented
- No MCP server wrapper yet (planned)
- `canvas sync` doesn't yet sync Module-only files (e.g. PHYSICS 7C has 80+
  files visible via `canvas modules` that aren't picked up by `canvas sync`)

See [SPEC.md](./SPEC.md) for the original design.
