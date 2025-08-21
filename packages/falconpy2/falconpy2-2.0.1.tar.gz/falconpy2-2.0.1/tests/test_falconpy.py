\
from falconpy import import_as, install

def test_helper_import(capsys):
    os_mod = import_as("os")
    _ = os_mod.listdir(".")
    out = capsys.readouterr().out
    assert "I'm sorry Dave, I'm afraid I can't do that" in out

def test_install_hook(capsys):
    install("json")
    import json  # noqa: F401
    json.dumps({"a": 1})
    out = capsys.readouterr().out
    assert "I'm sorry Dave, I'm afraid I can't do that" in out
