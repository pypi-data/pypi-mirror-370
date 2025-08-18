# Ties 🔗

[![PyPI version](https://badge.fury.io/py/ties.svg)](https://badge.fury.io/py/ties)
[![CI Status](https://github.com/AlonKellner/ties/actions/workflows/ci-orchestrator.yml/badge.svg)](https://github.com/AlonKellner/ties/actions/workflows/ci-orchestrator.yml)
[![Docs Status](https://github.com/AlonKellner/ties/actions/workflows/docs.yml/badge.svg)](https://github.com/AlonKellner/ties/actions/workflows/docs.yml)
[![All time downloads](https://static.pepy.tech/badge/ties)](https://pepy.tech/project/ties)
[![Weekly Downloads](https://static.pepy.tech/badge/ties/week)](https://pepy.tech/project/ties)  

[![Python versions](https://img.shields.io/pypi/pyversions/ties.svg)](https://pypi.org/project/ties/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Py Stack: astral.sh](https://img.shields.io/badge/py%20stack-astral.sh-30173d.svg)](https://github.com/astral-sh)
[![Open in Dev Containers](https://img.shields.io/static/v1?label=devcontainer&message=Open&color=blue)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/AlonKellner/ties)
[![Cursor](https://img.shields.io/static/v1?label=-&message=Cursor&color=black)](https://cursor.com/downloads)
[![Claude Code](https://img.shields.io/static/v1?label=-&message=Claude%20Code&color=d77253)](https://www.anthropic.com/claude-code)

A powerful CLI tool to duplicate and sync file content with advanced
transformations. Keep your repository files in sync automatically with
intelligent content synchronization.

## ✨ Features

- **File Synchronization**: Automatically keep multiple files in sync across
  your repository
- **Advanced Transformations**: Apply custom transformations during file copying
- **Pre-commit Integration**: Enforce file consistency as part of your
  development workflow
- **Configuration-Driven**: Simple TOML-based configuration
- **Environment Variable Support**: Embed environment variables in target files
- **Cross-Platform**: Works on Windows, macOS, and Linux

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

## 📖 Documentation

- [User Guide](docs/user-guide.md) - Complete usage instructions
- [Examples](docs/examples.md) - Common use cases and examples

## 🤝 Contributing

We welcome contributions! Please see our
[Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

#### Prerequisites
- [Docker](https://www.docker.com/get-started/)
- [VSCode](https://code.visualstudio.com/download)/[Cursor](https://cursor.com/downloads) (or any IDE with [devcontainer](https://code.visualstudio.com/docs/devcontainers/containers) support)

#### Steps

Either click the badge (VSCode only)  
[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/AlonKellner/ties)  
or (Cursor/VSCode)

1. `git clone https://github.com/AlonKellner/ties.git`
2. Open the repository in your IDE of choice
3. `cmd+shift+p`/`ctrl+shift+p`
4. Type "reopen"
5. Choose "Dev Containers: Reopen in Container"

   This will automatically:
6. Build and start a devcontainer with binary requirements
7. Install the `pre-commit` hooks
8. Use `uv` to install python and all python dependencies into a local `.venv`
9. Install a few MCP servers

   The first time it will fail and prompt you for 3 things:

- Add a [github access token](https://github.com/settings/personal-access-tokens) to ./.devcontainer/.env:

  ```sh
  GITHUB_PERSONAL_ACCESS_TOKEN=<your_personal_access_token_here>
  ```

- [Generate a GPG key and add it to github](https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key)
- [Configure a GPG key as your signing key](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key)

#### MCP

The current MCP servers that this repo supports are:
1. [`github-mcp-server`](https://github.com/github/github-mcp-server) (Remote)
2. [`repomix`](https://github.com/yamadashy/repomix) (Local)
3. [`mcp-language-server`](https://github.com/isaacphi/mcp-language-server)

#### [Claude Code](https://www.anthropic.com/claude-code)

The `pre-commit` setup in this repo uses `claude` code to
automatically review changes.  
By default, `claude` will not be configured and will automatically
pass in the `pre-commit`.  

If you want to use `claude` to review changes, you can read about
[Claude Code Deployment](https://docs.anthropic.com/en/docs/claude-code/third-party-integrations).

## 📝 License

This project is licensed under the MIT License - see the
[LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python tooling (uv, ruff, pytest)
- CI/CD powered by GitHub Actions
- Security scanning with Trivy

## 📊 Project Status

- **Development Status**: Alpha
- **Python Support**: 3.10+
- **License**: MIT
- **Maintainer**: [Alon Kellner](mailto:me@alonkellner.com)

---

## Made with ❤️ by the Ties community
