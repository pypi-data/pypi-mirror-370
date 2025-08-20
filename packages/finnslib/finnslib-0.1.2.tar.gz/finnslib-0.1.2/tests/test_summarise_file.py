from pathlib import Path
from finnslib.summarise import summarise_file

def test_summarise_file_uses_model(fake_openai, tmp_path):
    p = tmp_path / "x.py"
    p.write_text("def add(a,b): return a+b", encoding="utf8")
    fake_openai.set_text("adds two numbers")
    out_path = summarise_file(str(p), apikey=None, level="short", client=fake_openai)
    text = Path(out_path).read_text(encoding="utf8")
    assert "adds two numbers" in text