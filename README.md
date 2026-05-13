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

### Submit an assignment
```bash
canvas submit <course> <assignment> --text "my answer here"
canvas submit <course> <assignment> --text-file ~/essay.md
canvas submit <course> <assignment> --url https://example.com/repo
canvas submit <course> <assignment> --file lab3.pdf --file data.csv
canvas submit <course> <assignment> --text "..." --comment "first pass"
canvas submit <course> <assignment> --text "..." --dry-run  # preview only
canvas submit <course> <assignment> --text "..." -y          # skip confirm
```
- `<assignment>` accepts numeric id or name substring (interactive disambiguation on multiple matches)
- Text submissions are Markdown-rendered to HTML by default; use `--no-markdown` to send as preformatted text
- File uploads go through Canvas's two-step upload flow automatically
- The command validates `submission_types` against what the assignment accepts before any API write
- Default prompts for confirmation since submission is irreversible from the student side

### Health check
```bash
canvas ping            # is Canvas reachable + token valid?
canvas ping --json     # structured for agent / script use
```

### Take a quiz from the terminal
```bash
canvas quizzes <course> --open      # list quizzes that still need points
canvas quiz <course> <quiz>         # show metadata (read-only)
canvas quiz <course> <quiz> --take  # interactive: prompt for each question, save, complete
canvas quiz <course> <quiz> --take --answers answers.json
canvas quiz <course> <quiz> --take --dry-run    # don't call complete
canvas quiz <course> <quiz> --take -y           # skip the "complete?" confirm
```
- Falls back to the assignments API when the Quizzes tab is hidden by faculty
- Resumes an existing untaken attempt instead of starting a fresh one (preserves attempt count)
- Supports multiple_choice, true_false, multiple_answers, short_answer, essay
- For other types (numerical, calculated, matching, file_upload) prints a notice — use Canvas web UI
- `--answers` JSON shape: `{"<question_id>": <answer_value>, ...}`. Per question type:

| `question_type` | `<answer_value>` shape | Notes |
|---|---|---|
| `multiple_choice_question` | `<option_id>` (int) | from `qq.answers[i].id` |
| `true_false_question` | `<option_id>` (int) | True/False are just two options |
| `multiple_answers_question` | `[<option_id>, ...]` (list of ints) | checkbox-style |
| `matching_question` | `{"<left_id>": <right_match_id>, ...}` (dict) | canvas-cli converts to `[{answer_id, match_id}, ...]` automatically |
| `short_answer_question` | `"text"` (str) | exact text answer |
| `essay_question` | `"text"` (str) | auto-wrapped in `<p>` if not already HTML |
| `numerical_question` | `"3.14"` (numeric str) | accepts string, int, or float |
| `calculated_question` | `"3.14"` (numeric str) | same as numerical |
| `fill_in_multiple_blanks_question` | `{"<blank_name>": "text", ...}` (dict) | blank names found in question text |
| `multiple_dropdowns_question` | `{"<blank_name>": <option_id>, ...}` (dict) | option ids from `qq.answers` grouped by `blank_id` |
| `file_upload_question` | `<file_id>` or `[<file_id>, ...]` | pre-upload file via Canvas web; only file ids accepted for now |
| `text_only_question` | — | informational; skip entirely |
Distinguishes:
- HTTP 200 + JSON → API reachable, authenticated
- 30x off-domain → Canvas outage (UCI redirects to OIT status page)
- 401 / 403 → Token rejected
- Network error → unreachable

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
