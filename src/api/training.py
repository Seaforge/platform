"""Training API — COLREGS scoring, CTRB tracking, drill management."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from ..data.models import get_db

bp = Blueprint("training", __name__, url_prefix="/api/training")


# ── COLREGS Scores ───────────────────────────────────────────

@bp.route("/colregs-scores", methods=["GET"])
def get_scores():
    db = get_db()
    rows = db.execute("SELECT * FROM colregs_scores ORDER BY date DESC LIMIT 50").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/colregs-scores", methods=["POST"])
def add_score():
    data = request.json
    db = get_db()
    db.execute(
        "INSERT INTO colregs_scores (date, category, total_questions, correct, time_seconds) VALUES (?, ?, ?, ?, ?)",
        (data["date"], data["category"], data["total_questions"], data["correct"], data.get("time_seconds"))
    )
    db.commit()
    db.close()
    return jsonify({"status": "ok"}), 201


# ── CTRB Tasks ───────────────────────────────────────────────

@bp.route("/ctrb", methods=["GET"])
def get_ctrb():
    db = get_db()
    section = request.args.get("section")
    status = request.args.get("status")

    query = "SELECT * FROM ctrb_tasks"
    params = []
    conditions = []
    if section:
        conditions.append("section = ?")
        params.append(section)
    if status:
        conditions.append("status = ?")
        params.append(status)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY task_id"

    rows = db.execute(query, params).fetchall()
    db.close()

    # Add summary stats
    all_tasks = db.execute("SELECT status, COUNT(*) as count FROM ctrb_tasks GROUP BY status").fetchall() if not conditions else []
    return jsonify({
        "tasks": [dict(r) for r in rows],
        "total": len(rows),
    })


@bp.route("/ctrb/<task_id>", methods=["PATCH"])
def update_ctrb(task_id):
    data = request.json
    db = get_db()

    updates = []
    params = []
    for field in ["status", "evidence", "completed_date", "signed_off_by"]:
        if field in data:
            updates.append(f"{field} = ?")
            params.append(data[field])
    params.append(task_id)

    db.execute(f"UPDATE ctrb_tasks SET {', '.join(updates)} WHERE task_id = ?", params)
    db.commit()
    db.close()
    return jsonify({"status": "ok"})


# ── Drills ───────────────────────────────────────────────────

@bp.route("/drills", methods=["GET"])
def get_drills():
    db = get_db()
    drill_type = request.args.get("type")
    outcome = request.args.get("outcome")
    limit = int(request.args.get("limit", 50))
    
    query = "SELECT * FROM drills"
    params = []
    conditions = []
    
    if drill_type:
        conditions.append("type = ?")
        params.append(drill_type)
    if outcome:
        conditions.append("outcome = ?")
        params.append(outcome)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY conducted_at DESC LIMIT ?"
    params.append(limit)
    
    rows = db.execute(query, params).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/drills", methods=["POST"])
def add_drill():
    data = request.json

    # Validate required fields
    required = ["type", "conducted_at", "title", "officer_in_charge"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    db = get_db()
    db.execute(
        """INSERT INTO drills
        (type, conducted_at, title, scenario, duration_mins, participant_count, participants,
         outcome, officer_in_charge, lessons_learned, ctrb_section_ref, next_drill_due, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["type"],
            data["conducted_at"],
            data["title"],
            data.get("scenario"),
            data.get("duration_mins"),
            data.get("participant_count"),
            data.get("participants"),
            data.get("outcome"),
            data["officer_in_charge"],
            data.get("lessons_learned"),
            data.get("ctrb_section_ref"),
            data.get("next_drill_due"),
            data.get("status", "completed"),
        )
    )
    db.commit()
    db.close()
    return jsonify({"status": "ok"}), 201


@bp.route("/drills/<int:drill_id>", methods=["PATCH"])
def update_drill(drill_id):
    data = request.json
    db = get_db()

    updates = []
    params = []
    allowed_fields = ["type", "conducted_at", "duration_mins", "participant_count",
                     "outcome", "officer_in_charge", "title", "scenario", "lessons_learned",
                     "ctrb_section_ref", "next_drill_due", "status"]

    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = ?")
            params.append(data[field])

    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    params.append(drill_id)
    db.execute(f"UPDATE drills SET {', '.join(updates)} WHERE id = ?", params)
    db.commit()
    db.close()
    return jsonify({"status": "ok"})


@bp.route("/drills/<int:drill_id>", methods=["DELETE"])
def delete_drill(drill_id):
    # Hard delete is not allowed — drills are compliance records
    return jsonify({"error": "Drill records cannot be deleted. Use status='cancelled' to mark as inactive."}), 405


@bp.route("/drills/frequency", methods=["GET"])
def get_drill_frequency():
    """Return SOLAS frequency requirements for drill types."""
    frequencies = {
        "abandon_ship": "Monthly (all crew within 24h of departure if >25% new crew)",
        "fire": "Monthly (alternating locations on the ship)",
        "mob": "Monthly",
        "flooding": "Monthly (as part of damage control)",
        "oil_spill": "Quarterly (SOPEP)",
        "security": "Quarterly (ISPS)",
        "medical": "As required",
        "anchor": "As required",
        "blackout": "As required",
        "other": "As required",
    }
    return jsonify(frequencies)


# ── Certificates ─────────────────────────────────────────────

@bp.route("/certificates", methods=["GET"])
def get_certificates():
    db = get_db()
    rows = db.execute("SELECT * FROM certificates ORDER BY expiry_date").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/certificates", methods=["POST"])
def add_certificate():
    data = request.json
    db = get_db()
    db.execute(
        "INSERT INTO certificates (name, issuer, issue_date, expiry_date, certificate_number, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (data["name"], data.get("issuer"), data.get("issue_date"),
         data.get("expiry_date"), data.get("certificate_number"), data.get("notes"))
    )
    db.commit()
    db.close()
    return jsonify({"status": "ok"}), 201
