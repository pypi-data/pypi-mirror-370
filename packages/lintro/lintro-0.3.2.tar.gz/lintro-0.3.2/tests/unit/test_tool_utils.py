from __future__ import annotations

from lintro.utils.tool_utils import (
    format_as_table,
    should_exclude_path,
    walk_files_with_excludes,
)


def test_should_exclude_path_patterns():
    assert should_exclude_path("a/b/.venv/lib.py", [".venv"]) is True
    assert should_exclude_path("a/b/c.py", ["*.md"]) is False
    assert should_exclude_path("dir/file.md", ["*.md"]) is True


def test_get_table_columns_and_format_tabulate(monkeypatch):
    # Pretend tabulate is available by providing stub function
    rows_captured = {}

    def fake_tabulate(
        tabular_data, headers, tablefmt, stralign=None, disable_numparse=None
    ):
        rows_captured["headers"] = headers
        rows_captured["rows"] = tabular_data
        return "TABLE"

    monkeypatch.setitem(
        __import__("lintro.utils.tool_utils").utils.tool_utils.__dict__,
        "tabulate",
        fake_tabulate,
    )
    monkeypatch.setitem(
        __import__("lintro.utils.tool_utils").utils.tool_utils.__dict__,
        "TABULATE_AVAILABLE",
        True,
    )

    issues = [
        {"file": "a.py", "line": 1, "column": 2, "code": "X", "message": "m"},
        {"file": "b.py", "line": 3, "column": 4, "code": "Y", "message": "n"},
    ]
    table = format_as_table(issues=issues, tool_name="unknown", group_by=None)
    assert table == "TABLE"
    assert rows_captured["headers"]
    assert rows_captured["rows"]


def test_walk_files_with_excludes(tmp_path):
    d = tmp_path / "proj"
    (d / "sub").mkdir(parents=True)
    (d / "sub" / "a.py").write_text("x")
    (d / "sub" / "b.js").write_text("x")
    (d / "sub" / "ignore.txt").write_text("x")
    files = walk_files_with_excludes(
        paths=[str(d)],
        file_patterns=["*.py", "*.js"],
        exclude_patterns=["ignore*"],
        include_venv=False,
    )
    assert any(p.endswith("a.py") for p in files)
    assert any(p.endswith("b.js") for p in files)
    assert not any(p.endswith("ignore.txt") for p in files)
