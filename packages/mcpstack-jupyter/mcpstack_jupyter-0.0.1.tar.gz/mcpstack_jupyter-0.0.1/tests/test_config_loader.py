from mcpstack_jupyter.tools.jupyter.utils.config_loader import (
    load_cli_defaults,
    load_env_defaults,
    load_known_tools,
)


def test_known_tools_and_read_only_lists():
    data = load_known_tools()
    known = data["known_tools"]
    ro = data["read_only"]
    assert isinstance(known, list) and len(known) > 0
    assert "append_markdown_cell" in known
    assert "read_all_cells" in known
    assert set(ro).issubset(set(known))


def test_env_and_cli_defaults_present():
    env = load_env_defaults()
    cli = load_cli_defaults()
    assert "provider" in env
    assert "document_url" in env
    assert "output_filename" in cli
