# Git Gud

An AI-powered command-line assistant for safer Git usage.

## Overview

Git Gud is designed to make Git usage safer and more intuitive by providing proactive advice and preventing common mistakes. This Phase 1 implementation focuses on building a solid, safe foundation with core CLI functionality, Git interaction capabilities, and comprehensive safety mechanisms.

## Features

- **Safe Git Command Execution**: Execute Git commands with built-in safety checks
- **Dangerous Operation Detection**: Automatically identify potentially destructive Git operations
- **User Confirmation**: Require explicit confirmation before executing dangerous commands
- **Comprehensive Error Handling**: Clear error messages and graceful failure handling
- **Modular Architecture**: Clean separation of concerns for future extensibility

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd git-gud

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Using pip (when published)

```bash
pip install git-gud
```

## Usage

### Basic Command Execution

```bash
# Execute a safe Git command
git-gud --execute "git status"

# Execute a command that requires confirmation
git-gud --execute "git reset --hard HEAD~1"
```

### Command Line Options

- `--execute`, `-e`: Execute a Git command with safety checks

## Safety Features

Git Gud automatically detects and warns about dangerous operations including:

- Force push operations (`git push --force`)
- Hard resets (`git reset --hard`)
- Branch filtering (`git filter-branch`)
- Interactive rebases (`git rebase -i`)
- Force checkouts (`git checkout --force`)
- Forced file deletion (`git clean -fd`)
- Reflog expiration (`git reflog expire`)
- And more...

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=git_gud --cov-report=term-missing

# Format code
black git_gud/

# Type checking
mypy git_gud/
```

### Project Structure

```
git_gud/
├── __init__.py          # Package initialization
├── cli.py              # Command-line interface
├── git_ops.py          # Git command execution
├── safety.py           # Safety checks and confirmations
└── config.py           # Configuration management
```

## Requirements

- Python 3.8+
- Git (must be installed and accessible in PATH)
- typer (for CLI interface)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read the contributing guidelines and submit pull requests for any improvements.

## Roadmap

- **Phase 1** (Current): Core CLI functionality and safety mechanisms
- **Phase 2**: AI-powered natural language to Git command translation
- **Phase 3**: Advanced context awareness and personalized suggestions