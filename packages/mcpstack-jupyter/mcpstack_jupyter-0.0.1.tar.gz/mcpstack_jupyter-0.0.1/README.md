<!--suppress HtmlDeprecatedAttribute -->
<div align="center">
  <h1 align="center">
    <br>
    <a href="#"><img src="assets/COVER.png" alt="MCPStack Tool" width="100%"></a>
    <br>
    MCPStack Jupyter MCP
    <br>
  </h1>
  <h4 align="center">Operate Jupyter Notebooks from your favourite LLM</h4>
</div>

<div align="center">

<a href="https://pre-commit.com/">
  <img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-1f6feb?style=for-the-badge&logo=pre-commit">
</a>
<img alt="ruff" src="https://img.shields.io/badge/Ruff-lint%2Fformat-9C27B0?style=for-the-badge&logo=ruff&logoColor=white">
<img alt="python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img alt="pytest coverage" src="https://img.shields.io/badge/Coverage-66%25-brightgreen?style=for-the-badge&logo=pytest">
<img alt="license" src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge">

</div>

> [!IMPORTANT]
> If you haven’t visited the MCPStack main orchestrator repository yet, please start
> there: **[MCPStack](https://github.com/MCP-Pipeline/MCPStack)**

## 💡 About The MCPStack Jupyter Tool

This repository provides an **MCPStack tool that wraps the official Python Jupyter MCP Server** — it is **not** a novel MCP by itself.

- Upstream project: [datalayer/jupyter-mcp-server](https://github.com/datalayer/jupyter-mcp-server)
- We **reuse their MCP actions** and surface them through **MCPStack**.
- As the upstream evolves, **some actions / endpoints may deprecate**. Our wrapper is intentionally lightweight, so updating to new upstream versions should be straightforward.
  If you hit an incompatibility, **please open an issue** and we’ll track an update to align with the Jupyter MCP Server.

### What is MCPStack, in layman’s terms?

The **Model Context Protocol (MCP)** standardises how tools talk to LLMs.
`MCPStack` lets you **stack multiple MCP tools together** into a pipeline and expose them to an LLM host (e.g., Claude Desktop).

Think **scikit-learn pipelines, but for LLM tooling**:
- In scikit-learn: you chain `preprocessors` → `transformers` → `estimators`.
- In MCPStack: you chain multiple MCP tools (Jupyter, MIMIC, …) and the LLM can use all of them during a conversation.

---

## Installation

The tool is distributed as a standard Python package. Thanks to entry points, MCPStack will auto-discover it.

### Via `uv` (recommended)

```bash
uv add mcpstack-jupyter
```

### Via `pip`

```bash
pip install mcpstack-jupyter
```

### (Dev) Pre-commit hooks

```bash
uv run pre-commit install
# or: pre-commit install
```

---

## 🔌 Using With MCPStack

This tool declares entry points so MCPStack can see it automatically:

```toml
[project.entry-points."mcpstack.tools"]
jupyter = "mcpstack_jupyter.tools.jupyter.jupyter:Jupyter"

[project.entry-points."mcpstack.tool_clis"]
jupyter = "mcpstack_jupyter.tools.jupyter.cli:JupyterCLI.get_app"
```

### 1) Run Jupyter with a Token

You **must** run a Jupyter Server/Lab **with a token** (the same token will be used by both the document and runtime APIs).

```bash
uv run jupyter lab \
  --port 8888 \
  --IdentityProvider.token MY_TOKEN \
  --ip 0.0.0.0

# MY_TOKEN can for instance be: 1117bf468693444a5608e882ab3b55d511f354a175a0df02
```

> [!NOTE]
> Docs reference: https://jupyter-mcp-server.datalayer.tech/jupyter/

Make sure to have a notebook open in Jupyter lab, e.g., `notebook.ipynb` or whatever you have defined in the configuration.

### 2) Configure the Jupyter tool (set the token)

Use the tool’s CLI to create a small `MCPStack ToolConfig` JSON. **At minimum pass `--token`**:

```bash
uv run mcpstack tools jupyter configure \
  --token MY_TOKEN \
  --output jupyter_config.json

# MY_TOKEN can for instance be: 1117bf468693444a5608e882ab3b55d511f354a1750df02 (must match the Jupyter server token)
```

The CLI has sensible defaults:

- `DOCUMENT_URL`: `http://127.0.0.1:8888`
- `DOCUMENT_ID`: `notebook.ipynb` <-- Feel free to change this to any of your notebooks.
- `RUNTIME_URL`: defaults to `DOCUMENT_URL`

You can override those if needed:

```bash
uv run mcpstack tools jupyter configure \
  --document-url http://127.0.0.1:8888 \
  --document-id Untitled.ipynb \
  --runtime-url  http://127.0.0.1:8888 \
  --token        1117bf468693444a5608e882ab3b55d511f354a1750df02 \
  --output       jupyter_config.json
```

### 3) Compose a pipeline

Create a new pipeline (or append to an existing one) and include your Jupyter ToolConfig:

```bash
# New pipeline
uv run mcpstack pipeline jupyter --new-pipeline my_pipeline.json --tool-config jupyter_config.json

# Or append to an existing pipeline
uv run mcpstack pipeline jupyter --to-pipeline my_pipeline.json --tool-config jupyter_config.json
```

### 4) Run it inside Claude Desktop (or your host)

```bash
uv run mcpstack build --pipeline my_pipeline.json --config-type claude
```

Now ask the LLM to operate the notebook. A quick smoke test:

> “Append a code cell that prints `Hello World`.”

If everything’s wired correctly, you should see the new cell appear and execute in Jupyter Lab.

---

## ⚙️ Configuration — YAML (Developers)

This tool ships with YAML configs under `src/mcpstack_jupyter/configuration/`:

- `env_defaults.yaml` — defaults for provider/URLs/IDs and a `require_tokens` flag (we keep tokens **required**).
- `tools.yaml` — the list of upstream actions we expose by default. Adjust here as upstream evolves.
- `cli_defaults.yaml` — prompt labels and default output filename for the CLI.

You can tweak those YAML files to change defaults globally without touching code.
Tokens remain **required** and are enforced upfront by MCPStack when building the tool.

---

## 📖 Programmatic API

Use the `Jupyter` tool class directly in a pipeline.
Tokens are taken from the environment (the pipeline config or your process env):

```python
import os
from mcpstack_jupyter.tools.jupyter.jupyter import Jupyter
from MCPStack.stack import MCPStackCore

# Provide tokens via environment (same token for both is fine)
# On the long term we could think passing a StackConfig to the Jupyter tool instance, with all the necessary env vars. Open An Issue.
os.environ["DOCUMENT_TOKEN"] = "1117bf468693444a5608e882ab3b55d511f354a175a0df02"
os.environ["RUNTIME_TOKEN"]  = "1117bf468693444a5608e882ab3b55d511f354a175a0df02"

pipeline = (
    MCPStackCore()
    .with_tool(Jupyter(include=None))  # or provide a subset of actions of interest.
    # Add more tools as needed, e.g., MIMIC, etc.
    # .with_tool(MIMIC(...))
    .build(type="fastmcp", save_path="my_jupyter_pipeline.json")
    .run()
)
```

>[!NOTE]
> Common upstream actions you can expose (see `configuration/tools.yaml`):
>
> - `append_markdown_cell`,
> - `insert_markdown_cell`,
> - `overwrite_cell_source`,
> - `delete_cell`
> - `append_execute_code_cell`,
> - `insert_execute_code_cell`
> - `execute_cell_with_progress`,
> - `execute_cell_simple_timeout`,
> - `execute_cell_streaming`
> - `read_cell`,
> - `read_all_cells`,
> - `get_notebook_info`

---

## 🧰 Troubleshooting

- **403 Forbidden / `_xsrf` missing / cannot create kernels**
  Ensure you ran Jupyter with a token and that your `ToolConfig` provides **both** `DOCUMENT_TOKEN` and `RUNTIME_TOKEN`.
  In most setups it’s the same token.

- **404 on `notebook.ipynb`**
  Update `--document-id` to the actual notebook path relative to Jupyter’s working directory (e.g., `Untitled.ipynb` or `notebooks/analysis.ipynb`).

- **Nothing happens in Lab**
  Prefer `http://127.0.0.1:8888` over `http://localhost:8888`.
  Confirm your pipeline is running and that the tool is listed in `mcpstack list-tools`.

---

## 🤝 Upstream Compatibility & Support

As noted, this is a **lightweight wrapper** over the upstream Jupyter MCP Server
(`github.com/datalayer/jupyter-mcp-server`). If the upstream API changes,
we’ll happily track it — **please open an issue** with details of the version and failing action.

See more in [the official Jupyter MCP Server documentation](https://jupyter-mcp-server.datalayer.tech/).

---

## 🔐 License

MIT — see **[LICENSE](LICENSE)**.
