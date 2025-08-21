import contextlib
import sys
import types
from collections.abc import Iterable

import pytest

from mcpstack_jupyter.tools.jupyter.utils.config_loader import load_known_tools


def _make_fn(name: str):
    def _fn(*args, **kwargs):
        return {"__tool_name__": name}

    _fn.__name__ = name
    return _fn


@contextlib.contextmanager
def install_fake_jupyter_server(tool_names: Iterable[str]):
    pkg_name = "jupyter_mcp_server"
    mod_name = "jupyter_mcp_server.server"

    pkg = types.ModuleType(pkg_name)
    server = types.ModuleType(mod_name)

    server.PROVIDER = None
    server.DOCUMENT_URL = None
    server.DOCUMENT_ID = None
    server.DOCUMENT_TOKEN = None
    server.RUNTIME_URL = None
    server.RUNTIME_ID = None
    server.RUNTIME_TOKEN = None

    for n in tool_names:
        setattr(server, n, _make_fn(n))

    prev_pkg = sys.modules.get(pkg_name)
    prev_mod = sys.modules.get(mod_name)
    sys.modules[pkg_name] = pkg
    sys.modules[mod_name] = server
    try:
        yield server
    finally:
        if prev_pkg is not None:
            sys.modules[pkg_name] = prev_pkg
        else:
            sys.modules.pop(pkg_name, None)
        if prev_mod is not None:
            sys.modules[mod_name] = prev_mod
        else:
            sys.modules.pop(mod_name, None)


@pytest.fixture(scope="session")
def known_tools():
    return load_known_tools()["known_tools"]
