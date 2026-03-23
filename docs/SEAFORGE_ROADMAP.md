# Arne's Ecosystem — Architecture, Roadmap & Development Guide

**Owner:** Arne Verboom (GitHub: Flyntrea) | **Updated:** 2026-03-14
**Status:** Living document — feed sections into CLAUDE.md, AGENTS.md, and workspace configs

> This document covers the complete development ecosystem: the private AI assistant infrastructure (OpenClaw + Mission Control) and the public open-source maritime platform (SeaForge). These are separate projects with a shared knowledge boundary.

---

## 1. The Split: What's Private, What's Public

This is the most important architectural boundary in the ecosystem. Everything flows from this distinction.

```
PRIVATE (your tools, your data, your agents)
├── OpenClaw         ~/projects/openclaw/        AI agent runtime
├── Mission Control  ~/projects/mission-control/  React dashboard
├── Agent Workspaces ~/.openclaw/workspace[-*]/   Persona, memory, skills
└── CLAUDE.md        Session config for AI tools

PUBLIC (open-source, community-facing)
└── SeaForge         ~/projects/seaforge/         Maritime training platform
    └── GitHub: Seaforge/platform (MIT license)
```

**The bridge:** Popeye's workspace (`~/.openclaw/workspace-popeye/`) contains 2.8MB of maritime reference material — 54 modules, COLREGS.md, CTRB study guide. SeaForge's training content (98 scenarios, lights database) *originates from* this workspace but is exported as standalone data. SeaForge never calls OpenClaw. OpenClaw never depends on SeaForge. They share knowledge, not infrastructure.

**Why this matters:** When contributing to SeaForge publicly, nothing from the private stack leaks. No gateway tokens, no agent configs, no Supabase keys, no personal MEMORY.md content. The `.gitignore` and repo boundaries enforce this, but the mental model must be clear first.

---

## 2. Architecture Overview

### 2.1 System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      USER (Arne)                            │
│   Telegram (@Jarvi01bot)  │  Browser  │  Claude Code CLI    │
└────────┬──────────────────┴─────┬─────┴─────────────────────┘
         │                        │
         ▼                        ▼
┌────────────────────┐   ┌────────────────────────────────┐
│  OpenClaw Gateway  │   │      Mission Control           │
│  :18789 (WS v3)    │   │  :5174 (React/Vite)            │
│  systemd service    │◄──│  :5175 (local-api.mjs)         │
│                     │   │  Supabase (state persistence)  │
│  Agents:            │   └────────────────────────────────┘
│  ├─ Jarvis (main)   │          │
│  ├─ Atlas (code)    │          │ POST /api/agent/message
│  ├─ Popeye (maritime)│◄─────────┘ (proxied via local-api
│  ├─ OPS (admin)     │            → npx openclaw agent ...)
│  ├─ IRIS (design)   │
│  └─ SCOUT (personal)│
│                     │
│  Models:            │   ┌────────────────────────────────┐
│  Gemini (primary)   │   │        SeaForge               │
│  OpenRouter (free)  │   │  :5000 (Flask + Docker)        │
│  Claude (fallback)  │   │  MIT License, public repo      │
│  Ollama (local)     │   │  Maritime training + intel     │
└─────────────────────┘   │  Standalone — no OpenClaw dep  │
                          └────────────────────────────────┘
```

### 2.2 Data Flow

Messages arrive through Telegram, get routed by the gateway to the correct agent workspace, processed by Gemini/Claude, and returned. Mission Control connects via WebSocket to the gateway and via REST to local-api.mjs, which bridges the filesystem and CLI. SeaForge runs in its own Docker container, completely independent. Supabase syncs Mission Control state across sessions. Claude Code CLI is the expensive last resort for complex architecture decisions.

### 2.3 Cost Model

The ecosystem is designed around a hard constraint: 80% free models, Claude only as fallback.

| Tier | Models | Use Case | Cost |
|------|--------|----------|------|
| Primary | Gemini 2.5 Pro/Flash | Coding, content, general | Free |
| Bulk | OpenRouter free tier (Nemotron, Step Flash, Trinity) | Admin, cron, low-stakes | $0 |
| Local | Ollama (llama3.2, nomic-embed, qwen3-coder) | Private inference, embeddings | $0 |
| Fallback | Claude Sonnet 4.6 via OpenRouter | Code review, architecture | Paid |
| Last resort | Claude Opus 4.6 via CLI | Critical decisions only | Expensive |

This isn't just budget optimization — it's architectural resilience. If Anthropic's API goes down or pricing changes, the core system keeps running on Gemini and local models.

---

## 3. OpenClaw — Private AI Agent Runtime

### 3.1 What It Is

A local-first, multi-channel AI assistant runtime. Six agents, each with dedicated workspaces, routed through a single WebSocket gateway. Runs as a systemd user service on WSL2 Ubuntu (host: Boomski).

### 3.2 Agent Fleet

| Agent | Workspace | Model | Role |
|-------|-----------|-------|------|
| Jarvis (Clawdia) | `~/.openclaw/workspace/` | Gemini 2.5 Flash | The Orchestrator — main brain on Telegram |
| Atlas | `workspace-atlas/` | Gemini 2.5 Pro (primary), Claude Sonnet (fallback) | Code Architect — engineering tasks |
| Popeye | `workspace-popeye/` | Gemini 2.5 Pro | Chief Officer — maritime knowledge, COLREGS, SAR, GMDSS. 2.8MB reference material, 54 modules |
| OPS | `workspace-ops/` | Nemotron Nano (free) | Admin — scheduling, paperwork |
| IRIS | `workspace-iris/` | Gemini 2.5 Flash | Design tasks |
| SCOUT | `workspace-scout/` | Gemini 2.5 Flash | Personal tasks |

### 3.3 Workspace Anatomy

Every agent workspace follows the same structure:

```
~/.openclaw/workspace[-name]/
├── SOUL.md          # Persona, tone, boundaries
├── IDENTITY.md      # Name, emoji, vibe
├── AGENTS.md        # Instructions + operational memory
├── TOOLS.md         # Tool usage notes
├── USER.md          # User profile
├── skills/          # Per-agent skill definitions
├── knowledge/       # Domain knowledge files
├── docs/            # Reference documents
└── references/      # External reference material
```

Popeye's workspace is the densest, containing the full maritime knowledge base that also feeds SeaForge's training content.

### 3.4 Gateway Configuration

Key settings in `~/.openclaw/openclaw.json`:

- Port 18789, loopback bind, token auth
- Control UI allows localhost:5174 (Mission Control) and Tailscale origins
- `dangerouslyDisableDeviceAuth: true` (simplifies local dev, tighten for VPS)
- 4 model providers: Google (Gemini), OpenRouter (13 models), Ollama (local), Anthropic (fallback)

### 3.5 Current Pain Points & Improvement Areas

**Auth complexity.** The 3-tier auth system (token → device → channel) has caused repeated lockouts. The `dangerouslyDisableDeviceAuth` flag is a workaround, not a solution. Before VPS deployment, either properly implement device pairing or replace with a simpler auth scheme (e.g., Tailscale identity + single token).

**Agent routing clarity.** With 6 agents, it's not always obvious which agent should handle a given task. Mission Control's agent assignment UI helps, but the gateway itself doesn't have smart routing. Consider adding a lightweight triage layer — Jarvis receives all messages and delegates to specialists, rather than requiring the user to pick an agent.

**Session persistence.** Sessions are JSONL files in `~/.openclaw/agents/<id>/sessions/`. This works but isn't searchable. Consider indexing sessions into SQLite or using Ollama's nomic-embed for semantic search over past conversations.

**Workspace drift.** Six agent workspaces means six SOUL.md files, six AGENTS.md files, six sets of instructions to keep consistent. Establish a workspace template and a sync script that propagates shared conventions (commit style, cost rules, file conventions) while preserving per-agent specialization.

---

## 4. Mission Control — Private Dashboard

### 4.1 What It Is

A React dashboard (Vite + Tailwind v4 + Zustand + Supabase) that serves as the unified control panel. Three servers required: Vite dev (5174), local API (5175), and OpenClaw gateway (18789).

### 4.2 View Architecture (23 views)

**Primary:** Home (dashboard), Calendar, Goals (OKR), Kanban, Memory (Jarvis logs + Claude Code sessions), Chat (Jarvis WebSocket)

**Maritime:** Sea Mode (Beaufort/weather), CVC Map, COLREGS, Watch Log, Timezones

**Management:** Agents (task assignment + execution), Models (routing rules + cost tracking), System (disk/git), Roadmap, Channels, Gateway status, Settings

### 4.3 State Management

16 Zustand stores backed by Supabase (PostgreSQL with RLS) for persistence and localStorage for transient state. Key stores: agentStore, taskSlice, kanbanSlice, calendarSlice, goalStore, modelStore, gatewaySlice.

### 4.4 Improvement Areas

**Three-server startup.** Currently requires manually starting Vite, local-api.mjs, and OpenClaw gateway. Create a single launcher script (or a `docker-compose.dev.yml`) that brings up all three with health checks.

**Local API as bottleneck.** The local-api.mjs bridges everything — filesystem reads, CLI proxying, Google Calendar/Tasks via gog CLI. As complexity grows, this single file will become hard to maintain. Consider splitting into route modules or migrating to a lightweight framework (Fastify, Hono) with proper error handling.

**Supabase dependency.** If Supabase is unreachable, Mission Control loses state sync. Consider implementing an offline-first pattern: write to localStorage immediately, sync to Supabase when available. Zustand's `persist` middleware supports this, but it needs to be wired to Supabase's realtime as the source of truth.

**Maritime views overlap.** The Sea Mode, CVC Map, COLREGS, and Watch Log views in Mission Control overlap with SeaForge's functionality. Clarify the boundary: Mission Control's maritime views are *personal operational tools* (your watch, your vessel, your weather). SeaForge's maritime features are *training and intelligence tools* (scenario practice, fleet tracking, competency assessment). Don't duplicate the map — consider embedding SeaForge's chart view via iframe or shared component library if they converge further.

---

## 5. SeaForge — Open-Source Maritime Platform

### 5.1 What It Is

An open-source, self-hosted maritime intelligence and training platform. Flask backend, SQLite database, Leaflet.js chart display with dark nautical theme. Runs as a single Docker container on port 5000.

**GitHub:** `Seaforge/platform` (public, MIT license)

### 5.2 Current State (v0.1)

The chart view shows a dark-themed Leaflet map centered on the southern North Sea (Blankenberge/Zeebrugge area) displaying live AIS vessel targets with heading indicators, TSS zones, weather data overlay (wind 16.9kts S Bft 4, air 6.6°C, pressure 1005.3 hPa, waves 0.7m), and toggleable layers for nautical marks, bathymetry, rain radar, sea temperature, waves/swell, currents, protected areas, and EEZ boundaries. Navigation bar includes Chart, COLREGS, Fleets, Wellbeing, Tasks, Lights, Drills, Anchor, and MOB modules.

The platform already has substantial functionality across 4 core modules, 98 COLREGS training scenarios, 39 API endpoints, and 12 SQLite tables.

### 5.3 Architecture

```
seaforge/
├── src/
│   ├── core/
│   │   ├── colregs.py      # Encounter classification (Rules 13-15), CPA/TCPA
│   │   ├── ais.py           # aisstream.io WebSocket integration
│   │   ├── mob.py           # MOB drift, search patterns, GMDSS 19-step
│   │   └── nmea.py          # NMEA 0183 / Signal K fallback
│   ├── data/
│   │   └── lights_db.py     # 98 scenario database (10 categories × 3 levels)
│   ├── routes/              # Flask blueprints (39 endpoints)
│   │   ├── navigation.py    # /api/colregs, /api/fleet, /api/lights, /api/ais/*
│   │   ├── training.py      # /api/training/colregs-scores, /api/training/ctrb
│   │   ├── wellbeing.py     # /api/wellbeing/rest-hours, workouts, meals, mood
│   │   └── ops.py           # /api/ops/tasks, watch-log, voyage-log
│   └── static/              # Leaflet, vanilla JS, dark nautical CSS
├── docs/
│   └── TRAINING_PLATFORM_PLAN.md
├── docker-compose.yml
├── Dockerfile
└── README.md
```

### 5.4 Monetization Strategy

1. **Free tier:** COLREGS quiz engine (static site, PWA, offline-first) — the gateway
2. **Content expansion:** Sound signals, GMDSS, SMCP, case studies
3. **Premium ($9/mo):** AI tutor, assessment mode, competency radar, CTRB tracker
4. **Academy ($199/yr):** User accounts, multi-language, LMS API integration

### 5.5 Architecture Improvements

**Separate API from rendering.** Currently Flask serves both the API and the frontend. For the PWA/offline-first goal, extract the frontend into a standalone build (Vite + vanilla JS or lightweight framework) that consumes the API. This also enables deploying API and frontend independently — static frontend on a CDN, API on a small VPS.

**AIS WebSocket resilience.** The aisstream.io connection is a single point of failure for the chart view. Implement reconnection logic with exponential backoff, and add a "last updated" indicator so users know when data is stale. Consider NMEA fallback for shipboard deployment where direct AIS feed is available.

**COLREGS engine validation.** The encounter classification and CPA/TCPA computation are safety-adjacent. They should have a comprehensive test suite with known-good scenarios. If SeaForge is used for training, incorrect scenario classification is a liability. Add `tests/test_colregs.py` with at least 20 validated encounters.

**Database migration strategy.** SQLite with 12 tables and no ORM is pragmatic for v0.1, but adding columns or tables without migrations is fragile. Add a simple migration runner (numbered SQL files applied in order) before the schema grows further.

**API documentation.** 39 endpoints need documentation. Use Flask-RESTX or generate an OpenAPI spec. This is especially important for the premium tier — an AI tutor or LMS integration will consume these endpoints programmatically.

**Docker optimization.** The image should be multi-stage (build dependencies in stage 1, runtime in stage 2) to keep it small. Add a health check endpoint (`/api/health`) and wire it into docker-compose.

---

## 6. Popeye — The Knowledge Bridge

Popeye deserves its own section because it sits at the intersection of private and public.

### 6.1 Dual Role

**As an OpenClaw agent** (private): Popeye is the Chief Officer agent with a 2.8MB workspace — 54 modules covering COLREGS, SAR, GMDSS, and the full CTRB study guide. Runs on Gemini 2.5 Pro, answers maritime questions in context.

**As SeaForge's knowledge source** (public): The 98 training scenarios, the lights database, and the COLREGS classification logic all originate from Popeye's workspace. But they're exported as standalone Python data structures in SeaForge's codebase — no runtime dependency on OpenClaw.

### 6.2 Knowledge Sync Protocol

When Popeye's workspace is updated, changes need to flow to SeaForge as a deliberate export, not automatic sync:

1. Update Popeye's workspace files in `~/.openclaw/workspace-popeye/`
2. Validate changes via Popeye agent (ask it to test the new knowledge)
3. Export relevant data to `~/projects/seaforge/src/data/`
4. Commit to SeaForge repo with attribution (`feat: add 12 TSS scenarios from Popeye workspace`)
5. Never commit Popeye's raw workspace files to SeaForge — only curated exports

### 6.3 Module Expansion Priorities

Based on STCW II/1 competency requirements and the training platform plan:

| Priority | Module Area | Current State | Gap |
|----------|-------------|---------------|-----|
| 1 | COLREGS (Rules 1-38) | 54 modules, 98 scenarios | Good coverage, needs edge cases |
| 2 | GMDSS | Basic procedures in mob.py | Needs full DSC, SART, EPIRB, NAVTEX modules |
| 3 | SMCP | Not started | Standard Marine Communication Phrases — required for STCW |
| 4 | Cargo handling | Not started | Relevant for HMC heavy lift operations |
| 5 | Stability & trim | Not started | Fundamental OOW competency |
| 6 | MARPOL compliance | Referenced in roadmap docs | Needs structured modules per Annex |
| 7 | Emergency procedures | Not started | Fire, flooding, abandon ship, SAR coordination |

---

## 7. Development Roadmap

### Phase 1 — Stabilization (Weeks 1–4)

**Goal:** Make the existing three-project stack reliable and well-documented.

**OpenClaw hardening**
- [ ] Create single launcher script: `~/scripts/start-all.sh` (systemd openclaw-gateway + Mission Control vite + local-api.mjs)
- [ ] Audit `~/.openclaw/openclaw.json` — remove unused model configs, document active ones
- [ ] Establish workspace template for shared conventions across 6 agents
- [ ] Write `~/.openclaw/workspace/TOOLS.md` documenting all available tools per agent
- [ ] Test Tailscale remote access from mobile (simulate ship connectivity)

**Mission Control cleanup**
- [ ] Document all 23 views in a `VIEWS.md` — what each does, data sources, known issues
- [ ] Fix any broken Supabase sync (verify RLS policies)
- [ ] Add error boundaries to prevent single-view crashes from taking down the dashboard
- [ ] Implement offline-first localStorage fallback for critical stores

**SeaForge quality**
- [ ] Write `tests/test_colregs.py` — minimum 20 validated encounter scenarios
- [ ] Add `/api/health` endpoint for Docker health checks
- [ ] Document all 39 API endpoints (even a simple `API.md` with method/path/description)
- [ ] Add SQLite migration runner (numbered `.sql` files in `migrations/`)
- [ ] Ensure README has clear setup instructions for new contributors

**Cross-cutting**
- [ ] Rotate all credentials (gateway token, Telegram bot token, API keys)
- [ ] Audit all `.gitignore` files — verify no credentials can be staged
- [ ] Tag current state: OpenClaw v0.1.0, Mission Control v0.1.0, SeaForge v0.1.0
- [ ] Update CLAUDE.md to reflect the accurate three-project architecture

### Phase 2 — SeaForge Public Launch (Weeks 5–10)

**Goal:** Make SeaForge ready for public use and early adopter feedback.

**Frontend extraction (Weeks 5–6)**
- [ ] Extract frontend from Flask into standalone Vite build
- [ ] Implement PWA manifest + service worker for offline COLREGS quizzes
- [ ] Optimize Leaflet map: lazy-load layers, compress tile requests
- [ ] Add responsive design for tablet/mobile (bridge tablet use case)

**Training engine (Weeks 7–8)**
- [ ] Build quiz mode: timed COLREGS scenarios with scoring
- [ ] Add progress tracking: per-category completion percentage
- [ ] Implement spaced repetition for weak categories
- [ ] Add visual scenario renderer (SVG vessel positions on mini-chart)

**Content expansion (Weeks 9–10)**
- [ ] Export 15+ new scenarios from Popeye workspace (GMDSS, sound signals)
- [ ] Add SMCP module: basic phrases for bridge communications
- [ ] Create "scenario of the day" feature for homepage
- [ ] Write content contributor guide for external maritime professionals

**Community readiness**
- [ ] Add CONTRIBUTING.md, CODE_OF_CONDUCT.md, issue templates
- [ ] Set up GitHub Actions: lint, test, Docker build on PR
- [ ] Create project board for public issue tracking
- [ ] Write launch announcement for maritime communities

### Phase 3 — Infrastructure & VPS (Weeks 11–16)

**Goal:** Move from laptop-dependent to 24/7 remote-accessible operation.

**VPS deployment (Weeks 11–12)**
- [ ] Provision VPS (Ubuntu 24.04, 1 vCPU, 2GB RAM)
- [ ] Deploy OpenClaw gateway as systemd service on VPS
- [ ] Deploy SeaForge Docker container on VPS
- [ ] Set up nginx reverse proxy + Let's Encrypt HTTPS
- [ ] Configure UFW (Tailscale + SSH only), fail2ban

**Tailscale mesh (Week 13)**
- [ ] VPS ↔ Laptop ↔ Phone mesh
- [ ] Mission Control accessible via Tailscale from anywhere
- [ ] Telegram bot running from VPS (always-on)
- [ ] Test from mobile hotspot: simulate ship satellite connectivity

**Monitoring & automation (Weeks 14–16)**
- [ ] Heartbeat: 30min Telegram check-in from Jarvis
- [ ] Daily morning briefing cron (07:00 — weather, calendar, priority tasks)
- [ ] Monthly security rotation reminder
- [ ] SeaForge uptime monitoring (simple HTTP check → Telegram alert)
- [ ] Automated VPS backup (daily snapshot or rsync to offsite)

### Phase 4 — Popeye Expansion & Premium Prep (Weeks 17–24)

**Goal:** Expand Popeye's knowledge base and build SeaForge's premium features.

**Popeye modules (Weeks 17–20)**
- [ ] Complete GMDSS module: DSC, SART, EPIRB, NAVTEX procedures
- [ ] Build SMCP module: all standard bridge communication phrases
- [ ] Build stability module: basic trim and stability concepts for OOW
- [ ] Build emergency procedures module: fire, flooding, abandon ship
- [ ] Export all new content to SeaForge training database

**SeaForge premium (Weeks 21–24)**
- [ ] User accounts (Supabase Auth or simple JWT)
- [ ] CTRB tracker: digital Cadet Training Record Book
- [ ] AI tutor: integrate Popeye's knowledge via API (Gemini-powered, not OpenClaw-dependent)
- [ ] Assessment mode: timed exams with pass/fail criteria matching STCW standards
- [ ] Competency radar: visual progress across all STCW II/1 functions

### Phase 5 — HMC Preparation & Research (Months 7+)

**Goal:** Leverage the ecosystem for professional development and maritime innovation.

- [ ] Build HMC-specific Popeye module: Sleipnir/Thialf/Aegir operational parameters
- [ ] DP operations module: DP2/DP3 limits, environmental criteria, failure modes
- [ ] EU ETS calculation module: per-vessel, per-voyage compliance
- [ ] Heavy lift operations reference: crane capacities, lift planning basics
- [ ] DMON concept paper: formalize decentralized maritime operations idea
- [ ] MASS SMS framework: publish Safety Management System reference for autonomous vessels

---

### Future Development Possibilities & Integrations

- **OceanScrape region polygons**: [theSchaefer/OceanScrape](https://github.com/theSchaefer/OceanScrape) — The scraping approach itself is not suitable (pixel-based vessel detection, no MMSI/identity, ToS risk). However, `regions.py` contains **57 polygon-bounded maritime chokepoints** (Suez, Malacca, Panama, North Sea TSS, etc.) with zoom levels and tier classifications — a ready-to-use geographic dataset. Candidate use: pre-defined navigation zones or traffic hotspot layers on the SeaForge chart view. Also a strong candidate for WhaleGuardians: chokepoint polygons overlaid with whale habitat zones would directly support ship-strike risk analysis.

## 8. CLAUDE.md — Recommended Structure

Keep it under 2000 words. Dense, scannable, actionable. Context primer, not knowledge base.

```markdown
# CLAUDE.md — Arne's System Context

## Identity
- Maritime cadet (STCW II/2 Master Mariner cert), upcoming OOW at HMC
- GitHub: Flyntrea | Org: Seaforge
- Host: Boomski (WSL2 Ubuntu on Windows)

## Three Projects (keep them separate)
1. **OpenClaw** ~/projects/openclaw/ — private AI agent runtime
   - Gateway :18789, systemd service, 6 agents
   - Config: ~/.openclaw/openclaw.json
2. **Mission Control** ~/projects/mission-control/ — private React dashboard
   - :5174 (Vite) + :5175 (local-api.mjs) + Supabase
3. **SeaForge** ~/projects/seaforge/ — PUBLIC maritime platform (MIT)
   - :5000 (Flask + Docker), GitHub: Seaforge/platform
   - Never leaks private infrastructure details

## Cost Rules
- 80% free models: Gemini 2.5 Pro/Flash, OpenRouter free tier, Ollama local
- Claude = fallback ONLY for review/architecture/critical decisions
- Never default to Claude when Gemini can handle it

## Agent Fleet
Jarvis (main/Flash), Atlas (code/Pro), Popeye (maritime/Pro),
OPS (admin/free), IRIS (design/Flash), SCOUT (personal/Flash)

## Dev Rules
- Conventional commits: feat:, fix:, refactor: + Co-authored-by for AI
- No ORM: SeaForge = raw SQL on SQLite, Mission Control = Supabase client
- Agent commands: npx openclaw agent --agent <id> -m "msg" --json
- Pragmatic solutions only. No unnecessary abstractions. Ship fast.

## Current Sprint
[Update weekly]
```

### Anti-Patterns

**Don't dump everything into CLAUDE.md.** If Popeye has 54 modules, reference them by path, don't reproduce content.

**Don't use CLAUDE.md as a task list.** Tasks belong in Mission Control's Kanban or Jarvis's MEMORY.md.

**Don't let CLAUDE.md drift.** Schedule monthly review. If it describes architecture that no longer exists, it actively misleads every AI session that reads it.

---

## 9. Quality Standards

### 9.1 Commit Conventions

All three projects use Conventional Commits with AI co-author attribution:

```
feat: add GMDSS scenario set to training database

Co-authored-by: Claude <noreply@anthropic.com>
```

### 9.2 Code Standards

**SeaForge (Python):** Raw SQL, no ORM. Type hints on public functions. Docstrings on modules. Black formatter. pytest for tests.

**Mission Control (TypeScript/React):** Zustand for state. No class components. Tailwind v4 utilities. ESLint + Prettier.

**OpenClaw config (YAML/JSON5):** Hot-reloadable. Comments on non-obvious settings. Backup before editing.

### 9.3 Security

**Monthly audit checklist:**
- [ ] Review `~/.openclaw/openclaw.json` for stale configs
- [ ] Check all `.gitignore` files cover credential paths
- [ ] Verify Telegram bot `dmPolicy` setting
- [ ] Review Docker images for updates
- [ ] Check Supabase RLS policies
- [ ] Rotate gateway token, API keys quarterly

---

## 10. Failure Modes & Recovery

| Scenario | Detection | Recovery |
|----------|-----------|----------|
| OpenClaw gateway stops | No Telegram response | `systemctl --user start openclaw-gateway` |
| Token mismatch | `gateway closed (1008)` | Re-set token in openclaw.json, restart |
| Mission Control can't reach gateway | Dashboard disconnected | Check gateway status, verify port 18789 |
| Supabase unreachable | State not syncing | localStorage fallback keeps local state |
| SeaForge Docker down | Port 5000 unreachable | `docker compose up -d` in ~/projects/seaforge |
| aisstream.io disconnected | Stale AIS data | Automatic reconnect; check API key quota |
| Model API quota exhausted | Error responses | Fallback chain: Gemini → OpenRouter free → Ollama |
| VPS unreachable (post-migration) | No heartbeat | SSH via Tailscale, check systemd |
| Git credential leak | Sensitive files staged | `git reset HEAD <file>`, rotate immediately |

**Triage priority:** (1) Credential exposure → rotate first. (2) Telegram channel → must work. (3) Data persistence → verify backups. (4) Features → everything else.

---

## 11. Jarvis Tool Integrations

These are real-world capabilities wired into Jarvis via CLI tools in `~/scripts/` and agent skills. Other AI systems working on this ecosystem should know these exist — they're part of the daily operational loop.

### 11.1 Google Calendar (`~/scripts/gog`)

Jarvis has full read/write access to 6 Google Calendars via the `gog` CLI tool.

**Calendars:** Personal BOOM, Arne & Charlie, Polar trainingsresultaten, Polar trainingsdoelen, Feestdagen in België, Fasen van de maan

**Write aliases:** `charlie` (shared: meals, appointments), `personal` (workouts, deep work, keystones)

**Capabilities:** view agenda, create events, edit/move/copy/delete events, swap events between dates, search. ISO datetime format required. Mission Control syncs via local API endpoint `GET /api/google/calendar?days=30`.

**Jarvis playbook:** `~/.openclaw/workspace/CALENDAR_OPS.md`

### 11.2 Google Tasks (`~/scripts/gog tasks`)

Read/write Google Tasks. Served to Mission Control via `GET /api/google/tasks`.

### 11.3 Spotify (`spotify-cli`)

Full playback control: play/pause/skip/volume/search. Jarvis skill: say "play [song]", "pause", "volume 40%", etc. Requires a device to be "awake" (open Spotify on phone/PC first).

**Config:** `~/.config/spotify-cli/env` + `token-cache.json`

### 11.4 Polar Health Watch (`~/scripts/polar`)

Read-only health data from Polar AccessLink API: steps, calories, sleep quality, heart rate, training sessions. Jarvis includes this in morning briefings. "How did I sleep?" or "activity this week?" triggers it.

**Config:** `~/.config/polar/config.json` + `token.json`

### 11.5 Bring! Shopping List (`bring`)

Push items to shared Bring! shopping list. Jarvis uses the meal-planner skill to auto-generate shopping lists. **Items must always be in Dutch** (e.g. "Spinazie", not "Spinach").

**Config:** `~/.config/bring/config.json`

### 11.6 Cron Jobs & Automation

| Job | Schedule | Agent | What it does |
|-----|----------|-------|-------------|
| Heartbeat | Every 30 min | OPS | Telegram check-in, confirms gateway alive |
| Morning briefing | 07:00 daily | Jarvis | Weather, calendar, priority tasks, sleep data |
| Monthly model review | 1st of month, 10:17 | Jarvis | Research model rankings, suggest config changes (requires approval) |
| Evening memory curation | Nightly | Jarvis | Curate MEMORY.md from day's conversations |

### 11.7 Backup Procedures

**Quick backup** (secrets only, before risky changes):
```bash
tar -czf ~/backups/jarvis-backup-$(date +%Y-%m-%d_%H-%M-%S).tar.gz \
  ~/projects/openclaw/.env ~/.openclaw/openclaw.json \
  ~/.openclaw/agents/main/agent/auth-profiles.json \
  ~/.openclaw/identity/ ~/.openclaw/devices/ \
  ~/.config/polar/ ~/.config/bring/ ~/.config/spotify-cli/
```

**Full backup** (everything minus node_modules/.git/dist/logs):
```bash
tar -czf ~/backups/full-backup-$(date +%F).tar.gz \
  ~/projects/{openclaw,mission-control,seaforge} ~/.openclaw/ \
  ~/.config/{polar,bring,spotify-cli} \
  --exclude="*/node_modules" --exclude="*/dist" --exclude="*/.git" --exclude="*/logs"
```

**Copy to Windows:** `cp ~/backups/*.tar.gz /mnt/c/Users/HP/Documents/`

### 11.8 Troubleshooting Cheatsheet

| Symptom | Fix |
|---------|-----|
| Session context overflow (HTTP 400) | Archive `.jsonl`, set `sessionId: null` in sessions.json, restart gateway |
| Split-brain (workspace changes not picked up) | Clear BOTH `sessionId` AND `sessionFile` in sessions.json, archive stale .jsonl |
| Compaction hang (typing indicator, no reply) | Self-heals in 10 min. If urgent: archive session + clear pointer |
| Gateway reconnecting in Mission Control | Verify `dangerouslyDisableDeviceAuth: true` in openclaw.json, restart gateway |
| Gemini 3 Flash emoji spam | Known bug (2026-03-09). Switch to Gemini 2.5 series |

---

## 12. Metrics & Success Criteria

### Phase 1 (Stabilization)
- All three projects start with one command each
- SeaForge has 20+ passing COLREGS tests
- All repos have accurate READMEs
- CLAUDE.md reflects the true three-project architecture

### Phase 2 (SeaForge Launch)
- SeaForge works offline as PWA for COLREGS quizzes
- Quiz mode with scoring functional for all 10 categories
- At least 3 external users have tested and given feedback
- GitHub repo has issue templates and CI pipeline

### Phase 3 (VPS)
- Jarvis responds via Telegram within 30s from VPS
- Heartbeat arrives reliably for 7 consecutive days
- SeaForge accessible at a public URL via HTTPS
- Laptop can be off without losing Telegram or SeaForge

### Phase 4 (Premium)
- Popeye covers all STCW II/1 competency functions
- SeaForge has user accounts and progress tracking
- AI tutor generates meaningful training responses
- CTRB tracker covers full cadet training record

---

## Appendix A: Key Paths (updated 2026-03-14)

| What | Path |
|------|------|
| OpenClaw project | `~/projects/openclaw/` |
| OpenClaw config | `~/.openclaw/openclaw.json` |
| Agent workspaces | `~/.openclaw/workspace[-name]/` |
| Popeye knowledge | `~/.openclaw/workspace-popeye/knowledge/` |
| Sessions | `~/.openclaw/agents/<id>/sessions/*.jsonl` |
| Mission Control | `~/projects/mission-control/` |
| Local API | `~/projects/mission-control/local-api.mjs` |
| SeaForge | `~/projects/seaforge/` |
| Scripts | `~/scripts/` |
| Backups | `~/backups/` |

## Appendix B: Command Cheatsheet

```bash
# === OpenClaw ===
systemctl --user start openclaw-gateway
systemctl --user status openclaw-gateway
npx openclaw agent --agent popeye -m "COLREGS TSS rules?" --json

# === Update OpenClaw (source install) ===
cd ~/projects/openclaw && git pull && pnpm install && pnpm build \
  && npx openclaw gateway install --force \
  && systemctl --user restart openclaw-gateway \
  && openclaw gateway status

# === Mission Control ===
cd ~/projects/mission-control
pnpm dev --host                               # :5174
node local-api.mjs                            # :5175

# === SeaForge ===
cd ~/projects/seaforge
docker compose up --build -d                  # :5000

# === Maintenance ===
tar -czf ~/backups/openclaw-$(date +%F).tar.gz ~/.openclaw/
git status && git add specific-file && git commit -m "feat: desc" && git push
```

## Appendix C: Document Hierarchy

```
This document (SEAFORGE_ROADMAP.md)
└── Full ecosystem architecture + roadmap + integrations
    ├── CLAUDE.md — Dense session primer (<2000 words)
    ├── Boomski Ops Guide — Daily operations manual (Claude memory)
    │   └── Startup, shutdown, troubleshooting, tool integrations
    │       (Spotify, Polar, Bring!, gog calendar, backup procedures)
    ├── Agent workspaces (SOUL.md, AGENTS.md per agent)
    ├── SeaForge docs/ (TRAINING_PLATFORM_PLAN.md, API.md, CONTRIBUTING.md)
    ├── Mission Control docs/ (VIEWS.md)
    └── Individual repo READMEs
```

> **Boomski Ops Guide** lives at `~/.claude/projects/-home-arne/memory/boomski-ops-guide.md` and covers daily operational procedures, CLI tool references, and troubleshooting. This roadmap covers architecture and strategy. They complement each other — don't duplicate content between them.

---

*Single source of truth for the full ecosystem. Review monthly. Update on architectural changes. Feed the CLAUDE.md section into session configs.*

*Last verified: 2026-03-14*
