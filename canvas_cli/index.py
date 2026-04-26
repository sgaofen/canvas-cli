"""SQLite FTS5 full-text index over synced course files.

Index lives at `<sync_dir>/.search-index.sqlite` so it travels with the synced
content. Build is incremental: only files whose mtime is newer than the
indexed version are re-extracted.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from .extract import extract_by_filename

INDEX_FILENAME = ".search-index.sqlite"


@dataclass
class IndexStats:
    added: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0
    removed: int = 0

    def total_changed(self) -> int:
        return self.added + self.updated


def _open(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS files USING fts5("
        "  course, name, path, content,"
        "  tokenize='porter unicode61'"
        ")"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS file_meta ("
        "  file_id INTEGER PRIMARY KEY,"
        "  rowid INTEGER NOT NULL,"
        "  course TEXT,"
        "  name TEXT,"
        "  path TEXT,"
        "  abs_path TEXT,"
        "  mtime REAL"
        ")"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_meta_rowid ON file_meta(rowid)")
    return conn


def index_path(sync_root: Path) -> Path:
    return sync_root / INDEX_FILENAME


def reindex(sync_root: Path, db_path: Path | None = None, force: bool = False) -> IndexStats:
    """Walk all course manifests under sync_root and (re)index changed files."""
    db_path = db_path or index_path(sync_root)
    conn = _open(db_path)
    stats = IndexStats()

    # Collect currently-on-disk file ids so we can drop removals at the end
    on_disk: set[int] = set()

    for manifest_path in sorted(sync_root.glob("*/.canvas-manifest.json")):
        course_dir = manifest_path.parent
        try:
            data = json.loads(manifest_path.read_text())
        except (OSError, ValueError):
            continue
        course_short = (data.get("course", {}) or {}).get("short_code") or course_dir.name
        for file_id_str, meta in data.get("files", {}).items():
            try:
                file_id = int(file_id_str)
            except ValueError:
                continue
            local = course_dir / meta.get("path", "")
            if not local.exists():
                continue
            on_disk.add(file_id)
            mtime = local.stat().st_mtime
            existing = conn.execute(
                "SELECT mtime FROM file_meta WHERE file_id = ?", (file_id,)
            ).fetchone()
            if existing and not force and existing[0] >= mtime:
                stats.skipped += 1
                continue
            try:
                content = extract_by_filename(local.name, local.read_bytes())
            except Exception:
                stats.failed += 1
                continue
            if existing:
                # Replace by rowid stored in file_meta
                row = conn.execute(
                    "SELECT rowid FROM file_meta WHERE file_id = ?", (file_id,)
                ).fetchone()
                if row:
                    conn.execute("DELETE FROM files WHERE rowid = ?", (row[0],))
                stats.updated += 1
            else:
                stats.added += 1
            cur = conn.execute(
                "INSERT INTO files (course, name, path, content) VALUES (?,?,?,?)",
                (course_short, local.name, meta.get("path", ""), content),
            )
            new_rowid = cur.lastrowid
            conn.execute(
                "INSERT OR REPLACE INTO file_meta "
                "(file_id, rowid, course, name, path, abs_path, mtime) "
                "VALUES (?,?,?,?,?,?,?)",
                (file_id, new_rowid, course_short, local.name,
                 meta.get("path", ""), str(local), mtime),
            )

    # Drop entries for files that no longer exist on disk
    indexed = {row[0] for row in conn.execute("SELECT file_id FROM file_meta").fetchall()}
    removed = indexed - on_disk
    for fid in removed:
        row = conn.execute("SELECT rowid FROM file_meta WHERE file_id = ?", (fid,)).fetchone()
        if row:
            conn.execute("DELETE FROM files WHERE rowid = ?", (row[0],))
        conn.execute("DELETE FROM file_meta WHERE file_id = ?", (fid,))
        stats.removed += 1

    conn.commit()
    conn.close()
    return stats


def search_content(
    db_path: Path, query: str, course: str | None = None, limit: int = 30,
) -> list[dict]:
    """Run an FTS5 MATCH query against the index. Returns ranked hits with snippets."""
    if not db_path.exists():
        return []
    conn = _open(db_path)
    sql_parts = [
        "SELECT m.file_id, m.course, m.name, m.path, m.abs_path,",
        "       snippet(files, 3, '<<', '>>', '…', 16) AS snip,",
        "       bm25(files) AS rank",
        "FROM files JOIN file_meta m ON files.rowid = m.rowid",
        "WHERE files MATCH ?",
    ]
    params: list = [query]
    if course:
        sql_parts.append("  AND m.course LIKE ?")
        params.append(f"%{course}%")
    sql_parts.append("ORDER BY rank LIMIT ?")
    params.append(limit)
    sql = "\n".join(sql_parts)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [
        {
            "file_id": r[0],
            "course": r[1],
            "name": r[2],
            "path": r[3],
            "abs_path": r[4],
            "snippet": r[5],
            "rank": r[6],
        }
        for r in rows
    ]
