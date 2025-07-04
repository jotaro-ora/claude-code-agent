# API Key Loading Configuration — LunarCrush API

## Overview
Every tool in the `/tools/` directory automatically loads API keys from the project‑root `.env` file. This keeps key management consistent no matter where the tool is executed.

**⚠️ Important Note**: As of 2025, LunarCrush API v3 endpoints require a paid subscription with API credits. The tools are implemented correctly but will return payment-required errors unless you have an active paid subscription. Contact LunarCrush support for current pricing and v4 endpoint migration options.

## Configuration Details

### Environment‑Variable Loading
```python
import os
from dotenv import load_dotenv

# Load environment variables from the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))
```
This guarantees that  
- the same `.env` in the project root is always used,  
- keys load correctly regardless of the current working directory, and  
- every tool behaves identically.  

### Required API Keys

#### LunarCrush API Key
- **Environment Variable**: `LUNA_CRUSH_API_KEY`
- **Required For**: All LunarCrush tools
- **Header Format**:
  ```python
  headers = {"Authorization": f"Bearer {os.getenv('LUNA_CRUSH_API_KEY')}"}
  ```

### Tools that call LunarCrush *(initial set)*

| File | Purpose |
| ---- | ------- |
| `lunacrush.py` | Core thin wrapper around common request logic |
| `coins_list.py` | List all supported coins |
| `coin_meta.py` | Metadata for a specific coin |
| `coin_time_series.py` | Historical social + market metrics |
| `topic_details.py` | 24‑h aggregate metrics for a topic |
| `topic_time_series.py` | Historical topic metrics |
| `topic_posts.py` | Top social posts for a topic |
| `topic_news.py` | Top news articles for a topic |
| `topic_creators.py` | Top creators/influencers for a topic |
| `category_details.py` | Snapshot metrics for a social category |
| `category_time_series.py` | Historical metrics for a category |

*(Add additional endpoint wrappers as you expand coverage.)*

## `.env` File Structure
```env
# LunarCrush API
LUNA_CRUSH_API_KEY=your_lunarcrush_api_key_here

# Other API keys …
```

## Directory Structure (example)
```
claude-code-agent/
├── .env
├── tools/
│   ├── lunacrush.py
│   ├── coins_list.py
│   ├── coin_meta.py
│   ├── coin_time_series.py
│   ├── topic_details.py
│   ├── topic_time_series.py
│   ├── topic_posts.py
│   ├── topic_news.py
│   ├── topic_creators.py
│   ├── category_details.py
│   ├── category_time_series.py
│   └── ...
└── ...
```

## Usage Examples

### Basic
```python
from tools.topic_details import get_topic_details

# Keys are auto‑loaded
details = get_topic_details("bitcoin")
```

### Verification
```python
import os
from dotenv import load_dotenv
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

print("LUNA_CRUSH_API_KEY:", "Loaded" if os.getenv("LUNA_CRUSH_API_KEY") else "Missing")
```

## Error Handling
```python
if not os.getenv("LUNA_CRUSH_API_KEY"):
    raise EnvironmentError("Missing LUNA_CRUSH_API_KEY — set it in your .env file")
```

## Best Practices
1. **Never commit keys** — keep `.env` in `.gitignore`.  
2. **Always use `os.getenv()`** rather than hard‑coding.  
3. **Validate on init** — fail fast if the key is missing.  
4. **Surface clear errors** — explain missing/invalid key issues.  
5. **Rotate keys regularly** and monitor usage.

## Troubleshooting

| Issue | Fix |
| ----- | --- |
| `LUNA_CRUSH_API_KEY` not found | Ensure `.env` exists in project root and the variable is set |
| 401 Unauthorized | Check key value and header format |
| Rate‑limit errors | Review plan limits and back‑off logic |
| Network timeouts | Confirm internet access / LunarCrush status |

## Security Notes
- Treat API keys as secrets; never print them in logs.  
- Limit key scope from the LunarCrush dashboard if possible.  
- Rotate keys periodically and monitor for abuse.
