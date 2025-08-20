# Welcome to ties

A powerful CLI tool to duplicate and sync file content with advanced
transformations. Keep your repository files in sync automatically with
intelligent content synchronization.

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install ties

# Or install with YAML support
pip install ties[yaml]

# Or install from source
git clone https://github.com/AlonKellner/ties.git
cd ties
pip install -e .
```

### Basic Usage

1. **Create a configuration** in your `pyproject.toml`:

    ```toml
    [tool.ties]
    [[tool.ties.tie]]
    name = "gitignore sync"
    source = ".gitignore"
    target = "examples/.gitignore"
    ```

2. **Check for discrepancies**:

    ```bash
    ties check
    ```

3. **Fix discrepancies automatically**:

    ```bash
    ties fix
    ```

## 📖 Advanced docs

- [User Guide](user-guide.md) - Complete usage instructions
- [Examples](examples.md) - Common use cases and examples
