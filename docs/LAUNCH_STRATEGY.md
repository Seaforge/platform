# SeaForge — 25-Week Open-Source Launch Strategy

**Author:** Arne Verboom | **Date:** 2026-03-23 | **Status:** DRAFT — Awaiting Review
**GitHub Org:** [Seaforge](https://github.com/Seaforge) | **License:** MIT

---

## Executive Summary

Launch SeaForge as a **weekly micro-release** campaign: 25 standalone open-source tools for seafarers, one per week, each independently useful but feeding into the SeaForge platform. This creates 25 moments of community engagement, 25 GitHub repos, and a growing ecosystem that converges into SeaForge v1.0 in Week 25.

**The thesis:** The maritime industry has enterprise software ($50K+/year) and scattered free tools. Nothing exists in between. SeaForge fills that gap by releasing small, free, offline-first tools that a working seafarer can run on their tablet during a 4-hour watch.

---

## System Inventory — What Exists Today

### Assets Ready for Extraction

| Asset | Location | Lines / Size | Status |
|-------|----------|-------------|--------|
| SeaForge platform | `~/projects/seaforge/` | 3,087 py + 524 js | Working v0.1, Docker-ready |
| COLREGS engine | `seaforge/src/core/colregs.py` | ~400 lines | 98 scenarios, CPA/TCPA |
| AIS integration | `seaforge/src/core/ais.py` | ~200 lines | aisstream.io WebSocket |
| MOB calculator | `seaforge/src/core/mob.py` | ~150 lines | Drift, search patterns, GMDSS 19-step |
| Lights database | `seaforge/src/data/lights_db.py` | 98 scenarios | 10 categories × 3 difficulty levels |
| Compliance vault | `seaforge/src/core/vault_integrity.py` | ~200 lines | SHA-256 integrity, Phase 1 complete |
| Popeye knowledge | `~/.openclaw/workspace-popeye/references/` | **72 documents, 2.8MB** | Maritime mastery V17 |
| Popeye skills | `workspace-popeye/skills/` | 5 skills | OOW, Strategy, SAR, Maritime Master, CVC |
| Maritime Hub scaffold | `~/projects/maritime-hub/` | Minimal | React + Vite, neuroplasticity design doc |
| Mission Control maritime | `~/projects/mission-control/src/store/maritimeStore.ts` | 600+ lines | Certs, CTRB, mood, voyage, KPIs |
| COLREGS reference | `workspace-popeye/COLREGS.md` | Large | Full Rules 1-38 + interpretations |
| AHTS DP2 reference | `workspace-popeye/AHTS_DP2_OPERATIONS.md` | Large | Anchor handling, DP operations |

### Knowledge Base Categories (Popeye's 72 References)

```
Navigation & Safety (12):     COLREGS, celestial-nav, navigation, ecdis-radar, brm, safety-mgmt,
                               emergencies, isps-ism, maritime-security, cyber-security, dp-ops, navigation-advanced
Regulation & Compliance (8):  stcw, eu-emissions, imo-net-zero, regulatory-tracker, marpol,
                               maritime-single-window, qhse-iso, certificates-full
Operations (12):              ship-design, heavy-lift, tug-towage, mooring, cargo-securing,
                               tanker-ops, offshore-vessels, port-terminal, port-research, project-mgmt-advanced,
                               mariner-workload, meeting-kickoff
Engineering (6):              marine-engineering, ship-construction, performance-digital-twin,
                               bridge-electronics, ship-it-infrastructure, decarbonization-fuels
Innovation (6):               remote-ops-mass, wind-assisted-propulsion, offshore-wind-floating,
                               fleet-analytics-bi, vessel-management-platforms, crew-management-mobility
Training (4):                 competency-testing, oow-second-brain, medical-care, elite-pilotage
Commercial (4):               commercial-contracts, vetting-audits, imdg-code, case-studies
Other (2):                    marine-ecology-science, gmdss-telecommunications
Special (18):                 Remaining domain-specific reference files
```

---

## The 25-Week Launch Plan

### Design Principles

1. **Each week = 1 standalone repo** — Works without SeaForge, no dependencies
2. **PWA / offline-first** — Static site or lightweight Docker container
3. **Free APIs only** — Open-Meteo, aisstream.io, EMODnet, NOAA
4. **Mobile-friendly** — Designed for bridge tablet or phone
5. **Content from Popeye** — Curated exports, never raw workspace files
6. **Buildable in a weekend** — Scope to ~8-16 hours of work per release
7. **Each one is a marketing moment** — Reddit post, LinkedIn, maritime forums

### Phase 1: Quick Wins (Weeks 1-6) — "Tools That Sell Themselves"

These are standalone tools that solve immediate pain points. Each creates immediate value and gets shared organically.

| Wk | Repo Name | What It Is | Source | Effort |
|----|-----------|-----------|--------|--------|
| **1** | `colregs-quiz` | PWA: Interactive COLREGS quiz (Rules 13-15, lights & shapes). Timed mode, scoring, streak tracking. Works offline. | `seaforge/src/data/lights_db.py` + `core/colregs.py` | 8h |
| **2** | `rest-hours` | Rest hour calculator + MLC 2006 compliance checker. Log sleep blocks, see if you're legal. Visual 24h/7d bars. | `mission-control/seaModeStore.ts` logic | 8h |
| **3** | `maritime-weather` | Free maritime weather dashboard. Wind, waves, currents, rain radar. Beaufort conversion. Position-based. Open-Meteo API. | `popeye/references/metocean-weather-routing.md` | 10h |
| **4** | `lights-and-shapes` | Flashcard trainer: "What vessel shows these lights?" SVG renders of navigation lights at night. Spaced repetition. | `seaforge/src/data/lights_db.py` (98 scenarios) | 8h |
| **5** | `mob-calculator` | Man Overboard drift calculator. Wind/current vectors, search patterns (expanding square, sector, parallel), GMDSS 19-step checklist. | `seaforge/src/core/mob.py` | 6h |
| **6** | `bridge-checklists` | Digital bridge checklists: departure, arrival, anchoring, heavy weather, pilot boarding. Customizable YAML-based. Print-friendly. | `popeye/references/safety-management.md` | 8h |

**Phase 1 goal:** 6 repos, 6 Reddit/LinkedIn posts, first community feedback. Each is a complete product.

### Phase 2: Training Platform (Weeks 7-12) — "Learn at Sea"

Build out the training/competency tools. This is where SeaForge differentiates from enterprise products — free, offline training.

| Wk | Repo Name | What It Is | Source | Effort |
|----|-----------|-----------|--------|--------|
| **7** | `smcp-trainer` | Standard Marine Communication Phrases trainer. Flash cards, audio pronunciation, situational contexts. | `popeye/references/gmdss-telecommunications.md` | 10h |
| **8** | `morse-flags` | Morse code + International signal flags trainer. Tap-to-signal, timed recognition, NATO phonetic alphabet. | `popeye/references/competency-testing.md` | 8h |
| **9** | `gmdss-reference` | GMDSS quick reference: DSC procedures, SART/EPIRB operation, NAVTEX scheduling, sea areas A1-A4, frequencies. | `popeye/references/gmdss-telecommunications.md` | 8h |
| **10** | `stability-basics` | Interactive stability & trim calculator. Enter GM, displacement, loading condition → see stability curve + GZ. For OOW-level understanding. | `popeye/references (new module needed)` | 12h |
| **11** | `marpol-guide` | MARPOL Annex I-VI quick reference. Discharge rules, special areas, record book requirements. Interactive map of special areas. | `popeye/references/marpol-ecology.md` | 10h |
| **12** | `ctrb-tracker` | Digital Cadet Training Record Book. Track ISF competencies, collect sign-offs, generate PDF for assessor. | `mission-control/maritimeStore.ts` CTRB logic | 12h |

**Phase 2 goal:** Complete training toolkit. CTRB tracker is the killer feature for cadets.

### Phase 3: Operational Tools (Weeks 13-18) — "Use on Watch"

Tools designed for the working OOW during a 4-hour watch rotation.

| Wk | Repo Name | What It Is | Source | Effort |
|----|-----------|-----------|--------|--------|
| **13** | `anchor-watch` | GPS-based anchor watch. Set swing circle, alarm on drag. Shows wind/current vectors. Works on phone. | `seaforge` anchor module | 8h |
| **14** | `passage-planner` | Passage planning assistant: waypoint entry, distance/ETA calc, weather window check, nav warnings (NAVAREA). | `popeye/references/navigation-advanced.md` | 12h |
| **15** | `timezone-calc` | Ship's time zone calculator. Enter UTC offset + clocks, get local/UTC/LT conversions. Zone description generator for bridge clock labels. | `mission-control/TimezoneView` logic | 6h |
| **16** | `drill-manager` | Schedule, log, and track mandatory drills. Fire, abandon ship, MOB, SOPEP, security. Generates drill reports. SOLAS interval compliance. | `seaforge` drill module | 10h |
| **17** | `voyage-log` | Digital voyage log: position, weather, events, fuel readings. Timeline view. Export to PDF/CSV for port authorities. | `mission-control/maritimeStore.ts` voyage logic | 12h |
| **18** | `psc-prep` | Port State Control inspection preparation tool. Checklist by convention (SOLAS, MARPOL, MLC, ISPS). Certificate status. Deficiency risk assessment. | `popeye/references/vetting-audits.md` | 10h |

**Phase 3 goal:** Working OOW toolkit. These are the tools you'd actually use during a watch.

### Phase 4: Intelligence & Innovation (Weeks 19-23) — "See the Future"

Advanced tools that use data to provide insights. This is where AI and analytics come in.

| Wk | Repo Name | What It Is | Source | Effort |
|----|-----------|-----------|--------|--------|
| **19** | `ais-tracker` | Free AIS vessel tracker. Live map, fleet filtering, CPA calculation, encounter detection. | `seaforge/src/core/ais.py` | 10h |
| **20** | `fatigue-monitor` | Circadian risk assessment. Two-process model, trough windows (03:00-07:00, 13:00-17:00), hours-awake tracking. | `mission-control/seaModeStore.ts` | 8h |
| **21** | `emissions-calc` | EU ETS & FuelEU Maritime calculator. Per-voyage CO₂ estimation, compliance check, penalty estimation. | `popeye/references/eu-emissions-framework.md` | 12h |
| **22** | `cert-tracker` | Certificate expiry tracker. STCW, medical, endorsements, company certs. 90/30/7-day alerts. Renewal URL linking. | `mission-control/maritimeStore.ts` certs | 8h |
| **23** | `wellbeing-log` | Seafarer wellbeing dashboard: mood, energy, sleep quality, exercise. Weekly trends. Offline-first. Anonymous (privacy-focused). | `mission-control` mood + maritime-hub design | 10h |

**Phase 4 goal:** Data-driven tools. These attract attention from shipping companies and maritime schools.

### Phase 5: Convergence (Weeks 24-25) — "The Platform"

| Wk | Repo Name | What It Is | Source | Effort |
|----|-----------|-----------|--------|--------|
| **24** | `seaforge-cli` | CLI tool that installs and manages SeaForge modules. `seaforge install colregs-quiz rest-hours`. Module registry. | New | 16h |
| **25** | `seaforge` | **SeaForge v1.0** — The unified platform. All 23 modules integrated. Single Docker container. Self-hosted. The culmination. | Everything above | 20h |

---

## Architecture Decision: How Modules Become a Platform

```
Week 1-23: Individual repos (standalone)
├── colregs-quiz/          → Static PWA (GitHub Pages)
├── rest-hours/            → Static PWA
├── maritime-weather/      → Static PWA + API proxy
├── ...
└── wellbeing-log/         → Static PWA + localStorage

Week 24: seaforge-cli
├── Module registry (JSON)
├── Install/update commands
└── Shared config format

Week 25: seaforge (platform)
├── Flask API server (unified backend)
├── Module loader (imports from individual repos)
├── Shared SQLite database
├── Single Docker container
└── Leaflet chart view (Week 19's AIS tracker becomes the map)
```

Each module follows a standard structure:

```
module-name/
├── index.html           # PWA entry point (works standalone)
├── src/
│   ├── app.js           # Main logic
│   ├── data/            # Static data (scenarios, checklists)
│   └── style.css        # Dark nautical theme
├── api/                 # Optional: Flask blueprint (for platform integration)
│   └── routes.py
├── tests/
├── README.md
├── LICENSE              # MIT
└── seaforge.json        # Module manifest (name, version, category, dependencies)
```

---

## Tech Stack Decision

### For Weekly Modules (Weeks 1-23)

**Static PWA (primary):** Vanilla JS + Tailwind CSS + Service Worker. No build step needed. Works offline. Deploys to GitHub Pages for free.

**Why not React?** Too heavy for single-purpose tools. A COLREGS quiz doesn't need a component framework. Keep it minimal so maritime developers can contribute without learning React.

**When to use React:** Only for complex UIs (CTRB tracker in Week 12, passage planner in Week 14). Use Vite + React + Tailwind for those.

**Data storage:** localStorage for user data. IndexedDB for larger datasets. No server needed for most modules.

### For SeaForge Platform (Week 25)

**Backend:** Flask (Python) — already built, 39 endpoints, 3,087 lines
**Database:** SQLite (WAL mode) — single file, simple backup, offline-first
**Frontend:** Leaflet.js + vanilla JS (chart view) + individual module frontends
**Deployment:** Single Docker container, port 5000
**Package count:** 4 Python dependencies (flask, gunicorn, websocket-client, pyais)

---

## Content Pipeline: Popeye → SeaForge

Popeye's 72 reference documents are the **content goldmine**. Here's the extraction protocol:

```
Popeye Workspace (private, 2.8MB)
    ↓ curated extraction
SeaForge Data Files (public, MIT)
    ↓ structured format
Module Data (JSON/YAML)
    ↓ rendered
User-Facing Tool
```

### Extraction Rules

1. **Never commit raw Popeye files** — Only curated, structured exports
2. **Attribution in commit messages** — `feat: add 12 TSS scenarios (source: Popeye maritime-master V17)`
3. **No personal data leakage** — No agent configs, no API keys, no workspace paths
4. **Validate before export** — Run through Popeye agent first ("Is this correct? Any updates needed?")
5. **JSON preferred** — Machine-readable, versionable, diffable

### Content Already Ready for Export

| Popeye Document | Target Module | Data Type | Est. Items |
|-----------------|---------------|-----------|------------|
| `COLREGS.md` | colregs-quiz | Quiz scenarios | 98 existing + 30 new |
| `gmdss-telecommunications.md` | gmdss-reference, smcp-trainer | Reference cards, phrases | ~200 |
| `safety-management.md` | bridge-checklists, drill-manager | Checklists | ~40 |
| `marpol-ecology.md` | marpol-guide | Discharge rules, special areas | ~60 |
| `vetting-audits.md` | psc-prep | Inspection checklists | ~80 |
| `competency-testing.md` | morse-flags | Flashcards | ~100 |
| `navigation-advanced.md` | passage-planner | Planning steps | ~30 |
| `eu-emissions-framework.md` | emissions-calc | Formulas, thresholds | ~20 |
| `certificates-full.md` | cert-tracker | Certificate types | ~50 |
| `metocean-weather-routing.md` | maritime-weather | Beaufort scale, WMO codes | ~30 |
| `emergencies.md` | mob-calculator, drill-manager | Procedures | ~40 |
| `medical-care.md` | (future) medical-reference | Triage protocols | ~30 |

---

## Monetization Path (Long-Term)

```
FREE (MIT, always):
├── All 25 standalone tools
├── SeaForge platform (self-hosted)
├── COLREGS quiz engine
├── All training content
└── Community contributions

PREMIUM ($9/mo — "SeaForge Pro"):
├── AI tutor (Gemini-powered, contextual help)
├── Assessment mode (timed exams, STCW-aligned)
├── Competency radar (visual progress across all functions)
├── Cloud sync (cross-device, backup)
└── Certificate renewal alerts (email/push)

ACADEMY ($199/yr — "SeaForge Academy"):
├── Multi-user accounts (maritime schools)
├── Instructor dashboard (student progress)
├── LMS integration (Moodle, Canvas)
├── Bulk certificate tracking
└── Custom branding
```

**Revenue targets:**
- Month 6: 100 free users, 10 Pro ($90/mo)
- Month 12: 1,000 free users, 50 Pro ($450/mo), 2 Academy ($400/yr)
- Month 18: 5,000 free users, 200 Pro ($1,800/mo), 10 Academy ($2,000/yr)

---

## Community & Marketing Strategy

### Where Seafarers Are

| Platform | Audience | Content Strategy |
|----------|----------|------------------|
| **Reddit r/maritime, r/Nautical** | Cadets, junior officers | "I built a free COLREGS quiz — feedback?" |
| **LinkedIn (maritime groups)** | Senior officers, fleet managers | Professional posts, industry analysis |
| **The Nautical Institute** | All ranks | Conference presentations, journal articles |
| **Maritime forums (gCaptain, MarineInsight)** | Working seafarers | How-to guides, tool announcements |
| **GitHub** | Maritime developers | Clean READMEs, good issues, contributor guide |
| **Telegram maritime groups** | International seafarers | Tool announcements, feedback collection |
| **YouTube** | Cadets, students | Demo videos, "5-min tool walkthrough" |

### Weekly Launch Rhythm

```
Monday:    Code freeze. README polish. Screenshots.
Tuesday:   Push to GitHub. Tag release.
Wednesday: Reddit post + LinkedIn post + Tweet
Thursday:  Respond to feedback. Fix quick issues.
Friday:    Plan next week's module.
Weekend:   Build next module.
```

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep per module | Delays weekly cadence | Hard 16h cap per module. Ship it. |
| No community traction | Wasted effort | Week 1-3 validates demand. Pivot if zero engagement. |
| Content accuracy (safety-critical) | Liability, reputation | All maritime content reviewed via Popeye + manual check. Disclaimer on every tool. |
| Burnout (solo developer) | Project stalls | Modules are independent. Skip a week if needed. Backlog doesn't grow. |
| Enterprise competition | Outspent on features | Don't compete on features. Compete on price ($0) and accessibility (offline, self-hosted). |
| AIS API dependency | Service disruption | aisstream.io is free but rate-limited. NMEA fallback for shipboard. |

---

## Documents to Create/Update

### Immediate (This Week)

1. **`seaforge/README.md`** — Rewrite for open-source launch. Clear value prop, quick start, contributor guide.
2. **`seaforge/CONTRIBUTING.md`** — How to contribute modules, code standards, PR process.
3. **`seaforge/docs/MODULE_TEMPLATE.md`** — Standard structure for weekly modules.
4. **`seaforge/.github/ISSUE_TEMPLATE/`** — Bug report, feature request, new module proposal.
5. **GitHub org setup** — Create `Seaforge` org, transfer repos, set up project board.

### Before Week 1 Launch

6. **`colregs-quiz/README.md`** — Standalone repo, screenshots, demo link.
7. **Disclaimer/license header** — "This tool is for training purposes only. Not a substitute for professional seamanship."
8. **GitHub Pages deployment** — Auto-deploy PWAs on push.
9. **Social media accounts** — Twitter/X, LinkedIn page for SeaForge.

### Ongoing

10. **`seaforge/docs/SEAFORGE_ROADMAP.md`** — Update with this 25-week plan (replace current content).
11. **`~/.claude/memory/seaforge_launch_strategy.md`** — Persist this strategy to Claude memory.
12. **Popeye export log** — Track what's been extracted from Popeye's workspace.

---

## Relationship to Existing Projects

### What Changes

| Project | Current Role | New Role |
|---------|-------------|----------|
| **SeaForge** | Monolithic Flask app | Platform that integrates all 25 modules |
| **Maritime Hub** | Standalone React scaffold | **MERGE INTO** Week 23's wellbeing-log (React version) |
| **Mission Control** | Personal dashboard | Stays private. Maritime features extracted to public modules. |
| **Popeye** | Private AI agent | Content source. Never exposed publicly. |
| **OpenClaw** | Private AI runtime | Stays private. Powers AI tutor in premium tier. |
| **Paperclip** | Reference/study material | Inspiration for multi-agent orchestration. Not used directly. |

### Key Boundary

```
PRIVATE (never open-source):
├── OpenClaw (agent runtime, API keys, session data)
├── Mission Control (personal dashboard, Supabase data)
├── Popeye workspace (raw knowledge files, agent config)
└── Claude memory (conversation history, personal preferences)

PUBLIC (open-source, MIT):
├── SeaForge platform
├── 25 standalone tools
├── Curated maritime content (exported from Popeye)
└── Module development kit
```

---

## Week 1 Action Plan: `colregs-quiz`

### Scope
- Extract 98 lights & shapes scenarios from SeaForge's `lights_db.py`
- Convert to JSON format
- Build static PWA: HTML + vanilla JS + Tailwind
- Quiz mode: random scenario, 4 multiple-choice answers, timer, score
- Streak tracking (localStorage)
- Dark nautical theme
- Offline-first (Service Worker)
- Deploy to GitHub Pages

### Acceptance Criteria
- [ ] Works without internet after first load
- [ ] 98 scenarios playable
- [ ] Score tracking persists across sessions
- [ ] Mobile-friendly (375px viewport)
- [ ] < 1MB total download
- [ ] README with screenshots
- [ ] MIT license
- [ ] Disclaimer: "Training tool only"

### Files to Create
```
colregs-quiz/
├── index.html
├── src/
│   ├── quiz.js
│   ├── data/scenarios.json    (exported from lights_db.py)
│   ├── render.js              (SVG light rendering)
│   └── style.css
├── sw.js                      (Service Worker for offline)
├── manifest.json              (PWA manifest)
├── README.md
├── LICENSE
└── seaforge.json
```

---

## Success Metrics

| Metric | Week 6 | Week 12 | Week 25 |
|--------|--------|---------|---------|
| GitHub repos | 6 | 12 | 26 (25 + platform) |
| Total stars | 50 | 200 | 1,000 |
| Community contributors | 2 | 5 | 15 |
| Monthly active users | 100 | 500 | 2,000 |
| Reddit/forum mentions | 10 | 30 | 100 |
| Pro subscribers | 0 | 5 | 50 |

---

## Decision Log

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| 1 | Vanilla JS over React for standalone tools | Lower barrier for maritime developers, no build step, smaller bundle | 2026-03-23 |
| 2 | One repo per tool, not monorepo | Each tool independently discoverable, shareable, star-able on GitHub | 2026-03-23 |
| 3 | PWA + GitHub Pages for distribution | Zero hosting cost, works offline, instant deployment | 2026-03-23 |
| 4 | SQLite over Postgres for platform | Single file, simple backup, zero-config, perfect for self-hosted | 2026-03-23 |
| 5 | Flask (Python) for platform backend | Already built, 3K lines, 4 deps, familiar to maritime automation community | 2026-03-23 |
| 6 | Maritime Hub merges into wellbeing-log module | Avoid duplicate projects, focus energy | 2026-03-23 |
| 7 | Popeye content curated, never raw-exported | Privacy, accuracy, licensing compliance | 2026-03-23 |

---

*"Technology is the force multiplier. Seamanship is the foundation that never changes."*
— Popeye, Master Mariner V17
