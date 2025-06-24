# Claude Code Agent Project Framework

## Project Overview

This project is designed to be maintained entirely through Claude Code interactions, with no human maintenance required. All project development, modifications, and maintenance should follow the established framework rules below.

## Core Architecture Rules

### 1. Protected Tools Folder
- **Location**: `/tools/` - IMMUTABLE (Agents must NEVER modify)
- **Purpose**: Contains core utility tools available to all requirements
- **Current Tools**: `coingecko.py` (Cryptocurrency data fetching from CoinGecko API)

### 2. Requirement-Based Folder Structure
When a user requests a new feature or functionality:
- Create a new folder named after the requirement (use kebab-case: `user-authentication`, `data-visualization`)
- All related content goes in its dedicated folder: source code, tests, data, configuration, custom tools, documentation

### 3. Tool Priority System
1. **First Priority**: Use tools from `/tools/` folder
2. **Second Priority**: If `/tools/` cannot complete the task, create custom tools in the requirement's folder
3. **Custom Tool Location**: Never place custom tools in `/tools/`

### 4. Requirement Independence
- Each requirement must be completely independent and self-contained
- Requirements should NOT depend on other requirement folders
- Only use `/tools/` folder for shared functionality
- Each requirement manages its own data and configuration
- Any requirement should work independently after fresh project setup

## Development Principles

### Core Principles:
1. **Preserve Original Requirements**: Never modify user's explicit requirements. Supplement missing details with reasonable defaults but never change explicit instructions.
2. **Quality Assurance**: Test results against common sense and fix obvious errors (missing variables, empty returns, etc.) immediately.
3. **Version Control**: Delete redundant code versions - maintain only one primary working version per feature.
4. **Parameterization**: Make key task parameters externally configurable for future control and flexibility.
5. **File Management**: Only save files when explicitly requested by user or when task requires state persistence for successful execution.
6. **Documentation Synchronization**: When modifying requirements, always update the corresponding README.md file. When creating new implementations, remove outdated versions.

### Code Quality Standards
All agent-generated code MUST:
- Include comprehensive comments explaining functionality, parameters, and return values
- Follow test-driven development: Write tests before implementation
- Be continuously tested: Agent must execute and verify code works before completion
- Consider dependencies: When modifying code, check all references and update accordingly
- Handle errors gracefully: Include proper error handling and logging

### Performance & Security
- **Execution Time**: Single script execution must complete within 10 minutes
- **Performance**: Consider computational efficiency, implement caching, pagination, and rate limiting
- **Environment Configuration**: Use `.env` file for all API keys and sensitive data
- **Security**: Never hardcode credentials, validate inputs, handle secrets safely

## Development Workflow

### For New Requirements:
1. **Create requirement folder**: `/requirement-name/`
2. **Set up structure**:
   ```
   requirement-name/
   ├── README.md
   ├── src/
   ├── tests/
   ├── data/ (if needed)
   └── tools/ (if custom tools needed)
   ```
3. **Write comprehensive README.md**
4. **Implement with tests**: Follow TDD approach
5. **Continuous testing**: Execute code until it works correctly
6. **Quality validation**: Check results for logical consistency and obvious errors
7. **Performance validation**: Ensure execution time stays within 10-minute limit
8. **Independence verification**: Confirm no dependencies on other requirements
9. **File management**: Only save files necessary for task completion or user-requested outputs
10. **Clean up**: Remove any temporary or duplicate versions

### For Modifications:
1. **Read existing documentation**: Understand current implementation
2. **Identify impact**: Find all code that references what you're changing
3. **Respect original requirements**: Don't change explicit user specifications unless explicitly requested
4. **Update tests first**: Modify or add tests for new behavior
5. **Implement changes**: Make code modifications with configurable parameters where possible
6. **Verify functionality**: Test until everything works and results make sense
7. **Clean up versions**: Remove outdated or redundant code versions
8. **Synchronize documentation**: Update README.md to reflect all changes made to the requirement
9. **File management**: Only save modified files necessary for functionality

## Documentation Standards

### Required Documentation
Every requirement folder MUST contain:
- **README.md**: Comprehensive documentation including requirement description, agent's thought process, file structure, usage instructions, dependencies, and testing procedures

### README.md Template:
```markdown
# [Requirement Name]

## Purpose
Brief description of what this requirement accomplishes.

## Agent Thought Process
Detailed explanation of design decisions and approach.

## File Structure
- `src/`: Main source code
- `tests/`: Test files
- `data/`: Data storage (if applicable)
- `tools/`: Custom tools (if applicable)

## Dependencies
List of required packages and tools.

## Setup Instructions
Step-by-step setup process.

## Usage
How to use the implemented functionality.

## Testing
How to run tests and verify functionality.

## Integration Points
How this integrates with other parts of the project.
```

## Testing Requirements

All code must include:
- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows
- **Error handling tests**: Test failure scenarios

## Environment Configuration

Create and maintain `.env` with:
```bash
# CoinGecko API
COINGECKO_API_KEY=your_coingecko_api_key_here

# Add other API keys as needed
# OPENAI_API_KEY=your_openai_key
# DATABASE_URL=your_database_url
# OTHER_SERVICE_KEY=your_key
```

## Maintenance Protocol

When agents work on this project they should:
1. **Always read CLAUDE.md first** to understand the framework
2. **Use TodoWrite tool** to plan and track work
3. **Follow the folder structure** exactly as specified
4. **Respect user requirements** - never modify explicit user specifications without permission
5. **Test continuously** until code works correctly
6. **Validate results** for logical consistency and obvious errors
7. **Validate performance** ensuring 10-minute execution limit compliance
8. **Ensure independence** from other requirement folders
9. **Clean up redundant versions** - maintain only primary working code
10. **Make parameters configurable** where it adds value for future control
11. **Manage files responsibly** - only save when explicitly requested or functionally required
12. **Synchronize documentation** - update README files when making changes to requirements
13. **Document thoroughly** especially thought processes
14. **Consider impact** on existing code when making changes

## File Organization Examples

### Web Scraping Requirement
```
web-scraping/
├── README.md                 # Full documentation
├── src/
│   ├── scraper.py           # Main scraping logic
│   └── utils.py             # Helper functions
├── tests/
│   ├── test_scraper.py      # Unit tests
│   └── test_integration.py  # Integration tests
├── data/
│   └── scraped_data.json    # Output storage
└── config/
    └── scraping_config.yaml # Configuration
```

### API Integration Requirement
```
api-integration/
├── README.md
├── src/
│   ├── api_client.py        # API wrapper class
│   ├── data_processor.py    # Process API responses
│   └── models.py            # Data models
├── tests/
│   ├── test_api_client.py
│   └── test_data_processor.py
└── tools/                   # Custom tools if needed
    └── custom_auth.py       # Special authentication tool
```

## Error Handling Standards

All code should:
- Use try-catch blocks appropriately
- Log errors clearly
- Provide helpful error messages
- Fail gracefully when possible
- Include recovery mechanisms where appropriate

---

**Remember**: This project is designed for complete autonomous maintenance through Claude Code. Following these guidelines ensures consistency, maintainability, and successful long-term development without human intervention.