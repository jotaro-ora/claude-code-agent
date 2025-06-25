# Claude Code Agent Project Framework

## Project Overview

This project is designed for autonomous maintenance through Claude Code interactions. All development follows established framework rules to ensure consistency and maintainability.

## Core Architecture

### 1. Protected Tools Folder (`/tools/`)
- **IMMUTABLE**: Never modify during task implementations
- **Purpose**: Shared utility tools for all tasks
- **Documentation**: `tools_list.md` catalogs all available tools
- **Priority**: Always use existing tools before creating custom ones

### 2. Task-Based Structure (`/tasks/`)
- **Location**: All task implementations go in `/tasks/task-name/`
- **Independence**: Tasks are completely isolated from each other
- **Focus**: Work on only one task at a time to minimize token usage
- **Structure**:
  ```
  tasks/task-name/
  ├── README.md
  ├── src/
  ├── tests/
  ├── data/ (if needed)
  └── tools/ (custom tools only)
  ```

### 3. Task Isolation Principle
- **Single Task Focus**: Only read/analyze files from the current task being worked on
- **Token Efficiency**: Avoid loading multiple task contexts simultaneously
- **Independence**: Tasks should not reference or depend on other tasks
- **Shared Resources**: Use only `/tools/` for cross-task functionality

## Development Standards

### Code Quality Requirements
- **State Management**: Implement persistence for stateful tasks to handle restarts
- **Environment Variables**: Load all credentials from root `.env` using python-dotenv
- **CLI Parameters**: Make key parameters configurable via command-line arguments
- **Error Handling**: Comprehensive error handling with specific exceptions
- **Testing**: Write tests before implementation (TDD approach)
- **Documentation**: Comprehensive docstrings and comments
- **Performance**: Complete execution within 10 minutes

### Environment Configuration
Root `.env` file format:
```bash
# API Keys
COINGECKO_API_KEY=your_key_here
```

Load in code:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('COINGECKO_API_KEY')
```

## Development Workflow

### For New Tasks
1. Create folder: `/tasks/task-name/`
2. Set up standard structure
3. Check `tools_list.md` for existing tools
4. Implement with state persistence and CLI args
5. Write comprehensive tests
6. Document in README.md

### For Modifications
1. Focus only on the specific task being modified
2. Update tests first
3. Implement changes with CLI configurability
4. Verify functionality through testing
5. Update task's README.md

### Tool Usage Priority
1. **First**: Use existing tools from `/tools/`
2. **Second**: Create custom tools in task's `/tools/` folder
3. **Never**: Place custom tools in `/tools/`

## Documentation Standards

### Task README.md Template
```markdown
# [Task Name]

## Purpose
Brief description of task functionality.

## Usage
Command-line usage examples with parameters.

## Dependencies
Required packages and environment variables.

## Testing
How to run tests and verify functionality.
```

### Tools Documentation
- **Mandatory**: Update `tools_list.md` when modifying `/tools/`
- **Purpose**: Enable AI agents to discover available functionality
- **Content**: Tool purpose, functions, usage examples

## Maintenance Protocol

### Agent Guidelines
1. **Read CLAUDE.md first** to understand framework
2. **Use TodoWrite** to plan and track work
3. **Focus on single task** to minimize token usage
4. **Respect task independence** - no cross-task dependencies
5. **Test continuously** until code works correctly
6. **Make parameters CLI-configurable** where valuable
7. **Clean up redundant code** - maintain only working versions
8. **Document thoroughly** especially design decisions

### File Management
- **Save files only when**: Explicitly requested or functionally required
- **Clean up**: Remove temporary or duplicate versions
- **State files**: Only for tasks requiring persistence

## Performance & Security

### Execution Requirements
- **Time limit**: 10 minutes maximum per script
- **Memory efficiency**: Use generators for large datasets
- **Rate limiting**: Implement for API calls
- **Caching**: Recommend for expensive operations

### Security Standards
- **Never hardcode credentials**: Use environment variables only
- **Input validation**: Sanitize all user inputs
- **Error messages**: Don't expose sensitive information
- **Credential logging**: Never log API keys or secrets

## Error Handling Standards

### Required Patterns
```python
# Input validation
if not isinstance(param, expected_type):
    raise TypeError(f"Expected {expected_type}, got {type(param)}")

# API error handling
try:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
except requests.exceptions.Timeout:
    raise ConnectionError("Request timeout")
except requests.exceptions.HTTPError as e:
    raise ConnectionError(f"HTTP error: {e}")
```

## Testing Requirements

### Test Coverage
- **Unit tests**: Individual functions/methods
- **Integration tests**: Component interactions  
- **Error handling**: Failure scenarios
- **Performance**: Execution time validation

---

**Framework Goal**: Enable complete autonomous maintenance through Claude Code while ensuring consistency, security, and performance across all tasks.