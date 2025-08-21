import pytest

from mcpstack_jupyter.tools.jupyter.jupyter import Jupyter
from mcpstack_jupyter.tools.jupyter.utils.config_loader import load_env_defaults
from tests.conftest import install_fake_jupyter_server


def action_names(bound_fns):
    return [fn.__name__ for fn in bound_fns]


def test_bind_all_known_tools(known_tools):
    with install_fake_jupyter_server(known_tools) as server:
        tool = Jupyter()
        tool.initialize()  # import & bind
        names = action_names(tool.actions())
        assert sorted(names) == sorted(known_tools)
        for n in known_tools:
            assert hasattr(server, n)


def test_include_subset_only_binds_subset(known_tools):
    subset = known_tools[:3]
    with install_fake_jupyter_server(known_tools):
        tool = Jupyter(include=subset)
        tool.initialize()
        names = action_names(tool.actions())
        assert sorted(names) == sorted(subset)


def test_missing_upstream_tool_raises_attribute_error(known_tools):
    missing = known_tools[-1]
    present = known_tools[:-1]
    with install_fake_jupyter_server(present):
        tool = Jupyter()
        with pytest.raises(AttributeError) as ei:
            tool.initialize()
        assert missing in str(ei.value)


def test_env_mapping_defaults_and_overrides(monkeypatch, known_tools):
    defaults = load_env_defaults()
    with install_fake_jupyter_server(known_tools) as server:
        for k in [
            "PROVIDER",
            "DOCUMENT_URL",
            "DOCUMENT_ID",
            "DOCUMENT_TOKEN",
            "RUNTIME_URL",
            "RUNTIME_ID",
            "RUNTIME_TOKEN",
        ]:
            monkeypatch.delenv(k, raising=False)
        tool = Jupyter()
        tool.initialize()

        assert server.PROVIDER == defaults.get("provider", "jupyter")
        assert server.DOCUMENT_URL == defaults.get(
            "document_url", "http://127.0.0.1:8888"
        )
        assert server.DOCUMENT_ID == defaults.get("document_id", "notebook.ipynb")
        assert server.RUNTIME_URL == defaults.get("runtime_url") or server.DOCUMENT_URL

    with install_fake_jupyter_server(known_tools) as server:
        monkeypatch.setenv("PROVIDER", "custom")
        monkeypatch.setenv("DOCUMENT_URL", "http://10.0.0.1:9999")
        monkeypatch.setenv("DOCUMENT_ID", "foo.ipynb")
        monkeypatch.setenv("DOCUMENT_TOKEN", "DOC1234")
        monkeypatch.setenv("RUNTIME_URL", "http://10.0.0.2:8888")
        monkeypatch.setenv("RUNTIME_ID", "kernel-abc")
        monkeypatch.setenv("RUNTIME_TOKEN", "RUN5678")

        tool = Jupyter()
        tool.initialize()

        assert server.PROVIDER == "custom"
        assert server.DOCUMENT_URL == "http://10.0.0.1:9999"
        assert server.DOCUMENT_ID == "foo.ipynb"
        assert server.DOCUMENT_TOKEN == "DOC1234"
        assert server.RUNTIME_URL == "http://10.0.0.2:8888"
        assert server.RUNTIME_ID == "kernel-abc"
        assert server.RUNTIME_TOKEN == "RUN5678"


def test_to_from_dict_roundtrip():
    src = {"include": ["read_all_cells", "get_notebook_info"]}
    tool = Jupyter.from_dict(src)
    assert tool.to_dict() == src
