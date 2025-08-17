# Contributing to mcp-pandoc-md2pptx

Thank you for your interest in contributing! Choose your path below:

## 🚀 Quick Start (Simple Changes)

**Fixing docs, typos, or small bugs?**

1. **Fork & clone:** `git clone your-fork-url`
2. **Make your change:** Edit the files you need
3. **Test:** `uv run pytest tests/test_conversions.py` 
4. **Submit PR:** Include screenshots showing it works

That's it! The PR template will guide you through the rest.

**Need to add features or understand the codebase?** Expand the sections below.

---

<details>
<summary>📦 Full Development Setup (expand for new features)</summary>

## Prerequisites

### Required Dependencies
```bash
# Core dependencies (required for all development)
# macOS
brew install pandoc uv

# Ubuntu/Debian  
sudo apt-get install pandoc
pip install uv

# Windows
# Download pandoc from: https://pandoc.org/installing.html
pip install uv
```

## Development Setup

1. **Clone and setup:**
   ```bash
   git clone https://github.com/maekawataiki/mcp-pandoc-md2pptx.git
   cd mcp-pandoc-md2pptx
   uv sync
   ```

2. **Test everything works:**
   ```bash
   uv run pytest tests/test_conversions.py
   uv run mcp-pandoc-md2pptx
   ```

</details>

<details>
<summary>🏗️ Understanding the Codebase (expand to learn architecture)</summary>

## Project Structure

```
/mcp-pandoc-md2pptx/
├── src/mcp_pandoc_md2pptx/
│   ├── __init__.py              # Entry point
│   └── server.py                # Main MCP server implementation
├── tests/
│   ├── fixtures/                # Test input files for all formats
│   ├── output/                  # Test output directory  
│   └── test_conversions.py      # Comprehensive format testing
├── README.md                    # User documentation
├── CHEATSHEET.md               # Quick reference guide
└── pyproject.toml              # Python project configuration
```

## Core Architecture
- **MCP Server**: Implements Model Context Protocol for document conversion
- **Primary Tool**: `convert-contents` handles all format conversions
- **Supported Formats**: md to pptx

## Key Files
- `src/mcp_pandoc_md2pptx/server.py`: Core server implementation with tool definitions
- `tests/test_conversions.py`: Parametrized testing for all format combinations
- `pyproject.toml`: Dependencies and build configuration

</details>

<details>
<summary>⚙️ Development Guidelines (expand for code standards)</summary>

## Code Quality Standards

1. **Follow Existing Patterns**: 
   - Study `src/mcp_pandoc_md2pptx/server.py` for coding style
   - Use async/await patterns for MCP operations
   - Implement comprehensive error handling

2. **Type Hints**: All functions should include proper type annotations

3. **Error Handling**: Provide clear, actionable error messages
   ```python
   # Good
   raise ValueError(f"Output file path is required for {output_format} format")
   
   # Bad  
   raise ValueError("Invalid format")
   ```

4. **JSON Schema Validation**: New parameters must include proper schema definitions

## Testing Requirements

1. **Run Tests**: Always run the full test suite before submitting changes
   ```bash
   uv run pytest tests/test_conversions.py
   ```

2. **Add Tests**: New functionality must include corresponding tests

3. **Test Coverage**: The project uses parametrized testing to verify all format combinations work correctly

4. **Manual Testing**: Test with MCP Inspector if making server changes:
   ```bash
   npx @modelcontextprotocol/inspector uv --directory $(pwd) run mcp-pandoc-md2pptx
   ```

## Documentation Requirements

1. **Update README.md**: Document new features with clear examples
2. **Update CHEATSHEET.md**: Add quick reference examples for new functionality  
3. **Update Tool Descriptions**: Modify docstrings in `server.py` for parameter changes
4. **Version Documentation**: Note any breaking changes or new requirements

</details>

## Getting Help

- **Issues**: Open an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions about usage or development
- **Testing**: Use MCP Inspector for debugging server interactions

## Code of Conduct

This project follows standard open source community guidelines:
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Maintain a professional and welcoming environment

---

Thank you for contributing to mcp-pandoc-md2pptx! Your efforts help make document conversion more accessible for everyone.
