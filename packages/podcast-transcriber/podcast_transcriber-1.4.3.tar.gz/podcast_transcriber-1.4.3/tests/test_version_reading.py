import importlib
import re
import sys


def test_version_regex_fallback(monkeypatch):
    # Force tomllib/tomli unhelpful so __init__ falls back to regex path
    monkeypatch.setitem(sys.modules, "tomllib", object())
    monkeypatch.setitem(sys.modules, "tomli", object())

    mod = importlib.import_module("podcast_transcriber.__init__")
    mod = importlib.reload(mod)
    v = getattr(mod, "__version__", "dev")
    # Expect a semantic version string from pyproject.toml via regex fallback
    assert isinstance(v, str) and re.match(r"\d+\.\d+\.\d+", v)
