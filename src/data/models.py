"""SeaForge database schema — SQLite with raw SQL for zero dependencies."""

import sqlite3
import os
from pathlib import Path

DB_PATH = os.environ.get("SEAFORGE_DB_PATH", "data/seaforge.db")


def get_db() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_db()
    conn.executescript(SCHEMA)
    conn.close()


SCHEMA = """
-- ════════════════════════════════════════════════════════
-- WELLBEING
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS rest_hours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,                    -- ISO date (2026-03-14)
    start_time TEXT NOT NULL,              -- HH:MM (24h)
    end_time TEXT NOT NULL,                -- HH:MM (24h)
    type TEXT NOT NULL DEFAULT 'rest',     -- rest | work | standby
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    type TEXT NOT NULL,                    -- cardio | strength | flexibility | bodyweight
    exercise TEXT NOT NULL,                -- e.g. "push-ups", "rowing machine", "running"
    duration_min INTEGER,
    sets INTEGER,
    reps INTEGER,
    weight_kg REAL,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    meal_type TEXT NOT NULL,               -- breakfast | lunch | dinner | snack
    description TEXT NOT NULL,
    calories INTEGER,
    protein_g REAL,
    is_galley INTEGER DEFAULT 1,           -- 1 = ship galley, 0 = own food
    rating INTEGER,                        -- 1-5 quality rating
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS mood_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    time TEXT,                             -- HH:MM
    energy INTEGER NOT NULL CHECK(energy BETWEEN 1 AND 5),
    mood INTEGER NOT NULL CHECK(mood BETWEEN 1 AND 5),
    sleep_quality INTEGER CHECK(sleep_quality BETWEEN 1 AND 5),
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- ════════════════════════════════════════════════════════
-- TRAINING & CERTIFICATION
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS colregs_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,                -- lights | shapes | encounters | rules
    total_questions INTEGER NOT NULL,
    correct INTEGER NOT NULL,
    time_seconds INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ctrb_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL UNIQUE,           -- e.g. "NAV-01", "CARGO-03"
    section TEXT NOT NULL,                  -- Navigation, Cargo, Safety, ...
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending',          -- pending | in_progress | completed | signed_off
    evidence TEXT,                          -- notes / proof of completion
    completed_date TEXT,
    signed_off_by TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS drills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    type TEXT NOT NULL,                     -- fire | abandon_ship | mob | sopep | security | damage_control | custom
    title TEXT NOT NULL,
    scenario TEXT,
    participants TEXT,                      -- comma-separated names or count
    duration_min INTEGER,
    lessons_learned TEXT,
    next_drill_due TEXT,                    -- ISO date
    status TEXT DEFAULT 'scheduled',        -- scheduled | completed | cancelled
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                     -- e.g. "STCW Basic Safety", "GMDSS GOC"
    issuer TEXT,
    issue_date TEXT,
    expiry_date TEXT,
    certificate_number TEXT,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- ════════════════════════════════════════════════════════
-- DAILY OPERATIONS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT DEFAULT 'general',        -- general | maintenance | safety | admin | personal
    priority TEXT DEFAULT 'normal',         -- low | normal | high | urgent
    status TEXT DEFAULT 'todo',             -- todo | in_progress | done | cancelled
    due_date TEXT,
    completed_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS watch_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    watch_start TEXT NOT NULL,              -- HH:MM
    watch_end TEXT NOT NULL,                -- HH:MM
    position_lat REAL,
    position_lon REAL,
    course REAL,
    speed REAL,
    weather TEXT,                           -- brief description
    wind_direction TEXT,
    wind_force INTEGER,                    -- Beaufort
    sea_state INTEGER,
    visibility_nm REAL,
    events TEXT,                            -- notable events during watch
    handover_notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS voyage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,               -- departure | arrival | noon_report | event | bunkering
    port TEXT,
    position_lat REAL,
    position_lon REAL,
    course REAL,
    speed REAL,
    fuel_rob REAL,                         -- remaining on board (MT)
    distance_run REAL,                     -- since last entry (NM)
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- ════════════════════════════════════════════════════════
-- INDEXES
-- ════════════════════════════════════════════════════════

CREATE INDEX IF NOT EXISTS idx_rest_hours_date ON rest_hours(date);
CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date);
CREATE INDEX IF NOT EXISTS idx_meals_date ON meals(date);
CREATE INDEX IF NOT EXISTS idx_mood_date ON mood_logs(date);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(date);
CREATE INDEX IF NOT EXISTS idx_drills_date ON drills(date);
CREATE INDEX IF NOT EXISTS idx_drills_type ON drills(type);
CREATE INDEX IF NOT EXISTS idx_watch_log_date ON watch_log(date);
CREATE INDEX IF NOT EXISTS idx_voyage_log_ts ON voyage_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_ctrb_status ON ctrb_tasks(status);
CREATE INDEX IF NOT EXISTS idx_certificates_expiry ON certificates(expiry_date);
"""
