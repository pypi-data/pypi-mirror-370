import re

from mcpstack_jupyter.tools.jupyter.cli import JupyterCLI
from tests.conftest import install_fake_jupyter_server


def test_status_warns_when_tools_missing(known_tools, capsys, monkeypatch):
    present = known_tools[:-1]
    missing = known_tools[-1]
    with install_fake_jupyter_server(present):
        JupyterCLI.status(verbose=False)
        out = capsys.readouterr().out
        assert "Missing upstream tools" in out
        assert missing in out


def test_status_verbose_lists_availability(known_tools, capsys):
    with install_fake_jupyter_server(known_tools):
        JupyterCLI.status(verbose=True)
        out = capsys.readouterr().out
        assert "Upstream Tool Availability" in out
        assert re.search(r"\byes\b", out, re.IGNORECASE)
