from lumera.sdk import FileRef, resolve_path, to_filerefs


def test_resolve_path_with_string() -> None:
    p = "/lumera-files/example/data.csv"
    assert resolve_path(p) == p


def test_resolve_path_with_fileref_path() -> None:
    fr: FileRef = {"path": "/lumera-files/sessions/abc/file.txt"}
    assert resolve_path(fr) == "/lumera-files/sessions/abc/file.txt"


def test_resolve_path_with_fileref_run_path() -> None:
    fr: FileRef = {"run_path": "/lumera-files/agent_runs/run1/out.json"}
    assert resolve_path(fr) == "/lumera-files/agent_runs/run1/out.json"


def test_to_filerefs_from_strings() -> None:
    values = [
        "/lumera-files/scopeX/123/a.txt",
        "/lumera-files/scopeX/123/b.txt",
    ]
    out = to_filerefs(values, scope="scopeX", id="123")
    assert len(out) == 2
    assert out[0]["name"] == "a.txt"
    assert out[0]["path"].endswith("/a.txt")
    assert out[0]["object_name"] == "scopeX/123/a.txt"


def test_to_filerefs_from_dicts_merge_defaults() -> None:
    values: list[FileRef] = [
        {"path": "/lumera-files/scopeY/999/c.txt"},
        {"run_path": "/lumera-files/agent_runs/run2/d.txt", "name": "d.txt"},
    ]
    out = to_filerefs(values, scope="scopeY", id="999")
    assert len(out) == 2
    # path-backed
    assert out[0]["name"] == "c.txt"
    assert out[0]["object_name"] == "scopeY/999/c.txt"
    # run_path-backed
    assert out[1]["name"] == "d.txt"
    assert out[1]["path"].endswith("/d.txt")
    assert out[1]["object_name"] == "scopeY/999/d.txt"
