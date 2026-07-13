# Squeal IDE

![Squeal IDE banner](squeal_banner.svg)

A lightweight PyQt6 IDE for SQL, built on the Base IDE skeleton.

## Features
- Top menu bar (File, Edit, View, Theme)
- Toolbar
- Left file browser with navigation controls and bookmarks
- Tabbed editor area with line numbers, current-line highlight, and SQL syntax highlighting
  (including correctly-tracked multi-line `/* ... */` block comments)
- Find/Replace dialog (Ctrl+F)
- Console/terminal panel showing query results
- Status bar with cursor position
- Generic open/save workflow with error dialogs on failure
- Window size, splitter layout, and theme persisted across restarts

## Requirements
None — SQL execution uses Python's stdlib `sqlite3` module. No SQLite CLI, no
server, nothing to install.

## Run
```bash
cd "/home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/IDES/IDE_Suite 2/SQUEAL"
./run.sh
```
`run.sh` creates `venv/` and installs requirements automatically (via
`setup.sh`) on first run, then launches the app. Run `./setup.sh` directly
if you just want to (re)provision the environment without launching.

## Build a standalone binary
```bash
source venv/bin/activate
python build.py
```
Produces a self-contained app in `dist/SQUEAL/` via PyInstaller (see
`build.py` and the generated `SQUEAL.spec`). Since SQL execution is pure
Python stdlib (no external process spawned), the built binary needs nothing
else installed to run scripts.

## SQL support
`app/sql_language.py`'s `SqlLanguageProvider`:
- `create_highlighter` — `SqlHighlighter` subclasses the shared
  `BlockCommentHighlighter` (see `app/syntax.py`) for keywords, builtins,
  numbers, `'...'` strings (with `''` escape), `--` line comments, and
  properly multi-line `/* */` block comments.
- `run` — executes the script **in-process** (not via `QProcess`) against a
  fresh in-memory SQLite database: splits on `;`, runs each statement, and
  prints `col | col` headers plus rows for any statement that returns a
  result set. Errors on one statement are reported and execution continues
  with the next.
- No interpreter/backend picker — SQLite only, per design choice.

### Known limitations
- Statement splitting is a naive `;`-split. It breaks on semicolons embedded
  in string literals or multi-statement triggers/procedures. Fine for the
  simple scratch scripts this IDE targets; a real parser would be needed for
  more advanced scripts.
- Each Run starts a **fresh in-memory** database — nothing persists between
  runs. Add a "persist to file" option later if that's ever needed.
- Runs on the GUI thread (no subprocess), so a pathological long-running
  query (e.g. a runaway recursive CTE) will block the UI momentarily. An
  earlier design shelled out to a bundled runner script via `QProcess` using
  `sys.executable` as the interpreter, but `sys.executable` inside a
  PyInstaller-frozen build points at the frozen app itself, not a real
  Python interpreter — that would have broken the built binary. Running
  in-process sidesteps the issue and needs no subprocess machinery, since
  SQLite has no interactivity to support anyway.

## Other extension points
- Expand the file browser with project management features such as new folders, rename, and delete.
- Add a preferences dialog for editor font size, tab width, etc.
- A Postgres backend picker (the local `psql`/server already present on this
  machine) was considered and intentionally left out for now — SQLite-only
  keeps the workflow self-contained and credential-free.

## License
MIT — see [LICENSE](LICENSE).
