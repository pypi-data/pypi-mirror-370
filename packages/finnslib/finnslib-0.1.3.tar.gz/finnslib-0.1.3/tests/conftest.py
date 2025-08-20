import types
import os
import pytest
from openai import OpenAI

# fake client for unit tests
class _FakeChoice:
    def __init__(self, text: str):
        self.message = types.SimpleNamespace(content=text)

class _FakeResp:
    def __init__(self, text: str):
        self.choices = [_FakeChoice(text)]

class _FakeCompletions:
    def __init__(self, text: str):
        self._text = text
    def create(self, **kwargs):
        return _FakeResp(self._text)

class FakeOpenAI:
    def __init__(self):
        self._text = "fake summary"
        self.chat = types.SimpleNamespace(completions=_FakeCompletions(self._text))
    def set_text(self, text: str):
        self._text = text
        self.chat = types.SimpleNamespace(completions=_FakeCompletions(self._text))

@pytest.fixture
def fake_openai():
    return FakeOpenAI()

# real client for opt in runs
@pytest.fixture
def openai_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("no OPENAI_API_KEY set")
    return OpenAI(api_key=key)