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

### Prerequisites

- Python 3.8 or higher
- Git (must be installed and accessible in PATH)
- OpenRouter API key (for natural language features)

### Method 1: Install from PyPI (Recommended)

```bash
pip install git-gud
```

### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/git-gud/git-gud.git
cd git-gud

# Install the package
pip install .

# Or install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Method 3: Using requirements.txt

```bash
# Clone the repository
git clone https://github.com/git-gud/git-gud.git
cd git-gud

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install .
```

### Verify Installation

```bash
# Check if git-gud is installed correctly
git-gud --help

# Verify Git is available
git --version

# Set up OpenRouter API key for natural language features
export OPENROUTER_API_KEY="your-api-key-here"
```

### OpenRouter API Setup

To use the natural language features, you need an OpenRouter API key:

1. Visit [OpenRouter](https://openrouter.ai) and create an account
2. Generate an API key from your dashboard
3. Set the environment variable:

```bash
# Linux/macOS
export OPENROUTER_API_KEY="your-api-key-here"

# Windows (Command Prompt)
set OPENROUTER_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:OPENROUTER_API_KEY="your-api-key-here"
```

**Note**: Without an API key, you can still use the `--execute` flag for direct Git command execution.
```

## Usage

Git Gud offers two ways to interact with Git:

1. **Direct Git Commands** (Phase 1): Execute specific Git commands with safety checks
2. **Natural Language** (Phase 2): Describe what you want to do in plain English

### Natural Language Interface (Phase 2)

Describe what you want to do in natural language, and Git Gud will translate it to the appropriate Git command:

```bash
# Natural language examples
git-gud show me the current status
git-gud list all branches
git-gud show me the last 5 commits
git-gud create a new branch called feature-auth
git-gud switch to the main branch
git-gud show differences since last commit
git-gud add all files and commit with message "fix bug"
```

### Direct Command Execution (Phase 1)

Execute Git commands directly with built-in protection against dangerous operations:

```bash
# Execute safe Git commands (no confirmation required)
git-gud --execute "git status"
git-gud --execute "git log --oneline -10"
git-gud --execute "git diff"
git-gud --execute "git branch -a"

# Execute potentially dangerous commands (requires confirmation)
git-gud --execute "git reset --hard HEAD~1"
git-gud --execute "git push --force origin main"
git-gud --execute "git clean -fd"
```

### Command Line Options

```bash
git-gud [OPTIONS] [PHRASE]...

Arguments:
  [PHRASE]...         Natural language description of what you want to do

Options:
  --execute, -e TEXT  Git command to execute with safety checks
  --help             Show this message and exit
```

### Examples

#### Safe Operations (Execute Immediately)
```bash
# Check repository status
git-gud -e "git status"

# View commit history
git-gud -e "git log --graph --oneline -10"

# Show differences
git-gud -e "git diff HEAD~1"

# List branches
git-gud -e "git branch -v"
```

#### Dangerous Operations (Require Confirmation)
```bash
# Force push (will prompt for confirmation)
git-gud -e "git push --force origin feature-branch"

# Hard reset (will prompt for confirmation)  
git-gud -e "git reset --hard HEAD~3"

# Clean untracked files (will prompt for confirmation)
git-gud -e "git clean -fd"
```

### Interactive Confirmation

When Git Gud detects a dangerous operation, it will:

1. Display a warning message explaining the risks
2. Show which dangerous patterns were detected
3. Prompt for explicit confirmation with "yes"
4. Only proceed if you type exactly "yes"

Example:
```
⚠️  WARNING: This command will permanently delete uncommitted changes
Dangerous patterns detected: reset --hard
Type 'yes' to proceed with this dangerous operation: yes
```

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
# Clone the repository
git clone https://github.com/git-gud/git-gud.git
cd git-gud

# Install in development mode with all dev dependencies
pip install -e ".[dev]"

# Verify installation
git-gud --help
```

### Quick Development Setup

For a complete development setup with all tools:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install

# Run initial tests to verify setup
pytest

# Verify the CLI works
git-gud --help
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=git_gud --cov-report=term-missing

# Run specific test file
pytest tests/test_cli.py

# Run tests in verbose mode
pytest -v
```

### Code Quality Tools

```bash
# Format code with black
black git_gud/ tests/

# Sort imports with isort
isort git_gud/ tests/

# Type checking with mypy
mypy git_gud/

# Lint with flake8
flake8 git_gud/ tests/

# Run all quality checks
black git_gud/ tests/ && isort git_gud/ tests/ && mypy git_gud/ && flake8 git_gud/ tests/
```

### Building and Distribution

```bash
# Build the package
python -m build

# Install locally from built package
pip install dist/git_gud-*.whl

# Upload to PyPI (maintainers only)
python -m twine upload dist/*
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
- openai (for AI-powered natural language translation)
- OpenRouter API key (for natural language features)

## Troubleshooting

### Common Issues

#### "git-gud: command not found"
- Ensure you've installed the package: `pip install git-gud`
- Check that your Python scripts directory is in your PATH
- Try running with full path: `python -m git_gud.cli --help`

#### "Git is not installed or not available in PATH"
- Install Git from https://git-scm.com/downloads
- Ensure `git --version` works in your terminal
- On Windows, make sure Git is added to your PATH during installation

#### Permission Errors
- On Unix systems, you may need to use `pip install --user git-gud`
- Or use a virtual environment: `python -m venv venv && source venv/bin/activate`

#### Import Errors During Development
- Make sure you're in the project directory
- Install in development mode: `pip install -e .`
- Check that all dependencies are installed: `pip install -e ".[dev]"`

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read the contributing guidelines and submit pull requests for any improvements.

## Roadmap

- **Phase 1** ✅ (Complete): Core CLI functionality and safety mechanisms
- **Phase 2** ✅ (Complete): AI-powered natural language to Git command translation
- **Phase 3** (Planned): Advanced context awareness and personalized suggestions