from pathlib import Path
from finnslib.summarise import summarise_repo_tree

def test_tree_with_files_builds_and_summarises(fake_openai, tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "a.ts").write_text("export const a=1", encoding="utf8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "x").write_text("ignored", encoding="utf8")
    (tmp_path / ".gitignore").write_text("skipme.txt\n", encoding="utf8")
    (tmp_path / "skipme.txt").write_text("no", encoding="utf8")

    fake_openai.set_text("short summary")
    out_path = summarise_repo_tree(
        str(tmp_path),
        "tree_with_summaries.txt",
        apikey=None,
        level="short",
        client=fake_openai,
    )
    txt = Path(out_path).read_text(encoding="utf8")

    # keeps ascii tree look
    assert "project structure for:" in txt
    assert "├── " in txt or "└── " in txt

    # shows the folder and the file in tree form
    assert "app/" in txt
    assert "a.ts" in txt

    # includes summaries
    assert "short summary" in txt

    # respects gitignore and git internals
    assert ".git/" not in txt
    assert "skipme.txt" not in txt