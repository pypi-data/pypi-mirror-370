<div align="center">
  <h1 align="center">
    <br>
    <a href="#"><img src="assets/COVER.png" alt="MCPStack Tool" width="100%"></a>
    <br>
    MCPStack MIMIC MCP
    <br>
  </h1>
  <h4 align="center">Let Your Favourite LLM Dealing With The SQLs!</h4>
</div>

<div align="center">

<a href="https://pre-commit.com/">
  <img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-1f6feb?style=for-the-badge&logo=pre-commit">
</a>
<img alt="ruff" src="https://img.shields.io/badge/Ruff-lint%2Fformat-9C27B0?style=for-the-badge&logo=ruff&logoColor=white">
<img alt="python" src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img alt="pytest coverage" src="https://img.shields.io/badge/Coverage-65%25-brightgreen?style=for-the-badge&logo=pytest">
<img alt="license" src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge">

</div>

> [!IMPORTANT]
> If you have not been across the MCPStack main orchestrator repository, please start
> there: [View MCPStack](https://github.com/MCP-Pipeline/MCPStack)

## <a id="about-the-project"></a>💡 About The MCPStack MIMIC Tool

`MCPStack MIMIC` is an MCP tool that connects the **MIMIC-IV clinical database** (with either SQLite or BigQuery backends)
into your **MCPStack pipelines**.

In layman's terms:
* MIMIC-IV is a large, de-identified database of ICU patient records, commonly used for healthcare research.
* This tool makes that dataset accessible to an LLM in a controlled way.
* It provides actions like *listing available tables*, *showing table structure with sample data*, and *running queries*; all exposed through MCP so your model can reason with healthcare data securely.

### What is MCPStack, in layman's terms?

The **Model Context Protocol (MCP)** standardises how tools talk to large language models.
`MCPStack` is the orchestrator: it lets you **stack multiple MCP tools together** into a pipeline and then expose them
inside an LLM environment (like Claude Desktop).

Think of it like **scikit-learn pipelines, but for LLMs**:

* In scikit-learn: you chain `preprocessors`, `transformers`, `estimators`.
* In MCPStack: you chain MCP tools (like MIMIC, Jupyter Notebook MCP, etc).


>[!IMPORTANT]
> This MCP has been made possible thanks to the `M3` original work by @rafiattrach, @rajna-fani, @MoreiraP12
> Under Dr. Leo Celi's supervision at MIT Lab for Computational Physiology. Following a first pull request of
> MCPStack to `M3`, we realised that we needed to externalise MCPStack to make it more modular and reusable
> across different use-cases. As such, MCPStack MIMIC is a copy of the original `M3` codebase, with adjustments
> only based on how how MCPStack works, and how it is structured.

---

## Installation

You can install the MIMIC tool as a standalone package. Thanks to `pyproject.toml` entry points, MCPStack
will auto-discover it.

### PyPI Installation Via `UV`

```bash
uv add mcpstack_mimic
```

### PyPI Installation Via `pip`

```bash
pip install mcpstack-mimic
```

### Install pre-commit hooks (optional, for development)

```bash
uv run pre-commit install
# or pip install pre-commit
```

### Run Unit Tests (optional, for development)

```bash
uv run pytest
```

---

## 🔌 Using With MCPStack

The `MIMIC` tool is auto-registered in MCPStack through its entry points:

```toml
[project.entry-points."mcpstack.tools"]
mimic = "mcpstack_mimic.tools.mimic.mimic:MIMIC"
```

That means MCPStack will “see” it without any extra configuration.

### Initialise the database

For SQLite (demo dataset by default):

```bash
uv run mcpstack tools mimic init --dataset mimic-iv-demo
```

This downloads and prepares the dataset locally.

### Configure the tool

Pick a backend (SQLite or BigQuery):

```bash
uv run mcpstack tools mimic configure --backend sqlite --db-path ./mimic.db
```

or

```bash
uv run mcpstack tools mimic configure --backend bigquery --project-id <YOUR_GCP_PROJECT>
```

This generates a `mimic_config.json` you can later feed into pipelines.

### Check status

```python
uv run mcpstack tools mimic status
```

>[!NOTE]
> We favourite `uv` for running MCPStack commands, but you can also use `mcpstack` directly if installed globally
> with `pip install mcpstack`.

---

## 🖇️ Build A Pipeline With MIMIC

Now that the tool is installed and configured, add it to your pipeline:

### Default MIMIC Pipeline (Runs with demo MIMIC dataset)

```bash
uv run mcpstack pipeline mimic --new-pipeline my_pipeline.json
```

### Create a new pipeline and add MIMIC previously custom-configured

```bash
uv run mcpstack pipeline mimic --new-pipeline my_pipeline.json --tool-config mimic_config.json
```

Or append to an existing pipeline

```bash
uv run mcpstack pipeline mimic --to-pipeline existing_pipeline.json --tool-config mimic_config.json
```

### Run it inside Claude Desktop

```bash
uv run mcpstack build --pipeline my_pipeline.json
```

Your LLM can now use the MIMIC tool in conversation, with secure access to the clinical dataset.
Open Claude Desktop, and tada!

---

## 📖 Programmatic API

```python
from mcpstack_mimic.tools.mimic.mimic import MIMIC
from mcpstack_mimic.tools.mimic.backend.backends.sqlite import SQLiteBackend
from mcpstack.stack import MCPStackCore

pipeline = (
    MCPStackCore() #define =config if needed
    .with_tool(MIMIC(
        backends=[
            SQLiteBackend("<path_to_your_mimic.db>")  # SQLite backend with local MIMIC-IV database
        ])
    # Here you can add as many as new `.with_tool(.)` of interest to play with.
    ).build(
        type="fastmcp",
        save_path="my_mimic_pipeline.json",
    ).run()
)
```

>[!IMPORTANT]
> The current repository has (1) technical debts, as in it would benefit from a refactor to make it maybe less messy; for instance, organising the actions into specific files. (2) a lack of documentation, the readme could deserve more in depth exploration of all the possible configurations, explore the code if you are a developer ; it is a little codebase.
> Pull Requests are more than welcome to minimise the tech debts and improve the documentation.

---

## 📽️ Video Demo

<video src="https://github.com/user-attachments/assets/e13c4a56-0fe9-41be-b789-407355fe1f4a" width="320" height="240" controls></video>

🔐 License

MIT — see **[LICENSE](LICENSE)**.
