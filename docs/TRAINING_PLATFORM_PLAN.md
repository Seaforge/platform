# SeaForge Training Platform — Planning Document

> Open-source maritime training for every seafarer, from cadet to master.
> Status: BRAINSTORM — no execution yet. Decision gate required before build.

---

## Vision

A freemium, offline-first training platform for seafarers at every level.
Free tier covers STCW essentials (COLREGS, GMDSS, safety). Premium unlocks
deep competency modules, progress tracking, assessment mode, and AI tutoring.

Built so a 55-year-old chief mate with a basic Android phone can use it
without reading a manual.

---

## What Exists Today (DONE)

### SeaForge Core (deployed, Docker, port 5000)

| Component | Status | Notes |
|-----------|--------|-------|
| COLREGS scenario engine | DONE | 98 scenarios, 10 categories, 3 difficulty levels |
| `/api/lights` endpoint | DONE | Filters: `?category=`, `?difficulty=`, `?random=N` |
| MOB plotter + GMDSS procedure | DONE | Datum drift, search patterns, 19-step checklist |
| AIS overlay (aisstream.io) | DONE | Multi-source: WebSocket + TCP/UDP/Signal K |
| Fleet database | DONE | Heerema fleet, extensible |
| COLREGS encounter analyzer | DONE | CPA/TCPA, situation classification, action advice |
| Leaflet map + dark nautical UI | DONE | Single-page app, works offline for static features |
| Docker single-container deploy | DONE | `docker compose up --build -d` |
| Claude Code skills | DONE | /deploy, /add-fleet, /add-training-scenario |

### Popeye Knowledge Base (available, not yet integrated)

| Asset | Size | STCW Mapping | Integration Status |
|-------|------|-------------|-------------------|
| COLREGS.md (AI-actionable) | 12K | II/1 Table A-II/1 | EXTRACTED into 98 scenarios |
| CTRB_STUDY_GUIDE.md | 57K | II/1 full competency map | NOT YET — needs modularization |
| CTRB_TASKS.md (185 tasks) | 28K | ISF CTRB all sections | NOT YET — personal tracker exists in Popeye |
| GMDSS reference | 16K | IV/2 Radio Operator | NOT YET |
| SMCP (comm phrases) | 15K | II/1 Communications | NOT YET |
| Emergencies reference | 24K | VI/1 Safety training | NOT YET |
| Celestial navigation | 17K | II/1 Nav competency | NOT YET |
| ECDIS/Radar reference | 13K | II/1 ECDIS competency | NOT YET |
| Tanker ops (oil/gas/chem) | 101K | V/1-1, V/1-2 Tanker | NOT YET |
| Cargo/stability/mooring | 40K | II/1, II/2 Cargo | NOT YET |
| MARPOL/IMDG | 37K | II/1 Environmental | NOT YET |
| Medical care | 21K | VI/4 Medical first aid | NOT YET |
| Case studies (accidents) | 25K | Cross-competency | NOT YET |
| Enclosed space entry | 16K | VI/1 Safety | NOT YET |
| 54 reference modules total | ~800K | Various | NOT YET |

---

## What Needs Work (BUILD)

### Phase 1 — Free Training Engine (MVP)

> Goal: a working web app that any seafarer can open on their phone and
> start training COLREGS in 30 seconds. No login, no install, no Docker.

| Task | Effort | Priority |
|------|--------|----------|
| Static site generator (quiz UI from scenario DB) | Medium | P0 |
| Mobile-first responsive design (big buttons, high contrast) | Medium | P0 |
| Category selection screen ("What do you want to train?") | Small | P0 |
| Quiz mode: show scenario, reveal answer on tap | Small | P0 |
| Score tracking (localStorage, no account needed) | Small | P0 |
| Deploy to free hosting (GitHub Pages / Cloudflare Pages) | Small | P0 |
| Domain: seaforge.io or seaforge.training | Small | P1 |
| PWA manifest (installable, works offline) | Small | P1 |
| Dark mode default (bridge-friendly) | Small | P1 |

### Phase 2 — Content Expansion (Free Tier)

| Task | Source | Effort |
|------|--------|--------|
| Sound signals quiz (audio clips) | Popeye COLREGS.md Rule 34/35 | Medium |
| GMDSS procedures module | gmdss-telecommunications.md | Medium |
| Emergency procedures module | emergencies.md + SAR skill | Medium |
| SMCP phrase trainer | smcp.md | Medium |
| Encounter simulator (visual, animated) | Existing COLREGS engine | Large |
| Case study walkthroughs | case-studies.md (25K) | Medium |

### Phase 3 — Premium Features

| Feature | Value Proposition | Effort |
|---------|------------------|--------|
| CTRB task tracker (per-cadet progress) | Academies track student progress | Large |
| AI tutor (Popeye-style quiz + grade + explain) | Personal coaching, 24/7 | Large |
| Assessment mode (timed, exam-format) | MCA oral prep, AMA exam prep | Medium |
| Competency radar chart (visual progress) | Motivating, shareable | Medium |
| Tanker operations deep-dive | V/1-1, V/1-2 specialist cert | Medium |
| DP operations module | DPO cert prep | Medium |
| Celestial navigation worked examples | Sextant + sight reduction practice | Large |
| Instructor dashboard (class view) | Academy selling point | Large |
| Certificate of completion (non-official) | LinkedIn-shareable, motivation | Small |
| Spaced repetition algorithm | Proven learning science | Medium |

### Phase 4 — Platform & Growth

| Task | Effort |
|------|--------|
| User accounts (email, no social login — seafarers have bad wifi) | Medium |
| Offline-first sync (Service Worker + IndexedDB) | Large |
| Multi-language (EN, NL, DE, FR, ES — major maritime languages) | Large |
| API for third-party integration (LMS, academy portals) | Medium |
| Mobile app (PWA first, native later only if needed) | N/A if PWA works |

---

## Free vs Premium — The Hook Strategy

### Principle: free tier must be genuinely useful, not a teaser

Seafarers are price-sensitive and skeptical of upsells. The free tier must
deliver real value so they trust the platform and recommend it to colleagues.

### FREE (forever, no account)

| Content | Why Free |
|---------|----------|
| Full COLREGS quiz (all 98+ scenarios, all categories) | Hook — this is the gateway drug |
| Sound signals trainer | Universally needed, shareable |
| GMDSS procedure checklists | Safety-critical, ethical to share freely |
| Emergency procedures (MOB, fire, flooding) | Safety-critical |
| SMCP phrase reference | Broadly useful, drives adoption |
| Basic score tracking (localStorage) | No friction |
| Case study library (read-only) | Demonstrates depth |
| Rule lookup / quick reference | Utility — makes it a daily tool |

**Why this works:** Every cadet, every OOW, every leisure sailor needs COLREGS.
It's the universal entry point. They'll bookmark it, share it in WhatsApp groups
(seafarer primary communication channel), and come back.

### PREMIUM (subscription or one-time unlock)

| Feature | Price Point | Target |
|---------|------------|--------|
| AI Tutor mode (ask questions, get graded) | $9/mo or $49/yr | Cadets, exam prep |
| CTRB task tracker + study guide | $9/mo or $49/yr | Cadets on traineeship |
| Assessment mode (timed exams) | $9/mo or $49/yr | MCA/AMA exam prep |
| Competency radar + progress analytics | Included in subscription | All subscribers |
| Tanker operations modules | $19 one-time per module | Tanker officers |
| DP operations module | $19 one-time | DPO candidates |
| Celestial navigation practice | $19 one-time | Cadets, trad sailors |
| Academy license (class management) | $199/yr per academy | Maritime academies |
| Instructor dashboard + bulk tracking | Included in academy license | Instructors |

**Pricing rationale:** $9/mo is less than one beer in port. $49/yr is less than
a single textbook. Academy license is trivial compared to simulator costs.

### ACADEMY PITCH

> "Your cadets are already using SeaForge for free COLREGS training.
> With an academy license, you get a dashboard showing every student's
> progress across all STCW competencies, plus assessment generation
> matched to your exam format."

Target academies and their specific needs:

| Academy | Country | Key Need | Hook |
|---------|---------|----------|------|
| AMA (Antwerp Maritime Academy) | BE | STCW II/1 + II/2 curriculum | Supplement simulator, CTRB alignment |
| STC (Enkhuizen/Rotterdam) | NL | Practical cadetship support | Onboard training companion, NL language |
| IBIS / GO Scheepvaart | BE | Budget-constrained entry-level | Free COLREGS, affordable premium |
| MCA academies (South Shields, etc.) | UK | OOW oral exam prep | Assessment mode is the killer feature |
| Simwave / MIWB (Flushing) | NL/BE | Simulator supplement | Bridge between classroom and sim |
| Online (Maris, Seagull, KVH) | Global | CBT compliance modules | Differentiate: open-source, offline, free |
| Aboa Mare | FI | STCW training | Multi-language support |

---

## Accessibility — "The Chief Mate Test"

> If a 55-year-old chief mate on a bulk carrier with a cracked Samsung A13
> and intermittent Starlink can't figure it out in 30 seconds, it's too complex.

### Design principles

1. **No install required** — works in any browser, including Samsung Internet
2. **No account required** for free tier — just open and train
3. **Big touch targets** — minimum 48px, designed for calloused fingers
4. **High contrast** — works in bright sun (deck) and dark bridge
5. **Minimal text** — scenarios are short, answers reveal on tap
6. **Works offline** — PWA with Service Worker, syncs when connected
7. **Low bandwidth** — no images unless necessary, no video autoplay
8. **WhatsApp shareable** — each quiz result generates a share link
9. **Multilingual** — EN default, NL/DE/FR/ES for major fleets
10. **No jargon in UI** — maritime jargon in content, plain language in navigation

### Onboarding flow

```
1. Open link (from WhatsApp, QR code on poster, or search)
2. See: "What do you want to train?" + 6 big category buttons
3. Tap "COLREGS Lights" → first scenario appears
4. Read scenario → tap "Show Answer" → see answer + rule reference
5. Tap "Next" or swipe → next scenario
6. After 10: see score → option to continue or try another category
7. Footer: "Want to track progress? Create free account"
8. Footer: "Want AI tutoring? Upgrade to Premium"
```

No hamburger menus. No settings. No onboarding wizard. Just content.

---

## Target Audiences & Hooks

### 1. Cadets / Trainees (primary growth engine)

- **Who:** Maritime academy students, first-trip cadets
- **Pain:** Expensive textbooks, boring CBT, no practice between classes
- **Hook:** Free COLREGS quiz they can do on the bus to school
- **Upgrade:** CTRB tracker + AI tutor + assessment mode for exam prep
- **Spread:** Share scores in class WhatsApp group, instructor sees adoption

### 2. Competent OOW (retention & depth)

- **Who:** Working officers, 2-10 years experience
- **Pain:** Keeping sharp between courses, preparing for Chief Mate exam
- **Hook:** Quick daily drill (5 scenarios in 3 minutes), case studies
- **Upgrade:** Advanced modules (tanker, DP, celestial), assessment mode
- **Spread:** Recommend to junior officers, use as onboard training tool

### 3. Leisure Seafarers (volume & awareness)

- **Who:** Yacht owners, RYA/ICC holders, weekend sailors
- **Pain:** COLREGS is confusing, no structured way to learn/refresh
- **Hook:** "Do you know your lights?" — viral-friendly quiz
- **Upgrade:** Probably won't — but they spread the brand to professionals
- **Spread:** Sailing forums, Facebook groups, YouTube partnerships

### 4. Maritime Academies (revenue)

- **Who:** Instructors, training managers, heads of department
- **Pain:** Expensive simulators, hard to track individual progress, generic CBT
- **Hook:** "Your students are already using it" — show adoption data
- **Upgrade:** Academy license with instructor dashboard
- **Spread:** Conference presentations, word of mouth between institutions

### 5. Ship Operators / Fleet Managers (enterprise, later)

- **Who:** Training superintendents, HSQE managers
- **Pain:** CBT compliance is checkbox exercise, no real learning
- **Hook:** Better training outcomes = fewer incidents = lower insurance
- **Upgrade:** Fleet license, custom modules, compliance reporting
- **Spread:** Vetting inspections mention it, flag state awareness

---

## Agentic Development Team

> Use AI agents (Claude Code, Popeye framework) to continuously
> expand content, maintain quality, and respond to user needs.

### Agent Roles

| Agent | Role | Tooling |
|-------|------|---------|
| **Content Generator** | Transform Popeye reference docs into quiz scenarios | Claude Code + add-training-scenario skill |
| **Quality Reviewer** | Verify rule citations, flag outdated content | Claude Code + COLREGS.md cross-reference |
| **Gap Analyzer** | Compare content coverage vs STCW competency tables | CURRICULUM_GAP_ANALYSIS.md as baseline |
| **User Feedback Processor** | Triage bug reports, feature requests, content corrections | GitHub Issues + Claude Code |
| **Localization Agent** | Translate scenarios to NL/DE/FR/ES, verify maritime terminology | Claude Code + SMCP reference |
| **Assessment Builder** | Generate exam papers from scenario DB per competency | Claude Code + difficulty/category metadata |

### Continuous Enhancement Workflow

```
1. User reports: "Rule 24 scenario is unclear" (GitHub Issue)
2. Feedback Processor triages → assigns to Content Generator
3. Content Generator reads Popeye reference, rewrites scenario
4. Quality Reviewer verifies against COLREG-Consolidated-2018.pdf
5. PR created → human review → merge → auto-deploy
```

### Content Pipeline (scaling from 98 to 1000+ scenarios)

| Source | Scenarios Possible | Agent Action |
|--------|-------------------|-------------|
| Popeye COLREGS.md | ~150 (rules, lights, shapes, signals) | DONE: 98 extracted |
| CTRB_STUDY_GUIDE.md | ~300 (across all competencies) | Extract Q&A per task |
| Case studies (25K) | ~50 (incident-based scenarios) | Summarize + question |
| GMDSS reference (16K) | ~80 (procedures, equipment, frequencies) | Procedural quizzes |
| SMCP (15K) | ~100 (phrase recognition, response drills) | Fill-in-the-blank |
| Tanker ops (101K) | ~200 (operational procedures, safety) | Module-specific sets |
| Emergencies (24K) | ~80 (decision trees, immediate actions) | Situational quizzes |
| Medical care (21K) | ~60 (ABCDE, CPR, hypothermia, triage) | First aid drills |
| **Total potential** | **~1,000+** | **Agentic generation + human QA** |

---

## Technical Architecture (proposed)

```
seaforge.training (or seaforge.io)
    |
    +-- Static site (GitHub Pages / Cloudflare Pages)
    |   Free tier: quiz engine, reference, case studies
    |   PWA: Service Worker for offline, localStorage for scores
    |   Zero backend for free tier = zero hosting cost
    |
    +-- API backend (existing SeaForge Flask app or separate)
    |   Premium: user accounts, progress sync, AI tutor
    |   Academy: instructor dashboard, class management
    |   SQLite (single user) or Supabase (multi-tenant)
    |
    +-- Content repo (seaforge-training)
    |   Scenario DB as JSON/YAML (version controlled)
    |   Reference docs (Popeye-derived, cleaned for public)
    |   Automated CI: lint rule citations, check duplicates
    |
    +-- Popeye workspace (private, not published)
        Source material for content generation
        Agent skills for content pipeline
        CTRB personal data stays here
```

### What stays private vs public

| Content | Public (open source) | Private |
|---------|---------------------|---------|
| COLREGS scenarios | Yes — free, universal | |
| GMDSS procedures | Yes — safety-critical | |
| Emergency checklists | Yes — safety-critical | |
| SMCP phrases | Yes — IMO public domain | |
| Case studies | Yes — educational | |
| Quiz engine code | Yes — open source | |
| CTRB task framework (generic) | Yes — ISF standard | |
| Arne's personal CTRB progress | | Yes — personal data |
| AI tutor prompts / skills | | Yes — premium IP |
| Tanker ops deep content | | Freemium — preview free, full premium |
| Academy dashboard code | | Yes — premium feature |
| Popeye agent personality/skills | | Yes — OpenClaw IP |

---

## Competitive Landscape

| Platform | Model | Weakness | Our Edge |
|----------|-------|----------|----------|
| Seagull Training | Enterprise subscription | Expensive, compliance-focused, boring | Free tier, engaging, mobile-first |
| KVH Videotel | Enterprise subscription | Video-heavy (bandwidth), no interactivity | Offline-first, quiz-based, low bandwidth |
| Maris (Ocean Technologies) | Per-module purchase | Costly per course, no community | Open source core, community-driven |
| MarineTraffic Academy | Free articles | Not structured training, no assessment | Structured competency progression |
| Various YouTube channels | Free | Unstructured, no tracking, no assessment | Curated, progressive, trackable |
| Textbooks (Nicholls, Danton) | One-time purchase | Static, no interactivity, heavy to carry | Always in pocket, updated continuously |

**Our moat:** Open source + Popeye's 2.8MB knowledge base + agentic content
pipeline + zero marginal cost per user + built by a working seafarer.

---

## Revenue Model

### Year 1: Validate

- Free tier live, track adoption (target: 1,000 monthly active users)
- No premium yet — just build trust and content
- Revenue: $0 (investment phase)
- Cost: ~$0 (static hosting) or ~$5/mo (domain)

### Year 2: Monetize

- Premium subscriptions live ($9/mo individual, $199/yr academy)
- Target: 100 paying individuals + 5 academy licenses
- Revenue: ~$10K-15K/yr
- Cost: ~$50/mo (Supabase, domain, AI API calls for tutor)

### Year 3: Scale

- Fleet operator licenses, more academy partnerships
- Multi-language, more competency modules
- Target: 500 paying individuals + 20 academies
- Revenue: ~$50K-80K/yr
- Consider: VC/grant for maritime ed-tech? IMO endorsement?

---

## Open Questions (decision gates before execution)

1. **Separate repo or monorepo?** Training content as `seaforge-training` repo
   vs keeping it in `seaforge/src/data/`? Recommendation: separate repo for
   content, SeaForge consumes it.

2. **Domain?** seaforge.io / seaforge.training / openbridge.training?
   Check availability before committing.

3. **Legal:** Can we publish Popeye's reference content? IMO COLREGS are public
   domain. SMCP is IMO-published. CTRB task structure is ISF-copyrighted —
   need to verify fair use for educational platform.

4. **AI tutor cost model:** Claude API calls for premium tutor feature.
   At $9/mo subscription, can we sustain ~50 API calls/user/month?
   Estimate: ~$0.50/user/month at current pricing = viable.

5. **Timing:** Build during Arne's traineeship (real-world testing) or after?
   Recommendation: build free tier now (low effort), premium after traineeship
   when there's time for the instructor dashboard.

6. **Name:** "SeaForge Training" or a new brand? Training platform might
   outgrow the SeaForge project. Consider: "Bosun" / "Wheelhouse" /
   "BridgePrep" / keep SeaForge.

---

*Document created: 2026-03-14. Brainstorm only — no execution without decision gate.*
