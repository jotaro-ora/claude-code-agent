# Claude Code Agent Project Framework

## Project Overview

This project is designed to be maintained entirely through Claude Code interactions, with no human maintenance required. All project development, modifications, and maintenance should follow the established framework rules below.

## Core Architecture Rules

### 1. Protected Tools Folder
- **Location**: `/tools/`
- **Status**: IMMUTABLE - Agents must NEVER modify anything in this folder
- **Purpose**: Contains core utility tools available to all requirements
- **Current Tools**:
  - `coingecko.py`: Cryptocurrency data fetching from CoinGecko API

### 2. Requirement-Based Folder Structure
When a user requests a new feature or functionality:
- Create a new folder named after the requirement (use kebab-case: `user-authentication`, `data-visualization`, etc.)
- All related content for that requirement goes in its dedicated folder:
  - Source code
  - Tests
  - Data storage
  - Configuration files
  - Custom tools (if needed)
  - Documentation

### 3. Tool Priority System
1. **First Priority**: Use tools from `/tools/` folder
2. **Second Priority**: If `/tools/` cannot complete the task, create custom tools
3. **Custom Tool Location**: Place custom tools in the requirement's folder, not in `/tools/`

### 4. Required Documentation Standards
Every requirement folder MUST contain:
- **README.md**: Comprehensive documentation including:
  - Requirement description and purpose
  - Agent's thought process and design decisions
  - File structure explanation
  - Usage instructions for each file
  - Dependencies and setup instructions
  - Testing procedures

### 5. Code Quality Standards
All agent-generated code MUST:
- **Include comprehensive comments** explaining functionality, parameters, and return values
- **Follow test-driven development**: Write tests before implementation
- **Be continuously tested**: Agent must execute and verify code works before completion
- **Consider dependencies**: When modifying code, check all references and update accordingly
- **Handle errors gracefully**: Include proper error handling and logging

### 6. Environment Configuration
- **File**: `.env` (project root)
- **Purpose**: Store all API keys, passwords, and sensitive configuration
- **Access**: Agents should read from `.env` when credentials are needed
- **Security**: Never hardcode credentials in source files

### 7. Performance Requirements
- **Execution Time**: Single script execution must complete within 10 minutes
- **Performance Analysis**: Always consider computational efficiency and resource usage
- **Optimization**: Implement appropriate caching, pagination, and rate limiting
- **Monitoring**: Track execution time and provide progress indicators for long-running tasks
- **Scalability**: Design solutions that can handle reasonable data volumes without timeout

### 8. Requirement Independence
- **Isolation**: Each requirement must be completely independent and self-contained
- **No Dependencies**: Requirements should NOT depend on other requirement folders
- **Shared Resources**: Only use tools from `/tools/` folder for shared functionality
- **Data Separation**: Each requirement manages its own data and configuration
- **Standalone Execution**: Any requirement should work independently after fresh project setup

## Development Workflow

### Core Development Principles:
1. **Preserve Original Requirements**: Never modify user's explicit requirements. If requirements lack detail, supplement with reasonable defaults but never change explicit instructions.
2. **Quality Assurance**: After implementing requirements, test results against common sense and look for obvious errors (missing variables, empty returns, etc.). Fix issues immediately.
3. **Version Control**: Delete redundant code versions - maintain only one primary working version per feature.
4. **Parameterization**: Make key task parameters externally configurable for future control and flexibility.

### For New Requirements:
1. **Create requirement folder**: `/requirement-name/`
2. **Set up basic structure**:
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
9. **Clean up**: Remove any temporary or duplicate versions
10. **Update dependencies**: Check and update any affected code

### For Modifications:
1. **Read existing documentation**: Understand current implementation
2. **Identify impact**: Find all code that references what you're changing
3. **Respect original requirements**: Don't change explicit user specifications unless explicitly requested
4. **Update tests first**: Modify or add tests for new behavior
5. **Implement changes**: Make code modifications with configurable parameters where possible
6. **Verify functionality**: Test until everything works and results make sense
7. **Clean up versions**: Remove outdated or redundant code versions
8. **Update documentation**: Reflect changes in README.md

## File Organization Examples

### Example 1: Web Scraping Requirement
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

### Example 2: API Integration Requirement
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

## Environment Variables Template

Create and maintain `.env` with:
```bash
# CoinGecko API
COINGECKO_API_KEY=your_coingecko_api_key_here

# Add other API keys as needed
# OPENAI_API_KEY=your_openai_key
# DATABASE_URL=your_database_url
# OTHER_SERVICE_KEY=your_key
```

## Testing Standards

All code must include:
- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows
- **Error handling tests**: Test failure scenarios

## Documentation Requirements

### README.md Template for Requirements:
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

## Security Guidelines

- **Never hardcode credentials**: Always use `.env`
- **Validate inputs**: Sanitize all user inputs
- **Handle secrets safely**: Don't log or expose sensitive data
- **Use secure practices**: Follow security best practices for the technology stack

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
11. **Document thoroughly** especially thought processes
12. **Consider impact** on existing code when making changes

## Version Control (When Applicable)

If git is used:
- Commit frequently with clear messages
- Include requirement folder name in commit messages
- Tag major milestones
- Keep detailed commit history

## Error Handling Standards

All code should:
- Use try-catch blocks appropriately
- Log errors clearly
- Provide helpful error messages
- Fail gracefully when possible
- Include recovery mechanisms where appropriate

---

**Remember**: This project is designed for complete autonomous maintenance through Claude Code. Following these guidelines ensures consistency, maintainability, and successful long-term development without human intervention.