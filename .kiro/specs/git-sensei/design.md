# Design Document

## Overview

Git sensei is designed as a modular Python CLI application that provides a safe interface to Git operations. The architecture emphasizes separation of concerns with distinct modules for command-line interface, Git interaction, and safety validation. The design prioritizes safety through proactive dangerous operation detection and user confirmation workflows.

## Architecture

The application follows a layered architecture pattern:

```
┌─────────────────────────────────────┐
│           CLI Layer                 │
│        (Typer/Click)               │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│         Safety Module               │
│    (Command Validation)            │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│      Git Interaction Module        │
│       (subprocess wrapper)         │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│         System Git                  │
└─────────────────────────────────────┘
```

## Components and Interfaces

### 1. CLI Module (`cli.py`)

**Purpose:** Entry point and command-line interface handling

**Key Functions:**
- `main()`: Primary entry point for the application
- `execute_command(command: str)`: Handler for --execute flag
- `setup_cli()`: Configure Typer/Click application

**Interface:**
```python
def main() -> None:
    """Main CLI entry point"""

def execute_command(command: str) -> None:
    """Execute a Git command with safety checks"""
```

### 2. Git Interaction Module (`git_ops.py`)

**Purpose:** Abstraction layer for Git command execution

**Key Classes:**
```python
@dataclass
class GitResult:
    stdout: str
    stderr: str
    exit_code: int
    command: str
    success: bool
```

**Key Functions:**
```python
def execute_git_command(command: str) -> GitResult:
    """Execute Git command and return structured result"""

def is_git_available() -> bool:
    """Check if Git is installed and accessible"""

def get_git_version() -> str:
    """Get installed Git version"""
```

### 3. Safety Module (`safety.py`)

**Purpose:** Command validation and user confirmation for dangerous operations

**Key Classes:**
```python
@dataclass
class SafetyCheck:
    is_safe: bool
    dangerous_patterns: List[str]
    warning_message: str
```

**Key Functions:**
```python
def check_command_safety(command: str) -> SafetyCheck:
    """Analyze command for dangerous patterns"""

def get_user_confirmation(warning_message: str) -> bool:
    """Prompt user for confirmation of dangerous operation"""

def load_dangerous_patterns() -> List[str]:
    """Load list of dangerous Git operation patterns"""
```

**Dangerous Patterns List:**
- `push --force` / `push -f`
- `reset --hard`
- `filter-branch`
- `rebase -i` (interactive rebase)
- `checkout --force` / `checkout -f`
- `clean -fd` (force delete untracked files)
- `reflog expire`
- `gc --prune=now`
- `update-ref -d`

### 4. Configuration Module (`config.py`)

**Purpose:** Application configuration and settings management

**Key Functions:**
```python
def load_config() -> Dict[str, Any]:
    """Load application configuration"""

def get_dangerous_patterns() -> List[str]:
    """Get configured dangerous patterns"""
```

## Data Models

### GitResult
Encapsulates the result of a Git command execution:
- `stdout`: Standard output from the command
- `stderr`: Standard error output
- `exit_code`: Process exit code
- `command`: Original command that was executed
- `success`: Boolean indicating if command succeeded (exit_code == 0)

### SafetyCheck
Represents the safety analysis of a command:
- `is_safe`: Boolean indicating if command is safe to execute
- `dangerous_patterns`: List of dangerous patterns found in the command
- `warning_message`: Human-readable warning about the risks

## Error Handling

### Git Command Errors
- **Git Not Found**: Clear error message with installation instructions
- **Invalid Git Command**: Display Git's error message with context
- **Permission Errors**: Inform user about repository access issues
- **Network Errors**: Handle timeout and connectivity issues for remote operations

### User Input Errors
- **Invalid CLI Arguments**: Show usage help and examples
- **Confirmation Timeout**: Default to aborting dangerous operations
- **Interrupted Operations**: Graceful handling of Ctrl+C

### System Errors
- **Subprocess Failures**: Capture and report system-level errors
- **File System Issues**: Handle repository access and permission problems

## Testing Strategy

### Unit Tests
- **CLI Module**: Test argument parsing and command routing
- **Git Operations**: Mock subprocess calls to test command execution logic
- **Safety Module**: Test dangerous pattern detection with comprehensive test cases
- **Configuration**: Test config loading and validation

### Integration Tests
- **End-to-End Workflows**: Test complete user scenarios from CLI to Git execution
- **Safety Workflows**: Test dangerous command detection and confirmation flows
- **Error Scenarios**: Test error handling across module boundaries

### Test Data
- **Safe Commands**: `git status`, `git log`, `git diff`, `git branch`
- **Dangerous Commands**: `git reset --hard HEAD~1`, `git push --force origin main`
- **Edge Cases**: Commands with mixed safe/dangerous elements

### Mock Strategy
- Mock `subprocess.run` for Git command execution
- Mock user input for confirmation testing
- Use temporary Git repositories for integration tests

## Security Considerations

### Command Injection Prevention
- Validate and sanitize all user input
- Use subprocess with shell=False to prevent shell injection
- Whitelist allowed Git commands and flags

### Privilege Management
- Run with minimal required permissions
- Never require elevated privileges for normal operations
- Warn users about operations that modify repository history

### Data Protection
- Never log sensitive information (passwords, tokens)
- Respect Git's credential handling mechanisms
- Provide clear warnings about data loss risks

## Performance Considerations

### Command Execution
- Implement reasonable timeouts for Git operations
- Provide progress indicators for long-running commands
- Cache Git availability checks

### User Experience
- Minimize confirmation prompts for experienced users
- Provide verbose and quiet modes
- Fast startup time for CLI responsiveness

## Future Extensibility

### AI Integration Points
- **Command Translation**: Natural language to Git command conversion
- **Context Awareness**: Repository state analysis for better suggestions
- **Learning**: User pattern recognition for personalized safety rules

### Plugin Architecture
- Modular safety rule definitions
- Custom command handlers
- External tool integrations

### Configuration Extensions
- User-specific dangerous pattern customization
- Team-wide safety policy enforcement
- Integration with Git hooks and workflows