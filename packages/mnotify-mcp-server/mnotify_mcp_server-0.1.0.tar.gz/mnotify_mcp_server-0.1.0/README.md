MNotify MCP Server

Production-ready Model Context Protocol (MCP) server exposing MNotify SMS tools for use in MCP-compatible clients (Cursor, Claude, etc.).

### Requirements
- Python 3.10+
- Environment variable: `MNOTIFY_API_KEY`

### Install dependencies (development) with uv or pip
- Using uv (recommended):
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh  # install uv if needed
  uv venv                                          # create .venv
  uv pip install -r requirements.txt               # install deps
  ```
- Using any virtualenv manager + pip:
  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  ```

### Start the server
```bash
export MNOTIFY_API_KEY=sk_mnotify_...

# Preferred (matches Cursor config below once published)
mnotify_mcp server

# Alternatives if needed locally
mnotify-mcp
python -m mnotify_mcp.server
```

### Test quickly with the MCP Inspector
```bash
npx @modelcontextprotocol/inspector@latest
```
- Add server → Process
  - Command: `mnotify_mcp`
  - Args: `server`
  - Ensure `MNOTIFY_API_KEY` is set in the Inspector process environment
- Try tools: `check_sms_balance`, `get_group_list`, then `resolve_group_name({ group_name: "Youth", fetch: true })`.

### Connect to Cursor
- Option A: Project config `.cursor/mcp.json` (recommended)
```json
{
  "mcpServers": {
    "mnotify": {
      "command": "mnotify_mcp",
      "args": ["server"]
    }
  }
}
```
- Option B: Manual add in Cursor (Settings → MCP → Add Custom Server → Process)
  - Command: `mnotify_mcp`
  - Args: `server`
  - Ensure `MNOTIFY_API_KEY` is set in the environment where Cursor launches the process


### Using the server after PyPI install
Once published and installed globally or in a venv:
```bash
pip install mnotify_mcp
export MNOTIFY_API_KEY=sk_mnotify_...
mnotify_mcp server
```
Then connect from Cursor/Claude using the config above (no repo checkout required).

## MNotify Agent (interactive CLI)
Run a local chat agent that can call all MNotify tools directly.

### Setup
- Create a virtual environment and install dependencies with uv or pip (see above).
- Add a `.env` file with:
```env
OPENROUTER_API_KEY=sk-or-v1-...
MNOTIFY_API_KEY=...
AGNO_API_KEY=ag-...   # optional, if required by your agno setup
```

### Start the agent
```bash
python mnotify_agent.py
```

### CLI commands
- help: list commands
- history: show recent messages
- tools: list available tools
- test: run a quick tool-call test
- clear: clear conversation context

Example prompts:
- "Check my SMS balance"
- "Send 'Hello' to group 'Youth' from sender 'CHURCH'"
- "Create a group named Ushers"

### Tools exposed
- SMS: `send_quick_bulk_sms`, `send_bulk_group_sms`, `update_scheduled_sms`
- Reports: `sms_delivery_report`, `specific_sms_delivery_report`, `periodic_sms_delivery_report`
- Contacts: `add_contact`, `update_contact`, `delete_contact`, `get_contact_details`, `get_contact_list`, `get_group_contacts`
- Groups: `add_group`, `update_group`, `delete_group`, `get_group_details`, `get_group_list`
- Templates: `get_template_list`, `get_message_template`, `add_message_template`, `update_message_template`, `delete_message_template`
- Utilities: `register_sender_id`, `check_sender_id`, `check_sms_balance`
- Helpers: `get_context_snapshot`, `resolve_group_name`

### Validation & guardrails
- `message` length ≤ 460; `sender_id` length ≤ 11.
- `schedule=true` requires `schedule_time` (YYYY-MM-DD HH:MM).
- `recipient`/`recipients` and `group_id`/`groups` accept string, list, or comma-separated values.
- Optional: `verify_sender=true` performs a best‑effort sender status check before sending.

### Security
- Never pass secrets as tool arguments. The server reads `MNOTIFY_API_KEY` from the environment.
- The server does not log secrets.

## Preparing for PyPI
Before publishing:
- Project metadata in `pyproject.toml`:
  - Update `[project]` fields: `name`, `version`, `description`, `readme`, `license`, `authors`, `keywords`, `classifiers`, `urls`.
  - Ensure dependency on `mcp>=1.1.1` is present.
  - Ensure console script entry exists:
    ```toml
    [project.scripts]
    mnotify-mcp = "mnotify_mcp.server:main"
    ```
- Package contents:
  - Include `mnotify_mcp` package (has `__init__.py`) and the `functions.py` module used by the server.
    - If using Setuptools, configure `packages` and `py_modules = ["functions"]` (or move `functions.py` under the package and import accordingly).
  - Verify imports work when installed into a clean environment.
- Versioning: bump `__version__` in `mnotify_mcp/__init__.py` and match `pyproject.toml`.
- Build & upload:
  ```bash
  # build
  python -m pip install -U build twine
  python -m build    # or: uv build

  # check the tarball/wheel
  twine check dist/*

  # upload (use testpypi first if desired)
  twine upload dist/*
  # or
  twine upload --repository testpypi dist/*
  ```
- Post‑publish test:
  ```bash
  python -m venv /tmp/v
  /tmp/v/bin/pip install my-agent  # your package name
  MNOTIFY_API_KEY=sk... /tmp/v/bin/mnotify-mcp
  ```

