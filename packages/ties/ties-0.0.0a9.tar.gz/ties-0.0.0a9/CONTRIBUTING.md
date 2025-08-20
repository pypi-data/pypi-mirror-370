# Contributing to Ties 🔗

Thank you for your interest in contributing to Ties!
This document provides guidelines and information for contributors.

## 🤝 How to Contribute

There are many ways to contribute to Ties:

- **Report bugs** - Use the [issue tracker](https://github.com/AlonKellner/ties/issues)
- **Suggest features** - Open a feature request issue
- **Improve documentation** - Help make our docs clearer and more comprehensive
- **Submit code** - Fix bugs, add features, or improve existing code
- **Review pull requests** - Help review and test changes
  from other contributors

## 🚀 Development Setup

### Prerequisites
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

   - Build and start a devcontainer with binary requirements
   - Install the `pre-commit` hooks
   - Use `uv` to install python and all python dependencies into a local `.venv`
   - Install a few MCP servers

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

## Tooling

This python (3.13) repo uses the astral.sh stack along other CLIs:
1. `devcontainer` - environment isolation
2. `just` - common commands management
3. `pre-commit` - triggers all of the following CLIs
4. `uv` - venv and CLIs management
5. `ruff` - format and lint
6. `ty` - type checking
7. `pytest` - testing
8. `tox` - tests automation
9. `typos` - spell checking
10. `commitlint` - conventional commits adherence
11. `pip-audit` - dependency security
12. `trivy` - general security
13. `claude` - for an objective AI review
14. `lintok` - file size linter
15. `ties` - file-to-file sync with transformations
16. `yamlfmt` - yaml format and lint
17. `biomejs` - json format and lint
18. `rumdl` - markdown format and lint
19. `lychee` - broken link detection
20. `taplo` - general toml format and lint
21. `pyproject-fmt` - pyproject.toml format and lint
22. `tox-toml-fmt` - tox.toml format and lint

This stack seems overwhelming, but you will never need to dive into
any of it.
This stack managed by `devcontainers`, `pre-commit` and `just`,
thanks to those tools it's easy to setup and easy to use even
without tool specific knowledge.

For daily commands and their uses try:

```bash
just --list
```

### Running Quality Checks

```bash
# This runs everything on the current changes
just pre-commit  # or `just p`

# Run all pre-commit checks on all files
just pre-commit-all  # or `just pa`
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests on all python versions and coverage on latest python
just test  # or `just t`
```

### Test Structure

```text
tests/                      # Tests to run every commit (fast)
├── test_module.py          # Tests for specific module
└── data/                   # Test data files
    ├── sample_config.toml
    └── expected_output.txt
integration-tests/          # Tests to run manually (slow)
├── test_module.py          # Tests for specific module
└── data/                   # Test data files
    ├── sample_config.toml
    └── expected_output.txt

```

## 📚 Documentation

### Documentation Standards

- Write clear, concise documentation
- Include examples for all major features
- Keep documentation up-to-date with code changes
- Use consistent formatting and structure

### Building Documentation

Just push a change in the `docs` folder and open a pull request.

## 🔄 Pull Request Process

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a pull request**
   - Use the PR template
   - Describe your changes clearly
   - Link any related issues
   - Request reviews from maintainers

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## 🐛 Issue Reporting

When reporting issues, please include:

- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Code examples** if applicable

## 📋 Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Other (please describe)

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] All existing tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changes documented in CHANGELOG.md

## Related Issues
Closes #(issue number)
```

## 🏷️ Release Process

1. **Update CHANGELOG.md** with new changes
2. **Create a release tag**

   ```bash
   just bump minor  # or `just b minor`
   ```

3. **GitHub Actions** will automatically build and publish to PyPI

## 🆘 Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Email** - Contact maintainers directly at <me@alonkellner.com>

## 📜 Code of Conduct

Please note that this project is released with a
[Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this
project you agree to abide by its terms.

## 🙏 Recognition

All contributors will be recognized in:
- The project README
- Release notes
- The contributors section on GitHub

Thank you for contributing to Ties! 🎉
