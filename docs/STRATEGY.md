# SeaForge Strategy: From Open-Source Project to Maritime Business

**Date:** 2026-03-27
**Author:** Arne + Claude Code (strategy session)
**Status:** Draft -- decisions needed by Arne before execution

---

## Executive Summary

SeaForge today is a working self-hosted maritime platform with a map, COLREGS engine, fleet tracking, weather overlays, a compliance vault skeleton, and several wellbeing/ops stubs. It runs on a laptop or Raspberry Pi. The codebase is clean, MIT-licensed, and public on GitHub.

The problem: the project tries to be everything at once -- navigation intelligence, crew wellness, training platform, compliance vault, drill manager, and daily ops tool. That scope is a trap. No solo developer ships all of that before running out of energy, and no user adopts a tool that does twelve things at 30% quality.

This document answers four questions:
1. What is the minimum product that makes one seafarer's life meaningfully easier?
2. How do you decompose it into independent modules that invite contribution?
3. How does it generate income (in multiple ways)?
4. What gets built when?

The core thesis: **SeaForge wins by being the "personal dashboard" that a single watchkeeping officer installs on their own tablet -- not by competing with bridge systems or fleet management platforms.** Start personal. Earn trust. Expand from there.

---

## 1. MVP Scope & Customer Definition

### Target User: Junior Deck Officer (OOW / 3rd Officer / Cadet)

**Why this role first:**
- Most overwhelmed by information (learning regulations, standing watch, tracking training hours)
- Most likely to adopt personal tools (digital-native, career-motivated)
- Least served by existing ship systems (bridge equipment is for the Master/Chief Officer; cadets get PDFs)
- Arne *is* this user -- authentic product-market fit
- Career progression creates natural upsell (cadet -> 3rd officer -> Chief Officer -> Master)

**Why NOT other roles first:**
- Captain/Chief Engineer: satisfied with existing workflows, resistant to change, high trust bar
- Cook/Steward: different problem domain entirely, small addressable population
- Engine room crew: needs hardware integration (sensors), raises the complexity bar

### Target Vessel Type: Short-Sea / Coastal (< 3000 GT)

**Why:**
- Smaller crews (6-15 people) = each person wears more hats = more pain from fragmented tools
- Shorter voyages = more frequent port calls = easier to download updates, get internet access
- European short-sea fleet is large (ferries, RoRo, tugboats, offshore supply vessels)
- Less regulated than deep-sea (lower compliance bar to clear for MVP)
- Arne's direct experience (Baltic tugs) = authentic testing environment

**Why NOT deep-sea container/tanker first:**
- 30+ crew, established hierarchy, change requires management approval
- Longer offline periods make "cloud sync" features useless
- Higher regulatory burden (SOLAS, ISPS, ISM) raises the bar before you can call it "compliant"

### The Single Pain Point: **Watchkeeping Preparation & Personal Compliance Tracking**

A junior OOW's daily pain:
1. "Am I getting enough rest?" (MLC compliance -- currently tracked on paper or Excel)
2. "Do I know my COLREGS?" (exam prep anxiety, no good free trainer exists)
3. "What's my training progress?" (CTRB booklet is a physical binder, easy to lose track)
4. "What happened last watch?" (handover notes are verbal or scribbled)

**The MVP solves #1 and #2 first. That is it.**

### MVP Feature Set (Ruthlessly Scoped)

| Feature | In MVP | Reason |
|---------|--------|--------|
| Rest hours logger (MLC compliant) | YES | Daily use, regulatory requirement, replaces paper |
| COLREGS trainer (lights/shapes/encounters) | YES | Already built, unique differentiator, no competitor |
| Watch handover notes | YES | Simple text + timestamp, high daily value |
| Maritime map + weather | NO (Phase 2) | Already in codebase but not the core value prop |
| AIS tracking | NO (Phase 2) | Requires API key, internet, not personal-tool core |
| Drill manager | NO (Phase 2) | Ship-level tool, not personal tool |
| Workout/meal/mood tracker | NO (Phase 3) | Nice to have, not the hook |
| Compliance vault | NO (Phase 3+) | Enterprise feature, premature for personal tool |
| Signal K / IoT | NO (Phase 4+) | Hardware dependency, zero users need it yet |

### Success Metrics for MVP

| Metric | Target | Timeframe |
|--------|--------|-----------|
| Arne uses it daily on vessel | Yes/No | Week 6 |
| One other seafarer installs it | Yes/No | Month 3 |
| GitHub stars | 50 | Month 6 |
| Rest hours entries per week (Arne) | 7+ | Week 8 |
| COLREGS trainer sessions per week | 3+ | Week 8 |

---

## 2. Open-Source Modularity Breakdown

### Principle: Each module must work independently OR as part of SeaForge

The current codebase mixes concerns. The refactoring target:

```
seaforge/
  core/                          # Independent libraries (pip-installable)
    seaforge-colregs/            # COLREGS engine (pure Python, zero deps)
    seaforge-mlc/                # MLC rest hours calculator (pure Python)
    seaforge-nmea/               # NMEA parser (pure Python)

  platform/                      # The full SeaForge web app
    src/api/                     # Flask REST endpoints
    src/data/                    # SQLite data layer
    static/                      # Frontend
    templates/                   # Jinja2

  plugins/                       # Optional add-ons
    seaforge-ais/                # AIS stream integration
    seaforge-weather/            # Weather overlay provider
    seaforge-signalk/            # Signal K bridge
    seaforge-vault/              # Compliance vault (enterprise)
```

### Module Independence Matrix

| Module | Standalone? | Integrates into existing systems? | Community value? |
|--------|-------------|-----------------------------------|------------------|
| `seaforge-colregs` | YES (Python library) | YES (any Python app) | HIGH (no open-source COLREGS engine exists) |
| `seaforge-mlc` | YES (Python library) | YES (HR systems, crew management) | HIGH (MLC calc is needed everywhere) |
| `seaforge-nmea` | YES (Python library) | YES (any marine IoT project) | MEDIUM (alternatives exist but are mediocre) |
| `seaforge-ais` | Plugin | YES (WebSocket wrapper) | MEDIUM |
| `seaforge-weather` | Plugin | Limited (API wrapper) | LOW |
| `seaforge-vault` | Plugin | YES (compliance bolt-on) | HIGH (for enterprise) |

### The "Library-First" Strategy

**Before building the full platform, extract the COLREGS engine and MLC calculator as standalone pip packages.** This is the fastest path to community adoption:

1. `pip install seaforge-colregs` -- a pure Python COLREGS classification engine with no web dependencies
2. `pip install seaforge-mlc` -- MLC 2006 rest hour calculator with compliance checking

Why this matters:
- Other maritime developers integrate these into their own projects
- Creates inbound awareness for the full SeaForge platform
- Forces clean API boundaries in the codebase
- Each library gets its own GitHub repo, issues, contributors
- Maritime universities can use `seaforge-colregs` in teaching (huge distribution channel)

### What Shipping Companies Can Integrate

Shipping companies will NOT install an entire new platform. But they WILL:
- Use `seaforge-colregs` as a library in their existing training software
- Use `seaforge-mlc` to validate their rest hour calculations
- Use the COLREGS trainer as a standalone web app for crew training
- Use the compliance vault schema as a reference implementation

### What Works Standalone for Open-Source Community

- Full SeaForge platform (Docker, self-hosted, personal use)
- COLREGS trainer (web app, can be hosted on any free tier)
- Individual Python libraries
- Fleet database (JSON, community-maintained vessel data)

### Avoiding "Build Everything Before Feedback"

The rule: **nothing gets built until someone (including Arne) has used the previous thing for 2+ weeks.** Specifically:
- Do NOT build the compliance vault further until the rest hours logger is used daily
- Do NOT build Signal K integration until someone with a Signal K server requests it
- Do NOT build multi-vessel features until there is a second vessel
- Do NOT build authentication until there is a second user

---

## 3. Monetization Pathways

### The Matrix

| Path | What You Sell | To Whom | Revenue Type | Viable When? | Estimated Range |
|------|---------------|---------|-------------|--------------|-----------------|
| **A. COLREGS Training SaaS** | Hosted trainer with scoring, certificates, class management | Maritime academies, training centers | Subscription (per seat) | Phase 1 (month 3) | EUR 5-20/student/month |
| **B. Consulting** | Maritime software integration, compliance system design | Ship management companies | Project-based | Phase 2 (month 6) | EUR 80-150/hour |
| **C. Premium Plugins** | Compliance vault, advanced analytics, fleet dashboard | Ship operators (5-50 vessels) | License or subscription | Phase 3 (month 9) | EUR 200-1000/vessel/month |
| **D. Freelance Development** | Maritime UX, IoT integration, Python maritime libraries | Maritime tech companies | Contract | Immediate (portfolio) | EUR 60-120/hour |
| **E. Government/Grants** | Maritime safety R&D, crew welfare innovation | EU Maritime affairs, IMO initiatives, national maritime authorities | Grant funding | Phase 2 (month 6) | EUR 10K-100K per grant |
| **F. OOW Personal Premium** | Advanced rest hour analytics, certificate tracking, career planner | Individual officers | Freemium (free core + paid extras) | Phase 2 (month 6) | EUR 5-15/month |

### Priority Ranking (Effort vs. Likelihood)

**Tier 1 -- Start Now:**
1. **D. Freelance/Portfolio** -- SeaForge IS your portfolio. Every feature you build demonstrates maritime + software expertise. Start marketing yourself as "maritime software developer" on LinkedIn, maritime forums, Crew Connect conferences. Zero extra work needed.
2. **A. COLREGS Training** -- The trainer already exists. Package it as a standalone hosted service. Maritime academies spend EUR 50-200/student on training tools. Even 20 students at EUR 10/month = EUR 200/month. Small but real.

**Tier 2 -- Month 3-6:**
3. **F. OOW Premium** -- Once the rest hours + COLREGS MVP is used by real seafarers, add premium features (analytics dashboard, certificate expiry alerts, PDF export for interviews). Low price, high volume potential.
4. **E. Grants** -- Apply to: EU Horizon Europe (maritime digitalization), Dutch Maritime Fund (STC Group connection), ITF Seafarers' Trust (crew welfare), EMSA innovation calls. Having a working open-source tool is the application itself.

**Tier 3 -- Month 6-12:**
5. **B. Consulting** -- Once SeaForge has users and a compliance vault, offer "maritime compliance digitalization" consulting. Ship management companies (V.Ships, BSM, Anglo-Eastern) spend millions on compliance. You are the expert who built the open-source tool.
6. **C. Enterprise Plugins** -- The compliance vault becomes the premium layer. Open core model: free SeaForge, paid vault + fleet dashboard + API access.

### What NOT to Monetize

- The core platform (stays MIT, always free)
- The COLREGS engine library (stays MIT -- distribution > revenue)
- The MLC calculator library (stays MIT)
- Basic rest hours logging (stays free)

### Havenarbeider / Port Workers

Realistic assessment: port workers are a different user base with different problems (shift scheduling, crane safety, cargo handling). SeaForge's architecture does not naturally extend to port operations. **Park this for now.** If a port worker use case emerges organically (e.g., pilot boat crews who are basically short-sea seafarers), address it then.

---

## 4. Phased Rollout

### Phase 0: Foundation (Weeks 1-6, No Vessel Access)

**Goal:** A junior OOW can install SeaForge on their laptop and use it daily for rest hours + COLREGS training.

| Week | Deliverable | Details |
|------|-------------|---------|
| 1-2 | Rest hours logger MVP | Simple form: start/end time, work/rest toggle. MLC compliance calc (10h/24h, 77h/7d). Traffic-light status display. SQLite storage. |
| 2-3 | COLREGS trainer polish | Already built. Add: session scoring, progress tracking, spaced repetition for weak areas. |
| 3-4 | Watch handover notes | Text input + timestamp. Previous/next watch display. Simple but daily-use. |
| 4-5 | Mobile-friendly UI | Current UI is desktop-focused. Seafarers use tablets/phones. Responsive layout for the three MVP features. |
| 5-6 | Standalone deployment | One-command Docker install. Offline-capable. README that a cadet can follow. |

**NOT in Phase 0:** Map, AIS, weather, drills, compliance vault, auth, fleet features.

**Extract during Phase 0:**
- `seaforge-colregs` as standalone pip package (separate repo)
- `seaforge-mlc` as standalone pip package (separate repo)

**Marketing during Phase 0:**
- Post COLREGS trainer on r/maritime, r/sailing, maritime forums
- Share `seaforge-colregs` on Python maritime channels
- LinkedIn posts about building open-source maritime tools
- Contact 2-3 maritime academies about the COLREGS trainer

### Phase 1: First Paying Customer (Months 2-4)

**Target customer:** A maritime training center or academy.

**The pitch:** "Your cadets need COLREGS training. Current tools cost EUR 100+/student. SeaForge COLREGS Trainer is free for individual use, EUR 10/student/month for classroom management (instructor dashboard, class progress tracking, scored assessments, completion certificates)."

**What to build:**
- Instructor dashboard (view student progress, assign quizzes, export reports)
- Class management (add students, track completion)
- Scored assessments with timestamp (for certification evidence)
- Simple auth (instructor vs. student roles -- lightweight, not the full RBAC from the vault)

**Revenue target:** 1 training center, 20-50 students, EUR 200-500/month.

**Parallel track:** Arne uses rest hours logger and watch notes daily. Collects feedback. Iterates.

### Phase 2: Expand Use Cases (Months 4-8)

**Add based on demand (not speculation):**

Option A -- If training demand is strong:
- Expand trainer to include sound signals, day shapes, maneuvering signals
- Add STCW competency tracking
- Add drill scenario training (tabletop exercises)
- Target more academies

Option B -- If personal tool demand is strong:
- Add maritime map + weather (already built, just integrate into MVP flow)
- Add AIS tracking
- Add certificate expiry tracker
- Launch premium tier for individual officers

Option C -- If compliance demand emerges:
- Resume compliance vault work (the six keystones)
- Build rest hours export (MLC format for PSC inspection)
- Build drill logging with proper signoff workflow

**IoT / Signal K: NOT YET.** Only introduce when a user with a Signal K server asks for it. Building IoT infrastructure without a vessel to test on is waste.

### Phase 3: Platform Maturity (Months 8-12)

Based on which Phase 2 path succeeded:
- If training: build a proper LMS (Learning Management System) layer
- If personal tool: build the wellness features (workout, meals, mood)
- If compliance: build the vault properly (auth, RBAC, signoff, encryption)
- Apply for grants with traction data
- Start consulting conversations with ship management companies

### When to Introduce IoT Infrastructure

**Not before Phase 3, and only if:**
1. A real vessel operator requests Signal K integration
2. Arne has physical access to test hardware (NMEA network, AIS receiver)
3. The core platform is stable and used by real people

IoT is a trap for solo developers: expensive hardware, complex debugging, no users until installed on a real vessel. The COLREGS engine, rest hours logger, and training platform create far more value with zero hardware.

---

## 5. Component Architecture (Target State)

```
GitHub Organization: Seaforge/

Repositories:
  seaforge/platform          # Main web app (Flask + SQLite + Leaflet)
  seaforge/colregs           # COLREGS engine (pure Python library)
  seaforge/mlc               # MLC rest hours calculator (pure Python library)
  seaforge/nmea              # NMEA 0183 parser (pure Python library)
  seaforge/trainer           # Standalone COLREGS trainer web app
  seaforge/vault             # Compliance vault plugin (premium, source-available)
  seaforge/fleet-data        # Community-maintained fleet/vessel database (JSON)
  seaforge/docs              # Documentation site

Package Distribution:
  PyPI: seaforge-colregs, seaforge-mlc, seaforge-nmea
  Docker Hub: seaforge/platform
  npm: (none needed -- vanilla JS frontend)
```

### Dependency Graph

```
seaforge-colregs (zero deps)     seaforge-mlc (zero deps)
        |                               |
        v                               v
  COLREGS trainer                 Rest hours logger
        |                               |
        +---------- platform -----------+
                       |
            +----------+----------+
            |          |          |
         weather     AIS      fleet-data
            |          |
            +----+-----+
                 |
              Signal K (Phase 4+)
                 |
              Vault (Phase 3+)
```

Key principle: **arrows only point down.** Upper modules never depend on lower ones. The COLREGS engine does not know about Flask. The MLC calculator does not know about SQLite. The platform imports both, but they exist independently.

---

## 6. Six-Month Roadmap

```
Month 1 (Apr 2026)
  [x] Extract seaforge-colregs as standalone library
  [x] Build rest hours logger (MLC compliant)
  [x] Build watch handover notes
  [ ] Mobile-responsive UI for MVP features

Month 2 (May 2026)
  [ ] Extract seaforge-mlc as standalone library
  [ ] COLREGS trainer: scoring + progress tracking
  [ ] Publish pip packages (seaforge-colregs, seaforge-mlc)
  [ ] Marketing: Reddit, LinkedIn, maritime forums
  [ ] Deploy hosted COLREGS trainer demo (free tier hosting)

Month 3 (Jun 2026)
  [ ] Contact 5 maritime academies with COLREGS trainer pitch
  [ ] Build instructor dashboard (if interest confirmed)
  [ ] Arne: 30+ days of rest hours data -- analyze, iterate
  [ ] Apply to 1-2 maritime grants (EU, Dutch Maritime Fund)

Month 4 (Jul 2026)
  [ ] First paying customer (training center or premium OOW)
  [ ] Based on feedback: choose Phase 2 direction (training vs. personal vs. compliance)
  [ ] Community: first external contributor to seaforge-colregs?

Month 5 (Aug 2026)
  [ ] Phase 2 feature build (direction chosen in Month 4)
  [ ] If compliance: lock the six keystones, build vault Phase 2
  [ ] If training: expand question bank, add sound signals
  [ ] If personal: add map/weather, certificate tracker

Month 6 (Sep 2026)
  [ ] Evaluate: which monetization path is working?
  [ ] Revenue target: EUR 500/month (from any combination of paths)
  [ ] GitHub target: 100 stars, 3+ external contributors
  [ ] Decision: continue solo or seek co-founder/contributor for weak areas
```

---

## 7. Open Questions / Decisions Needed from Arne

These require your judgment -- they cannot be answered by analysis alone.

### Must Decide Now (Before Phase 0)

1. **Rest hours logger scope:** Track only YOUR rest hours, or also allow logging crew rest hours (multi-person)? Single-person is faster to build and matches the "personal tool" positioning. Multi-person is needed for Master/Chief Officer use but adds complexity.

2. **COLREGS trainer: free or freemium?** The trainer is the most marketable feature. Options:
   - A) Fully free (MIT) -- maximum distribution, monetize via academy dashboard
   - B) Free with limits (10 scenarios/day free, unlimited paid) -- faster revenue
   - C) Fully free core, paid certificate/scoring -- hybrid

3. **Library extraction timing:** Extract `seaforge-colregs` and `seaforge-mlc` as separate repos now (clean but slows platform development) or later (faster platform progress but messier extraction)?

4. **Compliance vault: pause or continue?** The six keystones are serious architectural work. Recommendation: **pause until Month 5+** unless a compliance customer appears. The vault is enterprise-grade infrastructure for a tool that has zero users. Build the personal tool first.

### Decide by Month 3

5. **Hosting model for trainer demo:** Self-hosted on Hetzner VPS (planned infrastructure) or free-tier cloud (Railway, Fly.io, Render)? VPS gives more control but costs EUR 5-10/month.

6. **Academy pricing:** What is a maritime training center willing to pay? Need real conversations with 2-3 academies before setting prices. The EUR 10/student/month above is a guess.

7. **Grant applications:** Which grants to pursue? Options:
   - EU Horizon Europe -- Maritime digitalization (large, competitive, slow)
   - ITF Seafarers' Trust -- Crew welfare (targeted, smaller, faster)
   - Dutch STC Group -- Maritime innovation (local connection via Arne?)
   - National maritime authorities -- Safety innovation funds

### Decide by Month 6

8. **Co-founder:** SeaForge needs at least two of: maritime expertise (Arne), full-stack development (Arne), business/sales (missing), UX design (missing). At what point do you actively seek a co-founder or collaborator?

9. **Open core boundary:** Where exactly is the line between MIT (free) and premium (paid)? Current thinking: core platform free, compliance vault and fleet dashboard paid. But this might shift based on what actually gets traction.

10. **Vessel testing:** Can you get SeaForge onto a real vessel for testing? Even a 2-week trip as a cadet/observer with a tablet running SeaForge would generate invaluable feedback. When is this feasible?

---

## Summary: The Three Rules

1. **Personal before enterprise.** Build for one OOW on one tablet before thinking about fleet management or compliance vaults. The compliance vault is important but premature.

2. **Library before platform.** Extract the COLREGS engine and MLC calculator as standalone packages. They are the fastest path to community awareness and the cleanest architecture decision.

3. **Revenue before features.** One paying academy customer using the COLREGS trainer is worth more than ten unfinished features. Ship the trainer, sell it, iterate.

---

*Built at sea. For those at sea.*
