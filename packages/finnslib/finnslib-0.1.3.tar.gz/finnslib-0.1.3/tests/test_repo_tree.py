from pathlib import Path
from finnslib.summarise import summarise_function

def test_summarise_function_focus(fake_openai, tmp_path):
    p = tmp_path / "y.py"
    p.write_text("def foo():\n  pass\n\ndef bar(x):\n  return x*2\n", encoding="utf8")
    fake_openai.set_text("explains bar function")
    out = summarise_function(str(p), "bar", apikey=None, level="medium", client=fake_openai)
    text = Path(out).read_text(encoding="utf8")
    assert "bar" in text.lower() or "explains bar function" in text.lower()