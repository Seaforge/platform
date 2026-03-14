# SeaForge

**The open-source life-at-sea platform.** Navigation intelligence, wellbeing, training, and daily operations — owned by the seafarer, running on their own hardware.

SeaForge combines real-time maritime intelligence (AIS, weather, COLREGS) with personal wellbeing tracking, drill management, and cadet training tools into a single self-hosted platform that works offline at sea.

---

## Why SeaForge?

Maritime software is either **free but fragmented** (OpenCPN for charts, a weather app, a separate AIS tracker, a PDF of COLREGS) or **enterprise and expensive** ($50K+/year for systems like NAPA or Orca AI). Nothing exists in between for the working seafarer who wants unified decision support on their own tablet.

SeaForge fills that gap:

- **Self-hosted** — Your data, your hardware, your rules. Runs on a laptop, tablet, or Raspberry Pi.
- **Offline-first** — Downloads weather and chart data when connected, works fully offline at sea.
- **Free and open source** — Core platform is MIT licensed. Run it, modify it, contribute back.
- **Built by a seafarer** — Created during an actual cadetship on a tug in the Baltic Sea.

---

## Features

### Navigation Intelligence
- **Live AIS tracking** via [aisstream.io](https://aisstream.io) (free API)
- **Weather overlays** — wind, waves, currents, rain radar, SST (all free: Open-Meteo, RainViewer, NOAA)
- **COLREGS engine** — Real-time encounter classification (Rules 13-15), CPA/TCPA computation
- **Fleet tracking** — Toggle carrier fleets on the map (CMB.TECH, DEME, Heerema, and custom)
- **Chart layers** — Bathymetry, MPA/EEZ boundaries, nautical marks (EMODnet, OpenSeaMap)
- **Anchor watch** — GPS-based swing circle alarm

### Training & Certification
- **COLREGS trainer** — Interactive lights & shapes quiz with scoring
- **CTRB tracker** — Cadet Training Record Book task completion
- **Drill manager** — Schedule, log, and track mandatory drills (fire, abandon ship, MOB, SOPEP)
- **Exam prep** — STCW competency tracking with gap analysis

### Wellbeing & Personal
- **Rest hours logger** — MLC 2006 compliant (10h/24h, 77h/7d minimum). Visual warnings when approaching limits.
- **Workout tracker** — Log exercises, track progress. Adapted for ship gym / bodyweight routines.
- **Meal logger** — Track nutrition, note galley meals, dietary goals
- **Mood & energy journal** — Quick daily check-ins for mental health awareness at sea
- **Personal coach** — Weekly summaries, habit streaks, recovery recommendations

### Daily Operations
- **Task manager** — Daily work list, maintenance rounds, standing orders
- **Watch schedule** — Plan and track OOW watches with handover notes
- **Voyage log** — Position, weather, events, fuel — all in one timeline
- **Admin tracker** — Port papers, certificates, inspections, due dates

---

## Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- That's it. No other dependencies needed.

### One-command setup

```bash
git clone https://github.com/SeaForge/platform.git
cd platform
cp .env.example .env          # review and adjust if needed
docker compose up -d
```

Open `http://localhost:5000` in your browser. Done.

### What's running

| Service | Port | Purpose |
|---------|------|---------|
| **seaforge** | 5000 | Web UI + API |
| **db** | — | SQLite (embedded, no separate service) |

One container. One database file. Back up your data by copying `data/seaforge.db`.

---

## Architecture

```
SeaForge runs as a single Docker container with an embedded SQLite database.
No cloud dependency. No account required. Your data stays on your device.

┌─────────────────────────────────────────────────────┐
│                  Your Device                         │
│               (laptop / tablet / Pi)                 │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │            SeaForge Container                │    │
│  │                                              │    │
│  │  Flask API ──── SQLite DB                    │    │
│  │    │              (data/seaforge.db)          │    │
│  │    ├── AIS engine (aisstream.io WebSocket)   │    │
│  │    ├── COLREGS engine (pure math, no deps)   │    │
│  │    ├── Weather (Open-Meteo, free)            │    │
│  │    ├── Wellbeing (rest hours, meals, mood)   │    │
│  │    ├── Training (COLREGS quiz, CTRB, drills) │    │
│  │    └── Ops (tasks, watch log, admin)         │    │
│  │                                              │    │
│  │  Leaflet Map ── OpenStreetMap / CartoDB tiles│    │
│  │    ├── AIS vessel overlay                    │    │
│  │    ├── Weather layers (wind, waves, rain)    │    │
│  │    ├── Chart data (bathymetry, MPA, EEZ)     │    │
│  │    └── Fleet markers                         │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  Data is YOURS:                                      │
│  • Copy data/seaforge.db to back up everything       │
│  • Export to JSON/CSV anytime via API                 │
│  • No cloud, no login, no tracking                   │
└─────────────────────────────────────────────────────┘
```

### Free APIs Used (No Keys Required)

| API | Data | Docs |
|-----|------|------|
| [Open-Meteo](https://open-meteo.com) | Wind, waves, currents, marine forecast | open-meteo.com/en/docs |
| [RainViewer](https://www.rainviewer.com/api.html) | Rain radar imagery | rainviewer.com/api |
| [EMODnet](https://emodnet.ec.europa.eu) | Bathymetry (WMS) | emodnet.ec.europa.eu |
| [NOAA ERDDAP](https://coastwatch.pfeg.noaa.gov/erddap/) | Sea surface temperature (WMS) | NOAA CoastWatch |
| [Marine Regions VLIZ](https://marineregions.org) | MPA, EEZ boundaries (WMS) | marineregions.org |
| [OpenSeaMap](https://www.openseamap.org) | Nautical marks, harbors | openseamap.org |
| [aisstream.io](https://aisstream.io) | Live AIS data (free signup) | aisstream.io/documentation |

### Signal K Integration (Optional)

If you have a Signal K server connected to your vessel's NMEA network, SeaForge can read real AIS, GPS, wind, and depth data directly. See [docs/signalk.md](docs/signalk.md).

---

## Project Structure

```
seaforge/
├── src/
│   ├── api/              # REST API routes
│   │   ├── navigation.py # AIS, COLREGS, fleet endpoints
│   │   ├── wellbeing.py  # Rest hours, meals, workouts, mood
│   │   ├── training.py   # COLREGS quiz, CTRB, drills
│   │   └── ops.py        # Tasks, watch log, admin
│   ├── core/             # Business logic
│   │   ├── colregs.py    # COLREGS classification engine
│   │   ├── weather.py    # Weather data fetching
│   │   └── ais.py        # AIS stream processing
│   └── data/             # Data layer
│       ├── models.py     # SQLite schema / ORM
│       ├── fleet_db.py   # Carrier fleet database
│       └── lights_db.py  # Lights & shapes scenarios
├── static/               # Frontend assets
│   ├── js/app.js         # Main application JS
│   └── css/style.css     # Styles
├── templates/            # Jinja2 HTML templates
│   └── index.html        # Main SPA shell
├── migrations/           # Database migrations
├── data/                 # Runtime data (SQLite DB, user uploads)
├── docs/                 # Documentation
├── scripts/              # Setup and utility scripts
├── Dockerfile
├── compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## MLC Rest Hours Compliance

SeaForge implements the Maritime Labour Convention (MLC 2006) rest hour rules:

- **Minimum 10 hours rest in any 24-hour period**
- **Minimum 77 hours rest in any 7-day period**
- Rest may be divided into no more than two periods, one of which must be at least 6 hours
- Maximum 14 hours between rest periods

The rest hours dashboard shows:
- Current compliance status (green/amber/red)
- Rolling 24h and 7-day totals
- Visual timeline of work/rest periods
- Automatic warnings when approaching limits
- Export for PSC inspection records

---

## Drill Management

Mandatory drill tracking per SOLAS and ISM Code:

| Drill Type | Frequency | SeaForge Feature |
|-----------|-----------|------------------|
| Fire & Emergency | Monthly | Schedule, log, track crew participation |
| Abandon Ship | Monthly | Muster list integration, completion records |
| Man Overboard (MOB) | Monthly | Log response times, lessons learned |
| SOPEP (Oil Spill) | Monthly | Equipment checks, notification procedure drill |
| Security (ISPS) | Quarterly | PFSO drill requirements tracking |
| Damage Control | As required | Custom scheduling |

---

## Roadmap

### Phase 1 — Core Platform (Current)
- [x] Maritime map with weather overlays
- [x] COLREGS engine (CPA/TCPA, encounter classification)
- [x] Fleet database with carrier tracking
- [x] Lights & shapes trainer
- [x] Anchor watch
- [ ] SQLite database layer
- [ ] Rest hours logger (MLC compliant)
- [ ] Workout & meal tracker
- [ ] Drill manager
- [ ] Task manager
- [ ] Watch schedule planner

### Phase 2 — Intelligence
- [ ] Live AIS via aisstream.io
- [ ] Signal K integration
- [ ] Voyage logging
- [ ] Offline weather data caching (GRIB)
- [ ] CTRB progress tracker

### Phase 3 — Coaching
- [ ] Weekly wellbeing summaries
- [ ] Training progress analytics
- [ ] Drill gap analysis
- [ ] Certificate expiry alerts
- [ ] Personal development goals

---

## Contributing

SeaForge is built by seafarers, for seafarers. Contributions welcome.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests: `docker compose run --rm seaforge python -m pytest`
5. Submit a PR

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## License

**MIT License** — Use it, modify it, deploy it, sell services on top of it. Just keep the attribution.

See [LICENSE](LICENSE) for full text.

---

## Acknowledgments

- [OpenCPN](https://www.opencpn.org/) — The pioneer of open-source maritime navigation
- [Signal K](https://signalk.org/) — The open marine data standard
- [aisstream.io](https://aisstream.io/) — Free global AIS data
- [Open-Meteo](https://open-meteo.com/) — Free weather API
- [OpenSeaMap](https://www.openseamap.org/) — Community nautical charts

---

*Built at sea. For those at sea.*
