#!/usr/bin/env python3
"""
Migration script to update drills table to match F5 Drill Log specification.
Run with: python migrations/drill_log_schema_update.py
"""

import sqlite3
import os

DB_PATH = os.environ.get("SEAFORGE_DB_PATH", "data/seaforge.db")

def migrate_drills_table():
    """Update drills table schema to match F5 spec."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Rename existing table to backup
    cursor.execute("ALTER TABLE drills RENAME TO drills_old")
    
    # 2. Create new table with updated schema
    cursor.execute("""
        CREATE TABLE drills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            conducted_at TEXT NOT NULL,
            duration_mins INTEGER NOT NULL,
            participant_count INTEGER DEFAULT 1,
            outcome TEXT NOT NULL DEFAULT 'satisfactory',
            officer_in_charge TEXT,
            notes TEXT,
            ctrb_section_ref TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # 3. Copy data from old table, mapping fields
    cursor.execute("""
        INSERT INTO drills (
            id, type, conducted_at, duration_mins, participant_count,
            outcome, officer_in_charge, notes, ctrb_section_ref, created_at
        )
        SELECT 
            id,
            type,
            date,
            COALESCE(duration_min, 30),
            CASE 
                WHEN participants IS NULL OR participants = '' THEN 1
                ELSE CAST(participants AS INTEGER)
            END,
            CASE 
                WHEN status = 'completed' THEN 'satisfactory'
                WHEN status = 'cancelled' THEN 'unsatisfactory'
                ELSE 'satisfactory'
            END,
            NULL,
            COALESCE(scenario, '') || COALESCE(' ' || lessons_learned, ''),
            NULL,
            created_at
        FROM drills_old
    """)
    
    # 4. Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_drills_conducted_at ON drills(conducted_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_drills_type ON drills(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_drills_outcome ON drills(outcome)")
    
    # 5. Optionally drop old table (uncomment when ready)
    # cursor.execute("DROP TABLE drills_old")
    
    conn.commit()
    
    # Verify migration
    cursor.execute("PRAGMA table_info(drills)")
    columns = cursor.fetchall()
    print("New drills table schema:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    cursor.execute("SELECT COUNT(*) FROM drills")
    count = cursor.fetchone()[0]
    print(f"\nMigrated {count} drill records.")
    
    conn.close()
    
    print("\nMigration complete. Old table saved as 'drills_old'.")
    print("Review the data, then uncomment the DROP TABLE line if everything looks good.")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        exit(1)
    
    migrate_drills_table()