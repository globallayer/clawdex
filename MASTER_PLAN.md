# vault404 Master Pivot Plan

> From AI coding memory tool → **AI vulnerability intelligence platform**

---

## The Repositioning

**Old:** "Collective intelligence for AI coding agents"

**New:** "The live intelligence feed for AI-discovered vulnerabilities — found by AI, fixed by the community, never forgotten"

The 404 name now has a double meaning: **the vulnerability that was not found until AI caught it.**

---

## Domain

- **Frontend:** https://vault404.dev
- **Backend API:** Railway (existing)
- **Database:** Supabase (existing)

---

## Phase 1: Backend Pivot (Weeks 1-2)

**Goal:** Make the codebase speak the language of security

### 1.1 Schema Changes

Add `VulnerabilityReport` model with fields:
- `vuln_type` — SQLi, XSS, SSRF, RCE, IDOR, Path Traversal, etc.
- `severity` — Critical / High / Medium / Low
- `language` — python, typescript, go, rust, etc.
- `framework` — express, fastapi, nextjs, django, etc.
- `pattern_snippet` — redacted vulnerable code pattern
- `fix_snippet` — redacted fix pattern
- `disclosure_status` — open / patched / mitigated
- `reported_by_agent` — Claude / GPT / Cursor / Aider / etc.
- `verified_count` — community verification count
- `timestamp` — when discovered
- `disclosure_delay` — 72h delay for unpatched vulns (responsible disclosure)

### 1.2 New API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/vulns/report` | POST | Submit a vulnerability finding |
| `/api/v1/vulns/feed` | GET | Live feed of recent vulnerabilities |
| `/api/v1/vulns/stats` | GET | Total found, patched, top types this week |
| `/api/v1/vulns/search` | GET | Semantic search for similar vulns |
| `/api/v1/vulns/:id/verify` | POST | Verify a fix works |

### 1.3 MCP Tool Updates

| Tool | Purpose |
|------|---------|
| `report_vulnerability` | Auto-log vulns during scan session |
| `find_similar_vuln` | Search vuln database before writing code |
| `verify_vuln_fix` | Confirm a fix works |
| `get_vuln_stats` | Dashboard stats |

### 1.4 Security/Redaction

Extend `redactor.py` to strip:
- File paths
- Repo names
- Variable names
- Company/project identifiers
- Keep only the vulnerability pattern shape

---

## Phase 2: vault404.dev Frontend (Weeks 2-4)

**Goal:** A public face that proves the project is alive and growing

### 2.1 Homepage — Live Intelligence Dashboard

**Above the fold:**
- Live counter: `[X] vulnerabilities found / [X] patched / [X] AI agents contributing`
- Rolling live feed (last 24h): "XSS via unsanitized innerHTML — React — High — Fixed 6 times — 2h ago"
- Single CTA: "Connect your AI agent →"

**Below the fold:**
- How it works (3 steps: AI finds it → vault logs it → community fixes it)
- Severity breakdown chart (donut: Critical/High/Medium/Low)
- Top vulnerability types this month
- Agent leaderboard (which AI agents contribute most)
- Install block: `pip install vault404`

### 2.2 Tech Stack

**Option A (Faster):**
- Framer for design + marketing
- Custom code embeds for live API data

**Option B (More control):**
- Next.js single page
- Direct API calls to Railway backend
- WebSocket or polling for live feed

### 2.3 Key UI Elements

- Live feed component (WebSocket or 30s polling)
- Severity badge colours (Critical=red, High=orange, Medium=yellow, Low=blue)
- Agent icons (Claude, GPT, Cursor logos)
- Redacted pattern preview (shows shape without exposing code)
- "Verified X times" social proof counter

---

## Phase 3: Content Seeding & Social Proof (Weeks 3-5)

**Goal:** Make the dashboard look alive before anyone else contributes

### 3.1 Legitimate Self-Seeding

1. Run Claude Code in scan mode on 5-10 public open-source repos:
   - Express.js boilerplates
   - FastAPI starters
   - React templates
   - Django projects
   - Next.js examples

2. Log every real vulnerability as a `VulnerabilityReport`

3. For each finding: open a GitHub issue on the affected repo crediting vault404
   - Creates backlinks
   - Builds visibility in open-source community
   - Establishes credibility

### 3.2 "State of AI Vulnerability Discovery" Report

After 2-3 weeks of scanning, compile findings:
> "AI agents scanned 10 popular open-source repos in 72 hours and found X vulnerabilities humans missed"

Publish on vault404.dev blog (or Notion page initially)

This becomes launch content.

---

## Phase 4: Launch & Distribution (Weeks 5-6)

### Day 1 — GitHub
- Update vault404 README with security-first positioning
- Submit to `awesome-mcp-servers`
- Submit to `awesome-claude` list

### Day 2 — Reddit
- r/netsec: "I built a shared vulnerability intelligence layer for AI coding agents — here's what it found scanning 10 popular repos"
- r/ClaudeAI + r/cursor: "vault404 now logs security vulnerabilities your AI agent finds — live feed at vault404.dev"
- r/SideProject: Honest builder story

### Day 3 — X/Twitter
- Thread: "AI agents are finding vulnerabilities faster than humans can patch them. I built something to fix the other half of that problem..."
- Tag: @AnthropicAI @cursor_ai @swyx @GergelyOrosz
- Post specific finding: "Claude found this SQL injection pattern in [repo] in 4 minutes..."

### Day 4 — Hacker News
- "Show HN: vault404 – Shared vulnerability intelligence for AI coding agents"
- Lead comment: specific findings, responsible disclosure approach, live dashboard link
- Timing: Tuesday-Thursday, 9am-12pm US Eastern

### Day 5 — Security Community
- Submit to daily.dev
- Post in OWASP Slack/Discord
- DEV.to article: "What happens when you let Claude scan open-source repos for vulnerabilities for a week"

---

## Phase 5: Monetisation (Month 2-3)

**Don't monetise yet — grow first. But set the architecture.**

### Free Tier (Forever)
- Public feed access
- Up to 50 vulnerability submissions/month
- MCP integration

### Pro Tier (~$19/month)
- Unlimited submissions
- Private vault (findings don't go to community brain)
- Priority in feed ranking
- CSV/JSON export

### API Tier (~$99/month)
- Bulk API access for teams
- Webhook on new matching vulnerabilities
- Custom severity filters
- White-label feed embed

---

## Marketing Strategy — Ongoing

### Content Pillars (2-3x per week)

1. **"AI found this"** — specific, anonymised finding with the fix
2. **"Did you know"** — educational posts about vuln types tied to vault patterns
3. **Builder updates** — honest progress posts with real numbers

### Channels by Priority

| Channel | Why | Effort |
|---------|-----|--------|
| X/Twitter | Security + AI dev overlap | Medium |
| Hacker News | One good Show HN = thousands of installs | Low |
| r/netsec + r/ClaudeAI | Direct audiences | Low |
| DEV.to articles | SEO + developer trust | Medium |
| GitHub SEO | Searchable forever | Low |
| YouTube (later) | "I scanned X repos with AI" videos | High — Month 3 |

---

## The Unfair Advantage

> "I'm not a developer. I built an AI that finds security vulnerabilities, and I made the knowledge shareable. Here's what it found."

This narrative is more interesting to mainstream tech media than another security tool from a pen tester.

---

## 30/60/90 Day Targets

| Milestone | Target | How |
|-----------|--------|-----|
| Day 30 | vault404.dev live + 200 real vuln entries | Self-seeding via scanning |
| Day 30 | 50 GitHub stars | Reddit + HN launch |
| Day 60 | 10 external contributors | MCP tool adoption |
| Day 60 | 500 vuln entries | Community + scanning |
| Day 90 | 1 piece of press coverage | DEV.to + HN traction |
| Day 90 | First paid Pro user | Soft launch pricing |

---

## Immediate Next Actions (This Week)

- [ ] Update vault404 README with security-first positioning
- [ ] Add `VulnerabilityReport` model to `models.py`
- [ ] Add new API endpoints to `routes.py`
- [ ] Add `report_vulnerability` MCP tool
- [ ] Start scanning 3 public repos with Claude Code
- [ ] Start building vault404.dev (Framer or Next.js)
- [ ] Compile first findings into launch post

---

**The codebase is ready. The domain is bought. Now it's execution.**
