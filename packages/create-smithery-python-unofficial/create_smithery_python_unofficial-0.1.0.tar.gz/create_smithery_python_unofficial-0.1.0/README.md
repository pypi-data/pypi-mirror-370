# create-smithery-python (Unofficial)

> ⚠️ **Note**: This is an unofficial community implementation. For official Smithery tools, please visit [smithery.ai](https://smithery.ai).

Create MCP servers for Smithery using Python and FastMCP.

## Installation

You can run this tool directly with `uvx` (no installation needed):

```bash
uvx create-smithery-python-unofficial my-mcp-server
```

Or install it globally:

```bash
uv pip install create-smithery-python-unofficial
```

The command is still `create-smithery-python` for convenience:

```bash
create-smithery-python my-server
```

## Usage

Create a new MCP server project:

```bash
# With a project name
create-smithery-python my-server

# Interactive mode (will prompt for name)
create-smithery-python
```

This will create a new directory with:
- A working FastMCP server (`main.py`)
- Dockerfile configured for Smithery deployment
- `smithery.yaml` configuration
- Basic project structure

## What's Created

The generated project includes:
- **FastMCP server** with a sample `greet` tool
- **CORS middleware** configured for Smithery
- **Docker support** using the official `uv` Python image
- **Smithery configuration** for container deployment

## Next Steps

After creating your project:

1. Navigate to your project:
   ```bash
   cd my-server
   ```

2. Install dependencies (if you have `uv`):
   ```bash
   uv pip install -r pyproject.toml
   ```

3. Run the server locally:
   ```bash
   python main.py
   ```

4. Deploy to Smithery:
   - Push your code to GitHub
   - Connect your repository at [smithery.ai/new](https://smithery.ai/new)

## Requirements

- Python 3.9+
- `uv` (recommended) or `pip`

## License

MIT
