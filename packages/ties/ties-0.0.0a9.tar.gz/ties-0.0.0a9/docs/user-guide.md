# Ties User Guide

This guide will walk you through using Ties to keep your repository files
synchronized.

## 🎯 What is Ties?

Ties is a command-line tool that automatically keeps files synchronized
across your repository. It's particularly useful for:

- Keeping configuration files in sync across different
  environments
- Maintaining consistent documentation across multiple
  locations
- Automating file synchronization as part of your development workflow
- Applying transformations during file copying (e.g., embedding
  environment variables)

## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install ties
```

### With YAML Support

```bash
pip install ties[yaml]
```

### From Source

```bash
git clone https://github.com/AlonKellner/ties.git
cd ties
pip install -e .
```

## ⚙️ Configuration

Ties uses TOML configuration, typically placed in your `pyproject.toml` file
or a separate `ties.toml` file.

### Basic Configuration

```toml
[tool.ties]
[[tool.ties.tie]]
name = "gitignore sync"
source = ".gitignore"
target = "examples/.gitignore"
```

### Advanced Configuration

```toml
[tool.ties]
[[tool.ties.tie]]
name = "Environment Config"
source = ".ties/config.template"
targets = [".env.local", ".env.production"]
transform = "ties:embed_environ"

[[tool.ties.tie]]
name = "Documentation Sync"
source = "README.md"
target = "docs/README.md"
transform = "transform:markdown_cleanup"
```

## 🔧 Configuration Options

Each tie has the following options:

- **`name`** (required): A descriptive name for the tie
- **`source`** (required): The source file path
- **`target`** or **`targets`**: Single target file or list of target files
- **`transform`**: Optional transformation function to apply

### Available Transforms

- **`ties:embed_environ`**: Embeds environment variables in target files
- **`transform:trivy_yaml`**: Converts gitignore to Trivy YAML format
  (requires local transform.py)
- **`transform:vscode_mcp_json`**: Formats MCP JSON for VS Code
  (requires local transform.py)

## 📖 Usage

### Basic Commands

```bash
# Check for discrepancies without making changes
ties check

# Fix discrepancies automatically
ties fix
```

### Command Options

```bash
# Show help
ties --help

# Check for discrepancies without making changes
ties check

# Fix discrepancies automatically
ties fix
```

## 🔄 Workflow Integration

### Pre-commit Integration

Add Ties to your pre-commit configuration:

```yaml
repos:
  - repo: local
    hooks:
      - id: ties-check
        name: Ties Check
        entry: ties check
        language: system
        types: [python]
```

### CI/CD Integration

Use Ties in your GitHub Actions workflow:

```yaml
- name: Check file synchronization
  run: ties check
```

## 📁 File Patterns

### Source Files

- Can be any file type
- Supports relative and absolute paths
- Can use glob patterns for multiple files

### Target Files

- Can be single file or list of files
- Supports directory creation if needed
- Can use environment variable substitution

## 🔧 Transformations

### Environment Variable Embedding

```toml
[[tool.ties.tie]]
name = "Config with Environment"
source = "config.template"
target = ".env"
transform = "ties:embed_environ"
```

This will replace `${env:ENV_VAR}` placeholders in your template with actual
environment variable values.

### Custom Transformations

You can create custom transformation functions in Python:

```python
def custom_transform(content: str, **kwargs) -> str:
    """Custom transformation function."""
    # Your transformation logic here
    return modified_content
```

## 🚨 Troubleshooting

### Common Issues

1. **Configuration not found**
   - Ensure your `pyproject.toml` has a `[tool.ties]` section
   - Check file paths are correct

2. **Permission errors**
   - Ensure you have write permissions to target directories
   - Check if files are read-only

3. **Transform errors**
   - Verify transform function names are correct
   - Check transform function dependencies

## 📚 Examples

### Example 1: Sync Configuration Files

```toml
[tool.ties]
[[tool.ties.tie]]
name = "Config Sync"
source = "config/default.toml"
targets = [
    "config/development.toml",
    "config/staging.toml",
    "config/production.toml"
]
```

### Example 2: Documentation Synchronization

```toml
[tool.ties]
[[tool.ties.tie]]
name = "Docs Sync"
source = "README.md"
target = "docs/README.md"
```

### Example 3: Environment-Specific Files

```toml
[tool.ties]
[[tool.ties.tie]]
name = "Environment Configs"
source = ".env.template"
targets = [".env.dev", ".env.prod"]
transform = "ties:embed_environ"
```

## 🔗 Next Steps

- Check out [Examples](examples.md) for more use cases

---

**Need help?** Check our [GitHub Issues](https://github.com/AlonKellner/ties/issues).
