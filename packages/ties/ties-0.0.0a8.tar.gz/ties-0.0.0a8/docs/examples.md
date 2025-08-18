# Ties Examples

This page provides practical examples of how to use Ties in various scenarios.

## 🚀 Basic Examples

### Example 1: Simple File Sync

Keep a file synchronized between two locations:

```toml
[tool.ties]
[[tool.ties.tie]]
name = "Simple Sync"
source = "README.md"
target = "docs/README.md"
```

### Example 2: Multiple Target Files

Sync one source file to multiple target locations:

```toml
[tool.ties]
[[tool.ties.tie]]
name = "Multi-Target Sync"
source = ".gitignore"
targets = [
    "examples/.gitignore",
    "docs/.gitignore",
    "tests/.gitignore"
]
```

### Example 3: Directory Structure Sync

Sync files while maintaining directory structure:

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

## 🔧 Advanced Examples

### Example 4: Environment Variable Embedding

Create environment-specific configuration files:

```toml
[tool.ties]
[[tool.ties.tie]]
name = "Environment Configs"
source = ".env.template"
targets = [".env.dev", ".env.prod"]
transform = "ties:embed_environ"
```

Template file (`.env.template`):

```bash
# Database Configuration
DB_HOST=${env:DB_HOST}
DB_PORT=${env:DB_PORT}
DB_NAME=${env:DB_NAME}

# API Configuration
API_KEY=${env:API_KEY}
API_URL=${env:API_URL}
```

### Example 5: Documentation Synchronization

Keep documentation in sync across multiple locations:

```toml
[tool.ties]
[[tool.ties.tie]]
name = "Documentation Sync"
source = "README.md"
targets = [
    "docs/README.md",
    "examples/README.md"
]
```

### Example 6: Configuration File Management

Manage multiple configuration files with different transformations:

```toml
[tool.ties]
[[tool.ties.tie]]
name = "Git Ignore to Trivy"
source = ".gitignore"
target = "trivy.yaml"
transform = "transform:trivy_yaml"

[[tool.ties.tie]]
name = "MCP Configuration"
source = ".ties/mcp.json"
targets = [
    ".mcp.json",
    ".cursor/mcp.json",
    ".vscode/mcp.json"
]
transform = "ties:embed_environ"
```

**Note**: The `transform:trivy_yaml` and `transform:vscode_mcp_json` transforms
require a local `transform.py` file in your `.ties/` directory.

## 🏗️ Real-World Scenarios

### Scenario 1: Multi-Environment Application

Keep configuration files synchronized across development, staging, and
production environments:

```toml
[tool.ties]
[[tool.ties.tie]]
name = "App Config Sync"
source = "config/app.toml"
targets = [
    "config/dev/app.toml",
    "config/staging/app.toml",
    "config/prod/app.toml"
]

[[tool.ties.tie]]
name = "Environment Variables"
source = "config/env.template"
targets = [
    "config/dev/.env",
    "config/staging/.env",
    "config/prod/.env"
]
transform = "ties:embed_environ"
```

### Scenario 2: Documentation Project

Maintain consistent documentation across multiple formats and locations:

```toml
[tool.ties]
[[tool.ties.tie]]
name = "Main README"
source = "README.md"
targets = [
    "docs/README.md",
    "examples/README.md",
    "CONTRIBUTING.md"
]

[[tool.ties.tie]]
name = "License Sync"
source = "LICENSE"
targets = [
    "docs/LICENSE.md",
    "examples/LICENSE"
]
```

### Scenario 3: Development Tools Configuration

Keep development tool configurations synchronized:

```toml
[tool.ties]
[[tool.ties.tie]]
name = "Pre-commit Config"
source = ".pre-commit-config.yaml"
targets = [
    "examples/.pre-commit-config.yaml",
    "docs/.pre-commit-config.yaml"
]

[[tool.ties.tie]]
name = "Editor Config"
source = ".editorconfig"
targets = [
    "examples/.editorconfig",
    "docs/.editorconfig"
]
```

## 🔄 Workflow Integration Examples

### Pre-commit Hook

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
        pass_filenames: false
```

### GitHub Actions

Use Ties in your CI/CD pipeline:

```yaml
name: Check File Synchronization
on: [push, pull_request]

jobs:
  sync-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install Ties
        run: pip install ties
      - name: Check file synchronization
        run: ties check
```

### Local Development

Create a development script:

```bash
#!/bin/bash
# dev-sync.sh

echo "Checking file synchronization..."
if ties check; then
    echo "✅ All files are in sync"
else
    echo "❌ Files are out of sync"
    echo "Run 'ties fix' to synchronize files"
    exit 1
fi
```

## 🎯 Best Practices

### 1. Use Descriptive Names

```toml
# Good
name = "Database Configuration Sync"

# Avoid
name = "sync"
```

### 2. Group Related Ties

```toml
[tool.ties]
# Documentation ties
[[tool.ties.tie]]
name = "README Sync"
source = "README.md"
target = "docs/README.md"

[[tool.ties.tie]]
name = "License Sync"
source = "LICENSE"
target = "docs/LICENSE.md"

# Configuration ties
[[tool.ties.tie]]
name = "App Config"
source = "config/app.toml"
targets = ["config/dev/", "config/prod/"]
```

### 3. Use Transformations Wisely

```toml
# Only use transformations when needed
[[tool.ties.tie]]
name = "Simple Copy"
source = "file.txt"
target = "copy.txt"
# No transform needed for simple copying

[[tool.ties.tie]]
name = "Environment Config"
source = ".env.template"
target = ".env"
transform = "ties:embed_environ"
# Transform needed for environment variable substitution
```

## 🚨 Common Pitfalls

### 1. Circular Dependencies

Avoid creating ties that reference each other:

```toml
# ❌ Don't do this
[[tool.ties.tie]]
name = "Circular 1"
source = "file1.txt"
target = "file2.txt"

[[tool.ties.tie]]
name = "Circular 2"
source = "file2.txt"
target = "file1.txt"
```

### 2. Missing Source Files

Ensure source files exist before running Ties:

```bash
# Check if source files exist
ls -la .gitignore config/app.toml

# Then run Ties
ties check
```

### 3. Insufficient Permissions

Ensure you have write permissions to target directories:

```bash
# Check permissions
ls -la target_directory/

# Fix permissions if needed
chmod 755 target_directory/
```

## 🔗 Related Documentation

- [User Guide](user-guide.md) - Complete usage instructions

---

**Need more examples?** Check our
[GitHub repository](https://github.com/AlonKellner/ties) for additional
examples and use cases.
