"""SeaForge compliance vault schema — append-only, integrity-protected."""

import sqlite3
import os
from pathlib import Path

VAULT_DB_PATH = os.environ.get("SEAFORGE_VAULT_DB_PATH", "data/compliance_vault.db")


def get_vault_db() -> sqlite3.Connection:
    """Get a database connection to the compliance vault."""
    Path(VAULT_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(VAULT_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_vault_db():
    """Create all compliance vault tables if they don't exist."""
    conn = get_vault_db()
    conn.executescript(VAULT_SCHEMA)
    conn.close()


VAULT_SCHEMA = """
-- ════════════════════════════════════════════════════════
-- COMPLIANCE VAULT — APPEND-ONLY AUDIT TRAIL
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL DEFAULT (datetime('now')),
    event TEXT NOT NULL,                    -- WRITE | READ | EXPORT | ATTEMPT_DELETE
    table_name TEXT,
    record_id INTEGER,
    endpoint TEXT,
    ip TEXT,
    details TEXT
);

-- PREVENT deletion of audit log (append-only enforcement)
CREATE TRIGGER IF NOT EXISTS audit_log_no_delete BEFORE DELETE ON audit_log
BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;

-- ════════════════════════════════════════════════════════
-- MLC 2006 — REST HOURS RECORDS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS rest_hours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'rest',     -- rest | work | standby
    notes TEXT,
    record_hash TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_vault_rest_hours_date ON rest_hours(date);

-- ════════════════════════════════════════════════════════
-- SOLAS / ISM — DRILL RECORDS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS drills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conducted_at TEXT NOT NULL,
    type TEXT NOT NULL,                     -- fire | abandon_ship | mob | sopep | security | damage_control | custom
    title TEXT NOT NULL,
    scenario TEXT,
    duration_mins INTEGER,
    participant_count INTEGER,
    participants TEXT,
    officer_in_charge TEXT NOT NULL,
    outcome TEXT,                           -- pass | needs_improvement | failed
    lessons_learned TEXT,
    ctrb_section_ref TEXT,
    next_drill_due TEXT,
    status TEXT DEFAULT 'completed',        -- completed | cancelled
    record_hash TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_vault_drills_type ON drills(type);
CREATE INDEX IF NOT EXISTS idx_vault_drills_conducted ON drills(conducted_at);

-- ════════════════════════════════════════════════════════
-- STCW — TRAINING RECORDS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS ctrb_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL UNIQUE,
    section TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending',         -- pending | in_progress | completed | signed_off
    evidence TEXT,
    completed_date TEXT,
    signed_off_by TEXT,
    record_hash TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    issuer TEXT,
    issue_date TEXT,
    expiry_date TEXT,
    certificate_number TEXT,
    notes TEXT,
    record_hash TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_vault_certificates_expiry ON certificates(expiry_date);

-- ════════════════════════════════════════════════════════
-- OPERATIONAL LOGS (watch, voyage)
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS watch_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    watch_start TEXT NOT NULL,
    watch_end TEXT NOT NULL,
    position_lat REAL,
    position_lon REAL,
    course REAL,
    speed REAL,
    weather TEXT,
    wind_direction TEXT,
    wind_force INTEGER,
    sea_state INTEGER,
    visibility_nm REAL,
    events TEXT,
    handover_notes TEXT,
    record_hash TEXT,
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
    fuel_rob REAL,
    distance_run REAL,
    notes TEXT,
    record_hash TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_vault_watch_log_date ON watch_log(date);
CREATE INDEX IF NOT EXISTS idx_vault_voyage_log_ts ON voyage_log(timestamp);

-- ════════════════════════════════════════════════════════
-- MASS / ROC — AUTONOMOUS VESSEL & REMOTE OPERATIONS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS roc_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    operator_id TEXT NOT NULL,
    vessel_id TEXT NOT NULL,
    login_at TEXT NOT NULL DEFAULT (datetime('now')),
    logout_at TEXT,
    mode TEXT NOT NULL,                     -- monitoring | supervisory | direct_control
    handover_from TEXT,
    vessel_state_snapshot TEXT,             -- JSON snapshot at login
    record_hash TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TRIGGER IF NOT EXISTS roc_sessions_no_delete BEFORE DELETE ON roc_sessions
BEGIN SELECT RAISE(ABORT, 'roc_sessions is append-only'); END;

-- Only logout_at may be updated via dedicated PATCH endpoint
CREATE TRIGGER IF NOT EXISTS roc_sessions_restrict_update BEFORE UPDATE ON roc_sessions
    WHEN OLD.logout_at IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'roc_sessions: session already closed'); END;

CREATE TABLE IF NOT EXISTS roc_interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES roc_sessions(session_id),
    ts TEXT NOT NULL DEFAULT (datetime('now')),
    vessel_id TEXT NOT NULL,
    intervention_type TEXT NOT NULL,       -- course_change | speed_change | emergency_stop | takeover | handback | alert_ack
    reason TEXT,
    details TEXT,                          -- JSON: from_value, to_value, alert_id, etc.
    outcome TEXT,
    record_hash TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TRIGGER IF NOT EXISTS roc_interventions_no_delete BEFORE DELETE ON roc_interventions
BEGIN SELECT RAISE(ABORT, 'append-only'); END;

CREATE INDEX IF NOT EXISTS idx_vault_roc_sessions_operator ON roc_sessions(operator_id);
CREATE INDEX IF NOT EXISTS idx_vault_roc_sessions_vessel ON roc_sessions(vessel_id);
CREATE INDEX IF NOT EXISTS idx_vault_roc_interventions_session ON roc_interventions(session_id);

CREATE TABLE IF NOT EXISTS autonomy_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL DEFAULT (datetime('now')),
    vessel_id TEXT NOT NULL,
    from_mode TEXT,                        -- crewed | supervised | autonomous | emergency
    to_mode TEXT NOT NULL,
    trigger_event TEXT,                    -- manual | sensor_failure | comms_loss | geofence | scheduled
    triggered_by TEXT,                     -- operator_id or 'system'
    position_lat REAL,
    position_lon REAL,
    notes TEXT,
    record_hash TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TRIGGER IF NOT EXISTS autonomy_events_no_delete BEFORE DELETE ON autonomy_events
BEGIN SELECT RAISE(ABORT, 'append-only'); END;

CREATE INDEX IF NOT EXISTS idx_vault_autonomy_vessel ON autonomy_events(vessel_id);
CREATE INDEX IF NOT EXISTS idx_vault_autonomy_ts ON autonomy_events(ts);

-- ════════════════════════════════════════════════════════
-- ISM CODE — NON-CONFORMITY REPORTS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS non_conformities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ncr_number TEXT NOT NULL UNIQUE,       -- e.g. NCR-2026-001
    raised_at TEXT NOT NULL DEFAULT (datetime('now')),
    raised_by TEXT NOT NULL,
    category TEXT NOT NULL,                -- navigational | structural | safety_equipment | environmental | operational
    description TEXT NOT NULL,
    possible_cause TEXT,
    vessel_position TEXT,
    status TEXT DEFAULT 'open',            -- open | under_investigation | corrective_action | closed
    corrective_action TEXT,
    closed_at TEXT,
    closed_by TEXT,
    record_hash TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_vault_ncr_status ON non_conformities(status);
CREATE INDEX IF NOT EXISTS idx_vault_ncr_raised ON non_conformities(raised_at);

-- ════════════════════════════════════════════════════════
-- CYBER SECURITY — MSC.428(98), IACS UR E26/E27
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS cyber_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL DEFAULT (datetime('now')),
    event_type TEXT NOT NULL,              -- access | incident | firmware_update | third_party_session | backup
    system TEXT,
    actor TEXT,
    details TEXT,                          -- JSON
    severity TEXT,                         -- info | low | medium | high | critical
    record_hash TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TRIGGER IF NOT EXISTS cyber_events_no_delete BEFORE DELETE ON cyber_events
BEGIN SELECT RAISE(ABORT, 'append-only'); END;

CREATE INDEX IF NOT EXISTS idx_vault_cyber_type ON cyber_events(event_type);
CREATE INDEX IF NOT EXISTS idx_vault_cyber_ts ON cyber_events(ts);
"""
