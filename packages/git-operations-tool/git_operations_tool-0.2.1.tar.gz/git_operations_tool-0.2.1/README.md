# Git Operations Tool

[![PyPI version](https://badge.fury.io/py/git-operations-tool.svg)](https://badge.fury.io/py/git-operations-tool)
[![Python versions](https://img.shields.io/pypi/pyversions/git-operations-tool.svg)](https://pypi.org/project/git-operations-tool/)
[![License](https://img.shields.io/pypi/l/git-operations-tool.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/yourusername/git-operations-tool/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/git-operations-tool/actions)

A comprehensive Git operations tool with advanced features including:

- **Enhanced Auto commit and push** - Two modes available:
  - 🚀 **Bulk commit**: Commit all changes in one operation
  - 📁 **Individual file commits**: Commit each file separately with configurable delays
- **Smart timing controls** - Prevents rate limiting with configurable delays between commits
- **Advanced safety checks** - Automatically skips sensitive files, large files, and binary files
- **Improved error handling** - Retry mechanisms with exponential backoff
- **Branch management** - Create, list, checkout, and delete branches
- **Pull requests** - GitHub integration for creating pull requests
- **Merge operations** - Safe branch merging
- **Repository status and logs** - Comprehensive Git status and history viewing

## Installation

```bash
pip install git-operations-tool
```

## Usage

After installation, run the tool with:

```bash
git-ops
```

## Features

### 🚀 Enhanced Auto Commit & Push (v0.2.0)
- **Two commit modes**:
  - **Bulk commit**: All changes in one commit (fast, clean history)
  - **Individual commits**: Each file committed separately (detailed tracking)
- **Smart timing**: Configurable delays prevent rate limiting and commit conflicts
- **Safety first**: Automatically excludes sensitive files, large files, and binaries
- **Robust error handling**: Retry mechanisms with exponential backoff

### 🌿 Branch Management
- Create, list, checkout, and delete branches
- Automatic branch switching and creation
- Safe merge operations with conflict detection

### 🔗 GitHub Integration
- Create pull requests directly from the tool
- Repository status and commit history viewing
- Remote synchronization with retry logic

### 🛡️ Safety & Reliability
- Gitignore pattern matching
- Sensitive file detection (.env, keys, credentials)
- Large file size limits (>100MB excluded)
- Binary file detection and exclusion

## Development

To contribute or run from source:

```bash
git clone https://github.com/Idk507/git_operations_tool.git
cd git-operations-tool
pip install -e .
```

## License

MIT License - See [LICENSE](LICENSE) for details.