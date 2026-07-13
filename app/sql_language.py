"""SQL LanguageProvider: syntax highlighting and script execution for Squeal IDE.

Execution needs no external process or binary: the script runs in-process
against a fresh in-memory SQLite database via the Python stdlib `sqlite3`
module. (An earlier design shelled out to a bundled runner script via
QProcess with sys.executable as the interpreter — but sys.executable inside
a PyInstaller-frozen build points at the frozen app itself, not a real
Python interpreter, so that approach breaks in built binaries. Running
in-process avoids the problem, and there's no need for QProcess's
async/streaming machinery here anyway since sqlite3 has no interactivity
to support.)
"""

from __future__ import annotations

import re
import sqlite3
from typing import List

from PyQt6.QtGui import QTextDocument

from app.language import LanguageProvider
from app.syntax import BlockCommentHighlighter, HighlightRule, keyword_rule
from app.themes import SyntaxColors

SQL_KEYWORDS = [
    "select", "from", "where", "insert", "into", "values", "update", "set",
    "delete", "create", "table", "drop", "alter", "join", "inner", "left",
    "right", "outer", "on", "group", "by", "order", "having", "limit",
    "offset", "as", "distinct", "union", "all", "and", "or", "not", "null",
    "is", "in", "like", "between", "exists", "case", "when", "then", "else",
    "end", "primary", "key", "foreign", "references", "default", "unique",
    "index", "view", "trigger", "begin", "commit", "rollback", "transaction",
    "asc", "desc", "if",
]

SQL_BUILTINS = [
    "count", "sum", "avg", "min", "max", "abs", "round", "length", "substr",
    "upper", "lower", "coalesce", "ifnull", "cast", "date", "datetime",
]


def _sql_rules() -> List[HighlightRule]:
    return [
        keyword_rule(SQL_KEYWORDS, "keyword"),
        keyword_rule(SQL_BUILTINS, "builtin"),
        HighlightRule(re.compile(r"\b\d+\.?\d*\b"), "number"),
        HighlightRule(re.compile(r"'(?:''|[^'])*'"), "string"),
        HighlightRule(re.compile(r"--.*"), "comment"),
    ]


class SqlHighlighter(BlockCommentHighlighter):
    def __init__(self, document: QTextDocument, syntax_colors: SyntaxColors):
        super().__init__(document, syntax_colors, _sql_rules(), r"/\*", r"\*/")


class SqlLanguageProvider(LanguageProvider):
    """Runs SQL scripts against a fresh in-memory SQLite database.

    Naive statement splitting on ';' — breaks on semicolons embedded in
    string literals or multi-statement triggers, but is sufficient for the
    simple scratch scripts this IDE targets.
    """

    @property
    def name(self) -> str:
        return "SQL"

    @property
    def file_extensions(self) -> List[str]:
        return [".sql"]

    def create_highlighter(self, document: QTextDocument, syntax_colors: SyntaxColors) -> SqlHighlighter:
        return SqlHighlighter(document, syntax_colors)

    def run(self, source: str, terminal) -> None:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        error_count = 0

        for statement in (s.strip() for s in source.split(";")):
            if not statement:
                continue
            try:
                cursor.execute(statement)
            except sqlite3.Error as exc:
                terminal.write(f"Error: {exc}")
                error_count += 1
                continue

            if cursor.description is not None:
                columns = [d[0] for d in cursor.description]
                terminal.write(" | ".join(columns))
                for row in cursor.fetchall():
                    terminal.write(" | ".join(str(v) for v in row))

        conn.commit()
        conn.close()
        terminal.write(f"\n[Done — {error_count} error(s)]" if error_count else "\n[Done]")
