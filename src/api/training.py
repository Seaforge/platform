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
    status = request.args.get("status")
    if status:
        rows = db.execute("SELECT * FROM drills WHERE status = ? ORDER BY date DESC", (status,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM drills ORDER BY date DESC LIMIT 50").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/drills", methods=["POST"])
def add_drill():
    data = request.json
    db = get_db()
    db.execute(
        "INSERT INTO drills (date, type, title, scenario, participants, duration_min, lessons_learned, next_drill_due, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (data["date"], data["type"], data["title"], data.get("scenario"),
         data.get("participants"), data.get("duration_min"), data.get("lessons_learned"),
         data.get("next_drill_due"), data.get("status", "scheduled"))
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
    for field in ["status", "lessons_learned", "duration_min", "participants"]:
        if field in data:
            updates.append(f"{field} = ?")
            params.append(data[field])
    params.append(drill_id)
    db.execute(f"UPDATE drills SET {', '.join(updates)} WHERE id = ?", params)
    db.commit()
    db.close()
    return jsonify({"status": "ok"})


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
