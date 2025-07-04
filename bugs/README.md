# Bug Fixing Guidelines for Claude Code

## Overview

This directory contains bug fixing tasks where Claude Code must repair existing code that fails to meet user requirements. Each bug is contained in its own subdirectory with the original code, error reports, and user requirements.

## Core Principles

### 1. Preserve User Intent
- **Never alter the original purpose** of the user intent
- Understand what the user actually wants to achieve, not just what the code tries to do
- If requirements seem unclear, infer from context and user behavior patterns
- Maintain the same input/output interface unless explicitly broken

### 2. Minimal Code Changes
- Apply the **smallest possible fix** that resolves the issue
- Prefer targeted corrections over rewrites
- Keep existing code structure and patterns
- Only refactor when absolutely necessary for the fix

### 3. Requirement-Driven Debugging
- **Start with user requirements**, not error messages
- Errors are symptoms, not root causes
- Verify the code actually solves the user's problem, even if it runs without errors
- Compare actual output against expected behavior from requirements

### 4. Comprehensive Testing
- Test fixes thoroughly before considering them complete
- Look for edge cases and hidden bugs beyond the reported error
- Verify the entire workflow, not just the failing component
- Ensure output format, data accuracy, and business logic are correct

## Bug Fixing Workflow

### Phase 1: Analysis
1. **Read the bug report carefully**
   - Understand the original user requirement
   - Note the specific error message and stack trace
   - Identify what the code was supposed to do vs. what it actually does

2. **Examine the failing code**
   - Trace the execution path to the error
   - Look for obvious issues (API mismatches, missing parameters, wrong data types)
   - Check for configuration or environment issues

3. **Identify root cause vs. symptoms**
   - Error messages often point to symptoms, not causes
   - Look upstream for the actual source of the problem
   - Consider data flow, API constraints, and business logic mismatches

### Phase 2: Fix Implementation
1. **Apply minimal targeted fixes**
   - Change only what's necessary to resolve the issue
   - Preserve existing variable names, function signatures, and code style
   - Use existing patterns and libraries already in the codebase

2. **Handle multiple related issues**
   - Fix the reported error first
   - Test to discover additional hidden problems
   - Address secondary issues that prevent meeting user requirements

3. **Maintain code quality**
   - Keep error handling patterns consistent
   - Preserve existing logging and debugging capabilities
   - Don't introduce new dependencies unless absolutely necessary

### Phase 3: Validation
1. **Test the primary fix**
   - Run the code and verify it doesn't crash
   - Check that error messages are resolved
   - Ensure basic functionality works

2. **Verify user requirements are met**
   - Compare output against what the user actually requested
   - Test with realistic data and scenarios
   - Validate data formats, accuracy, and completeness

3. **Test for regressions and edge cases**
   - Check that existing functionality still works
   - Test with empty data, zero values, and boundary conditions
   - Verify error handling for invalid inputs

## Common Bug Patterns

### API/Configuration Issues
- **Missing or incorrect API parameters** (intervals, endpoints, authentication)
- **Mismatched data formats** between API and code expectations
- **Rate limiting or timeout issues** not properly handled
- **API key management** - see API Key Guidelines section below

### Data Processing Errors
- **Type mismatches** (strings vs numbers, timestamps vs text)
- **Empty or null data** not handled gracefully
- **Array indexing or iteration** problems with variable-length data

### Output Format Problems
- **Wrong output structure** (objects vs arrays, missing fields)
- **Incorrect data serialization** (JSON formatting, date formats)
- **Missing or malformed required fields** in response

### Logic and Business Rule Issues
- **Incomplete understanding of requirements** leading to wrong algorithms
- **Edge case handling** missing for boundary conditions
- **State management problems** in multi-step processes

## API Key Guidelines

### Environment Configuration
- **All API keys must be loaded from the root `.env` file** (same level as `/bugs/` directory)
- **Use python-dotenv for consistent environment loading**:
  ```python
  from dotenv import load_dotenv
  import os
  
  # Load from root .env file
  load_dotenv()
  api_key = os.getenv('API_KEY_NAME')
  ```

### API Key Handling Strategy
1. **Check for API key availability first**:
   ```python
   api_key = os.getenv('COINGLASS_API_KEY')
   if not api_key:
       print("ERROR: COINGLASS_API_KEY not found in .env file")
       exit(1)
   ```

2. **If API key is missing**:
   - **DO NOT continue with the fix**
   - Document in test results that API key is required
   - Wait for administrator to provide the key in root `.env` file
   - Example message: "Fix cannot be completed - missing API_KEY_NAME in root .env file"

3. **If API key is available**:
   - **Test thoroughly** until external API calls succeed
   - **Consult online documentation** for correct API usage
   - **Try different parameter combinations** if initial attempts fail
   - **Implement proper error handling** for API failures
   - **Use appropriate rate limiting** to avoid hitting API limits

### API Integration Best Practices
- **Read API documentation** online when calls fail
- **Test with minimal parameters first**, then add complexity
- **Handle common HTTP status codes** (401, 403, 429, 500)
- **Implement exponential backoff** for retries when appropriate
- **Validate response structure** matches expected format
- **Log API responses** during debugging (without exposing sensitive data)

### Environment File Structure
Root `.env` file should contain:
```bash
# Crypto APIs
COINGLASS_API_KEY=your_key_here
COINGECKO_API_KEY=your_key_here
BINANCE_API_KEY=your_key_here
BINANCE_SECRET_KEY=your_secret_here

# Other service APIs
OPENAI_API_KEY=your_key_here
```

## Best Practices

### Code Modification Strategy
- **Read before writing**: Always examine the existing code thoroughly
- **Test incrementally**: Make small changes and test frequently
- **Preserve patterns**: Match existing code style and architectural decisions
- **Document reasoning**: Use clear commit messages explaining the fix rationale

### Testing Strategy
- **Test the exact scenario** described in the bug report
- **Test with real data** when possible, not just mock data
- **Test error conditions** to ensure robust error handling
- **Validate business logic** against user requirements, not just technical specs

### Quality Assurance
- **Run the full workflow** end-to-end after fixes
- **Check output format and content** match user expectations exactly
- **Verify performance** hasn't degraded significantly
- **Ensure maintainability** for future modifications

## File Organization

Each bug should be contained in its own directory:
```
bugs/
├── bug_task_id/
│   ├── original_code.py          # The failing code
│   ├── bug_report.txt           # Error details and requirements
│   ├── fixed_code.py            # Your corrected version
│   └── test_results.txt         # Verification of the fix
└── README.md                    # This file
```

## Success Criteria

A bug fix is complete when:
1. ✅ **Code runs without errors** in the reported scenario
2. ✅ **Output matches user requirements** exactly
3. ✅ **No regressions** in existing functionality
4. ✅ **Edge cases are handled** appropriately
5. ✅ **Code changes are minimal** and focused
6. ✅ **Original user intent is preserved** and fulfilled
7. ✅ **External API calls work correctly** (if applicable and API keys available)

## Important Reminders

- **Scope limitation**: Only modify files within the specific bug directory
- **Error message focus**: Don't just fix errors - ensure requirements are met
- **Testing persistence**: Keep testing until you're confident the fix is complete
- **User-centric approach**: Always validate from the user's perspective, not just technical correctness
- **API key dependency**: If external APIs require keys not in root `.env`, document this and wait for administrator setup

Remember: A successful bug fix doesn't just eliminate error messages - it delivers what the user originally requested in a reliable, maintainable way.