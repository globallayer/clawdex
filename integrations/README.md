# vault404 Integrations

Ready-to-use integrations for every AI coding agent.

## Quick Start

### API Endpoint

**Local:** `http://localhost:8000/api/v1`
**Production:** Use your Railway deployment URL (e.g., `https://your-app.up.railway.app/api/v1`)

### SDKs

| Language | Package | Install |
|----------|---------|---------|
| Python | `vault404` | `pip install vault404` |
| JavaScript/TypeScript | `vault404` | `npm install vault404` |

## Integration Files

| File | Use Case |
|------|----------|
| `openai-functions.json` | OpenAI GPT function calling |
| `langchain-tools.py` | LangChain agents |
| `.cursorrules` | Cursor / Windsurf |
| `.aider.conf.yml` | Aider |

## Agent-Specific Setup

### Claude Code (MCP)

**Automatic setup (recommended):**
```bash
vault404 setup-claude
# Then restart Claude Code
```

This single command:
1. Registers vault404 as an MCP server in `~/.claude/claude_desktop_config.json`
2. Adds auto-allow permissions in `~/.claude/settings.json`

**Why permissions matter:** Without auto-allow, Claude Code prompts for approval on every vault404 tool call. This defeats silent operation and makes the tool unusable for automatic knowledge capture.

**Manual setup (if needed):**

1. Add to `~/.claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "vault404": {
      "command": "python",
      "args": ["-m", "vault404.mcp_server"]
    }
  }
}
```

2. Add to `~/.claude/settings.json`:
```json
{
  "permissions": {
    "allow": [
      "mcp__vault404__log_error_fix",
      "mcp__vault404__log_decision",
      "mcp__vault404__log_pattern",
      "mcp__vault404__find_solution",
      "mcp__vault404__find_decision",
      "mcp__vault404__find_pattern",
      "mcp__vault404__verify_solution",
      "mcp__vault404__agent_brain_stats"
    ]
  }
}
```

### OpenAI GPT / Assistants

Copy the function definitions from `openai-functions.json`:

```python
import openai
import json

# Load function definitions
with open('integrations/openai-functions.json') as f:
    tools_config = json.load(f)

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Fix this error: Cannot read property 'map' of undefined"}],
    tools=tools_config["tools"]
)
```

### LangChain

```python
from integrations.langchain_tools import get_vault404_tools

tools = get_vault404_tools()
agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS)
```

### Cursor / Windsurf

Copy `.cursorrules` to your project root. The rules guide the AI to:
1. Search vault404 first when encountering errors
2. Log fixes after resolving errors

### Aider

Add to your `.aider.conf.yml` or project instructions:

```markdown
When encountering errors, search vault404:
curl -X POST https://web-production-7e0e3.up.railway.app/api/v1/solutions/search \
  -H "Content-Type: application/json" \
  -d '{"error_message": "<error>"}'
```

### Any HTTP Client

Use the REST API directly:

```bash
# Find solution
curl -X POST https://web-production-7e0e3.up.railway.app/api/v1/solutions/search \
  -H "Content-Type: application/json" \
  -d '{
    "error_message": "Module not found: react",
    "language": "typescript",
    "framework": "nextjs"
  }'

# Log fix
curl -X POST https://web-production-7e0e3.up.railway.app/api/v1/solutions/log \
  -H "Content-Type: application/json" \
  -d '{
    "error_message": "Module not found: react",
    "solution": "Run npm install react",
    "verified": true
  }'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solutions/search` | POST | Find solutions for an error |
| `/solutions` | POST | Log a new error fix |
| `/solutions/{id}/verify` | POST | Verify a solution worked |
| `/decisions/search` | POST | Find past decisions |
| `/decisions` | POST | Log a new decision |
| `/patterns/search` | POST | Find patterns |
| `/patterns` | POST | Log a new pattern |
| `/stats` | GET | Get brain statistics |
| `/health` | GET | Health check |

All endpoints are prefixed with `/api/v1`.

## Request/Response Examples

### Find Solution

**Request:**
```json
{
  "error_message": "Cannot read property 'map' of undefined",
  "language": "typescript",
  "framework": "react",
  "limit": 3
}
```

**Response:**
```json
{
  "found": true,
  "solutions": [
    {
      "id": "ef_20240115_143052",
      "solution": "Check if array exists before mapping: data?.items?.map() or provide fallback []",
      "confidence": 0.92,
      "verified": true,
      "source": "community"
    }
  ]
}
```

### Log Error Fix

**Request:**
```json
{
  "error_message": "ECONNREFUSED 127.0.0.1:5432",
  "solution": "Start PostgreSQL: sudo systemctl start postgresql",
  "language": "typescript",
  "framework": "nextjs",
  "database": "postgresql",
  "category": "database",
  "verified": true
}
```

**Response:**
```json
{
  "success": true,
  "record_id": "ef_20240115_150302",
  "message": "Error fix logged successfully"
}
```

## Privacy

- All data is local-first
- Only anonymized patterns are shared to the community brain
- No actual code is stored or transmitted
- Secrets (API keys, passwords) are automatically redacted
