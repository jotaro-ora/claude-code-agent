# Tools Directory - Coding Standards

## Overview

This directory contains high-quality, reusable utility tools that can be used across all project tasks. All code in this directory must adhere to the highest standards of quality, documentation, and maintainability.

**⚠️ IMPORTANT**: This directory is **IMMUTABLE**. Tools here should never be modified during task implementations. Only add new tools or make improvements through careful review and testing.

**🔧 CRITICAL MAINTENANCE RULE**: When modifying any tool in this directory (adding, updating, or removing tools), you MUST also update `tools_list.md` to reflect the changes. This file serves as the authoritative reference for AI agents to understand available functionality.

## Tools Documentation Maintenance

### tools_list.md
- **Purpose**: Comprehensive catalog of all available tools for AI agent reference
- **Location**: `/tools/tools_list.md`
- **Maintenance**: Must be updated whenever tools are added, modified, or removed
- **Content**: Includes purpose, main functions, usage examples, and categorization

### Required Updates to tools_list.md
When making any changes to tools in this directory:

1. **Adding New Tools**: Add complete entry with purpose, main function, description, and usage
2. **Modifying Existing Tools**: Update the corresponding entry to reflect changes
3. **Removing Tools**: Remove the corresponding entry
4. **Function Changes**: Update main function names and descriptions
5. **New Categories**: Add new tool categories if needed

### tools_list.md Update Checklist
- [ ] Tool purpose and main function documented
- [ ] Usage example provided
- [ ] Proper categorization assigned
- [ ] Environment variables listed
- [ ] Error handling notes included
- [ ] Performance considerations documented

## Code Quality Standards

### 1. Module Documentation

Every tool must begin with a comprehensive module-level docstring that includes:

```python
"""
[Tool Name] - Brief Description

This module provides functionality to [primary purpose]. It handles [key features]
and integrates with [external services/APIs if applicable].

Dependencies:
- package1: Purpose and version requirements
- package2: Purpose and version requirements
- standard_library_module: Purpose

Environment Variables Required:
- VARIABLE_NAME: Description and purpose
- ANOTHER_VAR: Description and purpose (optional)

API/Service Limitations:
- Rate limits, quotas, or other constraints
- Data availability windows or restrictions
- Authentication requirements

Usage Example:
    from tools.module_name import main_function
    
    # Basic usage
    result = main_function(
        param1="value1",
        param2="value2"
    )
    
    # Advanced usage with options
    result = main_function(
        param1="value1",
        param2="value2",
        option1=True,
        timeout=30
    )
"""
```

### 2. Function Documentation

All functions must have comprehensive docstrings following this format:

```python
def function_name(param1, param2, optional_param=None):
    """
    Brief description of what the function does.
    
    Detailed explanation of the function's purpose, behavior, and any
    important implementation details. Include algorithm explanations
    for complex logic.
    
    Args:
        param1 (type): Description of parameter, including:
                      - Valid values or ranges
                      - Format requirements
                      - Examples if helpful
        param2 (type): Description with multiple format options:
                      - Format 1: Description
                      - Format 2: Description  
                      - Format 3: Description
        optional_param (type, optional): Description and default behavior.
                                        Defaults to None.
    
    Returns:
        return_type: Description of return value including:
                    - Data structure details
                    - Column names for DataFrames
                    - Possible return states
                    
    Raises:
        SpecificError: When this specific condition occurs
        AnotherError: When this other condition occurs
        ValueError: For invalid input parameters
        
    Limitations and Constraints:
        - Performance limitations
        - Memory usage considerations
        - API rate limits or quotas
        - Data availability constraints
        
    Error Handling:
        - How errors are handled internally
        - Retry logic if applicable
        - Fallback behaviors
        - What errors are propagated vs handled
        
    Performance Notes:
        - Time complexity information
        - Memory usage patterns
        - Optimization considerations
        - Caching recommendations
        
    Example Usage:
        # Basic example
        result = function_name("value1", "value2")
        
        # Advanced example with edge cases
        result = function_name(
            param1="complex_value",
            param2=datetime.now(),
            optional_param={"custom": "config"}
        )
        
        # Example with error handling
        try:
            result = function_name("value1", "value2")
        except SpecificError as e:
            print(f"Handle specific error: {e}")
    """
```

### 3. Error Handling Standards

#### Input Validation
```python
def validate_inputs(param1, param2):
    """Validate all inputs before processing."""
    if not isinstance(param1, str):
        raise TypeError(f"param1 must be string, got {type(param1)}")
    
    if param1.strip() == "":
        raise ValueError("param1 cannot be empty")
    
    # Validate format/pattern
    if not re.match(r'^[A-Z]{3}_[A-Z]{3}$', param1):
        raise ValueError(f"param1 format invalid: {param1}. Expected: XXX_YYY")
```

#### Comprehensive Exception Handling
```python
def robust_api_call(url, params, retries=3):
    """Make API call with comprehensive error handling."""
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            if attempt == retries - 1:
                raise ConnectionError(f"Request timeout after {retries} attempts")
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                time.sleep(5)
                continue
            raise ConnectionError(f"HTTP error: {e}")
            
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                raise ConnectionError(f"Request failed after {retries} attempts: {e}")
            time.sleep(1)
    
    raise ConnectionError("All retry attempts failed")
```

### 4. Environment Variable Management

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_required_env(var_name, description=""):
    """Get required environment variable with clear error message."""
    value = os.getenv(var_name)
    if not value:
        raise KeyError(
            f"Environment variable '{var_name}' is required. "
            f"{description}. Please add it to your .env file."
        )
    return value

# Usage
API_KEY = get_required_env(
    "SERVICE_API_KEY", 
    "Get your API key from https://service.com/api-keys"
)
```

### 5. Helper Functions

Break down complex logic into well-documented helper functions:

```python
def _parse_timestamp(timestamp_input):
    """
    Internal helper to parse various timestamp formats.
    
    Args:
        timestamp_input: Various timestamp formats
        
    Returns:
        int: Unix timestamp in seconds
        
    Note:
        This is an internal function (prefixed with _) used by public functions.
        It handles multiple input formats for user convenience.
    """
    # Implementation with detailed comments
    pass

def _validate_date_range(start_time, end_time):
    """Internal helper to validate date range logic."""
    pass

def _format_response_data(raw_data):
    """Internal helper to standardize response format."""
    pass
```

### 6. Code Structure Standards

#### Imports Organization
```python
# Standard library imports
import os
import time
import re
from datetime import datetime, timezone
from typing import Optional, Dict, List, Union

# Third-party imports  
import requests
import pandas as pd
from dotenv import load_dotenv

# Local imports (if any)
from .utils import helper_function
```

#### Variable Naming
- Use descriptive names: `api_response` not `resp`
- Use snake_case for variables and functions
- Use UPPER_CASE for constants
- Prefix internal functions with underscore: `_helper_function`

#### Comments
```python
# High-level comment explaining the next section's purpose
def complex_function():
    # Step 1: Validate inputs and prepare data
    validated_data = _validate_inputs(raw_input)
    
    # Step 2: Process data with error handling
    try:
        processed_data = _complex_processing(validated_data)
    except ProcessingError as e:
        # Handle specific processing errors
        return _handle_processing_error(e)
    
    # Step 3: Format and return results
    return _format_results(processed_data)
```

### 7. Performance Considerations

#### Memory Management
```python
def process_large_dataset(data_source):
    """Process large datasets efficiently."""
    # Use generators for large data processing
    for chunk in _chunk_data(data_source, chunk_size=1000):
        yield _process_chunk(chunk)
        
    # Clear large objects when done
    del large_temporary_object
```

#### Caching Recommendations
```python
def expensive_operation(param):
    """
    Expensive operation with caching recommendations.
    
    Performance Notes:
        - This operation takes ~5-10 seconds for large datasets
        - Consider caching results for frequently accessed data
        - Memory usage scales linearly with input size
    """
    pass
```

### 8. Testing Integration

Every tool should be designed with testing in mind:

```python
def testable_function(input_data, api_client=None):
    """
    Function designed for easy testing.
    
    Args:
        input_data: The data to process
        api_client: Optional API client for dependency injection
                   (useful for testing with mock clients)
    """
    if api_client is None:
        api_client = _create_default_api_client()
    
    # Function logic that can be easily tested
    return api_client.process(input_data)
```

### 9. Security Best Practices

#### Credential Handling
```python
# ✅ Correct: Use environment variables
api_key = os.getenv("API_KEY")

# ❌ Wrong: Never hardcode credentials
api_key = "hardcoded-secret-key"

# ✅ Correct: Validate credentials without exposing them
if not api_key:
    raise ValueError("API_KEY environment variable is required")

# ❌ Wrong: Don't log or expose credentials
logger.info(f"Using API key: {api_key}")  # Don't do this
```

#### Input Sanitization
```python
def sanitize_user_input(user_input):
    """Sanitize user input to prevent injection attacks."""
    # Remove dangerous characters
    sanitized = re.sub(r'[<>"\';()&+]', '', user_input)
    
    # Validate against expected patterns
    if not re.match(r'^[a-zA-Z0-9_-]+$', sanitized):
        raise ValueError("Input contains invalid characters")
    
    return sanitized.strip()
```

### 10. Example Tool Template

```python
"""
Example Tool - Template for New Tools

This module provides [functionality description]. It demonstrates all the
coding standards required for tools in this directory.

Dependencies:
- requests: For HTTP API calls
- pandas: For data manipulation  
- python-dotenv: For environment variable management

Environment Variables Required:
- EXAMPLE_API_KEY: Your API key from https://service.com

Usage Example:
    from tools.example_tool import main_function
    
    result = main_function(
        param1="value",
        param2="2023-01-01"
    )
"""

import os
import time
from datetime import datetime
from typing import Optional, Dict, Any

import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main_function(param1: str, param2: str, optional_param: Optional[Dict] = None) -> pd.DataFrame:
    """
    Main function following all coding standards.
    
    [Complete docstring following the format above]
    """
    # Input validation
    _validate_inputs(param1, param2)
    
    # Get required environment variables
    api_key = _get_api_key()
    
    # Main logic with error handling
    try:
        result = _process_data(param1, param2, api_key, optional_param)
        return _format_output(result)
    except Exception as e:
        # Handle and re-raise with context
        raise RuntimeError(f"Processing failed: {e}") from e


def _validate_inputs(param1: str, param2: str) -> None:
    """Internal function to validate inputs."""
    pass


def _get_api_key() -> str:
    """Internal function to get API key with proper error handling."""
    pass


def _process_data(param1: str, param2: str, api_key: str, options: Optional[Dict]) -> Dict[str, Any]:
    """Internal function for main processing logic."""
    pass


def _format_output(raw_data: Dict[str, Any]) -> pd.DataFrame:
    """Internal function to format output data."""
    pass
```

## Review Checklist

Before adding any tool to this directory, ensure:

- [ ] Comprehensive module-level docstring
- [ ] All functions have detailed docstrings
- [ ] Input validation for all parameters
- [ ] Proper error handling with specific exceptions
- [ ] Environment variable management using dotenv
- [ ] Clear variable names and logical structure
- [ ] Helper functions for complex logic
- [ ] Security best practices followed
- [ ] Performance considerations documented
- [ ] Multiple usage examples provided
- [ ] Code tested and verified working
- [ ] Dependencies added to requirements.txt

## Integration with Project Framework

All tools in this directory should:

1. **Follow the project's environment variable pattern** using `.env`
2. **Be importable from any task folder** using `from tools.module_name import function`
3. **Handle errors gracefully** without breaking calling code
4. **Be well-documented** so future agents can understand and use them
5. **Be production-ready** with proper error handling and validation

## Maintenance Notes

- This directory should only contain proven, stable tools
- New tools should be thoroughly tested before addition
- Breaking changes should be avoided; create new tools instead
- Each tool should be independent with minimal cross-dependencies
- Regular review and optimization should be performed to maintain quality

---

**Remember**: These tools form the foundation of the entire project. High standards here ensure reliable, maintainable code across all tasks.