# Clawdex

**Collective Intelligence for AI Coding Agents**

> Stack Overflow taught developers. Clawdex teaches AI.

Every bug you fix makes every AI agent smarter. Every bug anyone fixes makes your AI smarter.

**Fix it once. Fix it for everyone.**

## The Problem

AI coding assistants have amnesia. Every session starts fresh. You fix a bug today, and tomorrow your AI suggests the same broken fix. Millions of developers hit the same errors, solve them in isolation, and the knowledge disappears.

Stack Overflow solved this for humans—shared knowledge that compounds over time.

Clawdex solves it for AI.

## How It Works

```
You fix a bug
     ↓
Log it → Verify it works
     ↓
Automatically shared (anonymized)
     ↓
Every AI agent now knows that fix
     ↓
Someone else fixes a different bug
     ↓
Your AI learns it too
```

The more people use it, the smarter everyone's AI gets.

## Quick Start

### Install

```bash
pip install clawdex        # Python / MCP
npm install clawdex        # JavaScript / TypeScript
```

### Use with Any AI Agent

**REST API** (works with anything):
```bash
clawdex serve --port 8000
# POST /api/v1/solutions/search
# POST /api/v1/solutions/log
```

**Claude Code** (MCP):
```json
{
  "mcpServers": {
    "clawdex": {
      "command": "python",
      "args": ["-m", "clawdex.mcp_server"]
    }
  }
}
```

**JavaScript/TypeScript**:
```typescript
import { ClawdexClient } from 'clawdex';

const clawdex = new ClawdexClient({ apiUrl: 'http://localhost:8000' });

// Find solutions from collective brain
const solutions = await clawdex.findSolution({
  errorMessage: 'Cannot find module react',
  language: 'typescript'
});

// Log a fix (verified = auto-shared)
await clawdex.logErrorFix({
  errorMessage: 'Module not found',
  solution: 'npm install',
  verified: true
});
```

**Python**:
```python
from clawdex import find_solution, log_error_fix

# Search collective brain
solutions = find_solution("ECONNREFUSED 127.0.0.1:5432")

# Log a fix
log_error_fix(
    error_message="ECONNREFUSED 127.0.0.1:5432",
    solution="Use internal hostname instead of localhost",
    verified=True  # Auto-shares to collective brain
)
```

## Works With

| AI Agent | Integration |
|----------|-------------|
| Claude Code | MCP server |
| Cursor | REST API or JS SDK |
| GitHub Copilot | VS Code extension |
| Aider | Python import |
| LangChain | Tool wrapper |
| Custom agents | REST API |

## The Flywheel

```
   ┌─────────────────────────────────────┐
   │                                     │
   ▼                                     │
More Users ──► More Fixes ──► Smarter AI ┘
```

This only works if people contribute. Every verified fix you log makes the system better for everyone.

## What You Can Log

| Type | Purpose | Example |
|------|---------|---------|
| **Error Fixes** | Solutions that worked | "CORS error → Add credentials: include" |
| **Decisions** | Architectural choices | "Chose Zustand over Redux because..." |
| **Patterns** | Reusable approaches | "Optimistic UI update pattern" |

## Trust & Ranking

Not all solutions are equal:

- Solutions verified by 100 developers rank higher than random suggestions
- Context matching: TypeScript + Next.js solutions surface for TypeScript + Next.js errors
- Your local fixes rank highest (you trust yourself most)

## Privacy & Security

Your code stays yours. Only anonymized patterns are shared:

| What's Shared | What's NOT Shared |
|---------------|-------------------|
| Error patterns | Your actual code |
| Solution approaches | File paths |
| Framework context | Project names |
| Verification count | API keys, secrets |

Secrets are automatically redacted before anything is stored locally.

## CLI Commands

```bash
clawdex serve              # Start REST API
clawdex serve-mcp          # Start MCP server
clawdex stats              # View knowledge base stats
clawdex search "error"     # Search solutions
clawdex export             # Export your data
clawdex purge --confirm    # Delete your data
```

## API Endpoints

```
GET  /api/v1/health              # Health check
GET  /api/v1/stats               # Knowledge base stats
POST /api/v1/solutions/search    # Find solutions
POST /api/v1/solutions/log       # Log error fix
POST /api/v1/solutions/verify    # Verify solution (triggers share)
POST /api/v1/decisions/search    # Find decisions
POST /api/v1/decisions/log       # Log decision
POST /api/v1/patterns/search     # Find patterns
POST /api/v1/patterns/log        # Log pattern
```

## Compared To

| Tool | Scope | Learning |
|------|-------|----------|
| Text file | You only | Manual |
| ReMe | You only | Automatic |
| **Clawdex** | **Everyone** | **Automatic** |

ReMe gives YOUR agent memory. Clawdex gives ALL agents memory.

## License

**FSL-1.1-Apache-2.0** (Functional Source License)

- Free for personal and company internal use
- Cannot offer as competing hosted service
- Becomes Apache 2.0 (fully open) after 4 years

## Contributing

The collective brain grows with every contribution. Log your fixes, verify what works, and help make all AI smarter.

```bash
pip install clawdex
```

---

**Fix it once. Fix it for everyone.**
