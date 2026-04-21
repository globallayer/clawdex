# vault404 - Roadmap

> **The live intelligence feed for AI-discovered vulnerabilities**
> Found by AI, fixed by the community, never forgotten.

---

## Vision

Build the definitive vulnerability intelligence platform powered by AI agents. Every vulnerability an AI finds gets logged, shared, and learned from — so no AI agent ever misses the same pattern twice.

**The 404 meaning:** The vulnerability that was not found until AI caught it.

---

## Phase 0: Foundation (COMPLETE)

**Goal:** Working infrastructure for AI coding memory

- [x] Core Python library with local storage
- [x] REST API deployed to Railway
- [x] MCP server for Claude Code integration
- [x] Python SDK on PyPI
- [x] JavaScript SDK on NPM
- [x] Semantic search with embeddings
- [x] Community brain with seeded patterns
- [x] API authentication and rate limiting
- [x] CI/CD pipeline with security scanning
- [x] Silent automatic operation
- [x] Auto-sync to community brain

**Status:** Complete. Infrastructure ready for pivot.

---

## Phase 1: Backend Pivot (Weeks 1-2) — IN PROGRESS

**Goal:** Transform codebase to speak the language of security

### 1.1 Vulnerability Schema
- [ ] Add `VulnerabilityReport` model
- [ ] Severity levels (Critical/High/Medium/Low)
- [ ] Vulnerability types (SQLi, XSS, SSRF, RCE, IDOR, etc.)
- [ ] Disclosure status tracking (open/patched/mitigated)
- [ ] 72-hour responsible disclosure delay for unpatched vulns
- [ ] Agent attribution (which AI found it)

### 1.2 API Endpoints
- [ ] `POST /api/v1/vulns/report` — submit findings
- [ ] `GET /api/v1/vulns/feed` — live vulnerability feed
- [ ] `GET /api/v1/vulns/stats` — dashboard statistics
- [ ] `GET /api/v1/vulns/search` — semantic search
- [ ] `POST /api/v1/vulns/:id/verify` — verify fixes

### 1.3 MCP Tools
- [ ] `report_vulnerability` — auto-log during scans
- [ ] `find_similar_vuln` — check before writing code
- [ ] `verify_vuln_fix` — confirm fix works
- [ ] `get_vuln_stats` — dashboard data

### 1.4 Enhanced Redaction
- [ ] Strip file paths from patterns
- [ ] Strip repo/project names
- [ ] Strip variable names
- [ ] Keep only vulnerability shape

**Success Metrics:**
- All new endpoints operational
- MCP tools functional in Claude Code
- Redaction working for all vuln patterns

---

## Phase 2: vault404.dev Frontend (Weeks 2-4)

**Goal:** Public face that proves the project is alive

### 2.1 Live Dashboard Homepage
- [ ] Real-time vulnerability counter
- [ ] Rolling feed of recent findings (24h)
- [ ] Severity breakdown chart
- [ ] Top vulnerability types this month
- [ ] Agent leaderboard
- [ ] "Connect your AI agent" CTA

### 2.2 Technical Implementation
- [ ] Domain setup (vault404.dev)
- [ ] Framer or Next.js build
- [ ] WebSocket or polling for live data
- [ ] Severity badge styling
- [ ] Redacted pattern preview component

### 2.3 Marketing Pages
- [ ] How it works (3-step flow)
- [ ] Installation guide
- [ ] API documentation
- [ ] Blog/updates section

**Success Metrics:**
- Site live at vault404.dev
- Live data flowing from API
- < 3 second page load

---

## Phase 3: Content Seeding (Weeks 3-5)

**Goal:** Make the dashboard look alive with real data

### 3.1 Public Repo Scanning
- [ ] Scan 10 popular open-source repos
- [ ] Log all real vulnerabilities found
- [ ] Open GitHub issues on affected repos
- [ ] Create backlinks and visibility

### 3.2 Launch Content
- [ ] "State of AI Vulnerability Discovery" report
- [ ] Compile 2-3 weeks of findings
- [ ] Publish on vault404.dev blog
- [ ] Prepare social media assets

**Success Metrics:**
- 200+ vulnerability entries
- 10+ GitHub issues opened
- Launch report published

---

## Phase 4: Launch & Distribution (Weeks 5-6)

**Goal:** Get vault404 in front of the right audiences

### 4.1 GitHub
- [ ] Update README with security positioning
- [ ] Submit to awesome-mcp-servers
- [ ] Submit to awesome-claude
- [ ] 50 stars target

### 4.2 Reddit
- [ ] r/netsec post (lead with findings)
- [ ] r/ClaudeAI post
- [ ] r/cursor post
- [ ] r/SideProject builder story

### 4.3 X/Twitter
- [ ] Launch thread
- [ ] Tag relevant accounts
- [ ] Share specific findings

### 4.4 Hacker News
- [ ] "Show HN" submission
- [ ] Prepared lead comment
- [ ] Optimal timing (Tue-Thu, 9am-12pm ET)

### 4.5 Security Community
- [ ] OWASP Slack/Discord
- [ ] daily.dev submission
- [ ] DEV.to article

**Success Metrics:**
- 50+ GitHub stars
- HN front page (ideally)
- 10+ external contributors

---

## Phase 5: Monetisation (Month 2-3)

**Goal:** Sustainable revenue without killing growth

### 5.1 Free Tier (Forever)
- Public feed access
- 50 submissions/month
- MCP integration

### 5.2 Pro Tier (~$19/month)
- Unlimited submissions
- Private vault option
- Priority feed ranking
- CSV/JSON export

### 5.3 API Tier (~$99/month)
- Bulk API access
- Webhooks on matches
- Custom severity filters
- White-label embed

### 5.4 Implementation
- [ ] Stripe integration
- [ ] Usage tracking
- [ ] Tier enforcement
- [ ] Billing portal

**Success Metrics:**
- First paid user
- $500 MRR by Month 3

---

## Phase 6: Scale (Month 3+)

**Goal:** Become the definitive vulnerability intelligence source

### 6.1 Content
- [ ] 1000+ vulnerability entries
- [ ] Weekly "AI Found This" posts
- [ ] YouTube: "I let AI scan repos for a week"
- [ ] Press/media coverage

### 6.2 Integrations
- [ ] VS Code extension
- [ ] Cursor native integration
- [ ] GitHub Action for CI/CD
- [ ] LangChain tool package

### 6.3 Enterprise
- [ ] Team spaces
- [ ] SSO integration
- [ ] Compliance documentation
- [ ] Self-hosted option

**Success Metrics:**
- 1000+ weekly active users
- 10+ integrations
- Enterprise pipeline started

---

## 30/60/90 Day Targets

| Day | Target |
|-----|--------|
| 30 | vault404.dev live + 200 vuln entries + 50 GitHub stars |
| 60 | 10 external contributors + 500 vuln entries |
| 90 | First paid user + press coverage + 1000 entries |

---

## Non-Goals (Out of Scope)

- Building a general-purpose AI assistant
- Competing with Snyk/Semgrep (we're complementary)
- Storing actual source code
- Manual vulnerability research (AI-first only)

---

## Success Principles

1. **AI-First** — Built for AI agents, not human researchers
2. **Live Data** — Real-time feed, not static database
3. **Responsible Disclosure** — 72h delay on unpatched vulns
4. **Privacy** — Never share actual code, only patterns
5. **Community** — Open source, shared learning

---

## The Unfair Advantage

> "I'm not a developer. I built an AI that finds security vulnerabilities, and I made the knowledge shareable."

This narrative is more interesting than another security tool from a pen tester. Own it.
