import os
import pytest
from pathlib import Path
from finnslib.summarise import summarise_file

pytestmark = pytest.mark.integration

def test_real_api_file_summary(openai_client, tmp_path):
    p = tmp_path / "x.py"
    p.write_text("def add(a, b): return a + b", encoding="utf8")
    out_path = summarise_file(str(p), apikey=os.environ["OPENAI_API_KEY"], level="short", client=openai_client)
    text = Path(out_path).read_text(encoding="utf8")
    assert text and isinstance(text, str)