"""Operations API — tasks, watch log, voyage log."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from ..data.models import get_db

bp = Blueprint("ops", __name__, url_prefix="/api/ops")


# ── Tasks ────────────────────────────────────────────────────

@bp.route("/tasks", methods=["GET"])
def get_tasks():
    db = get_db()
    status = request.args.get("status")
    date = request.args.get("date")

    query = "SELECT * FROM tasks"
    params = []
    conditions = []
    if status:
        conditions.append("status = ?")
        params.append(status)
    if date:
        conditions.append("date = ?")
        params.append(date)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END, created_at DESC"

    rows = db.execute(query, params).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    db = get_db()
    db.execute(
        "INSERT INTO tasks (date, title, description, category, priority, status, due_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (data.get("date"), data["title"], data.get("description"),
         data.get("category", "general"), data.get("priority", "normal"),
         data.get("status", "todo"), data.get("due_date"))
    )
    db.commit()
    db.close()
    return jsonify({"status": "ok"}), 201


@bp.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    data = request.json
    db = get_db()
    updates = []
    params = []
    for field in ["status", "title", "description", "priority", "due_date"]:
        if field in data:
            updates.append(f"{field} = ?")
            params.append(data[field])
    if data.get("status") == "done":
        updates.append("completed_at = ?")
        params.append(datetime.now().isoformat())
    params.append(task_id)
    db.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params)
    db.commit()
    db.close()
    return jsonify({"status": "ok"})


@bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    db.close()
    return jsonify({"status": "ok"})


# ── Watch Log ────────────────────────────────────────────────

@bp.route("/watch-log", methods=["GET"])
def get_watch_log():
    db = get_db()
    limit = int(request.args.get("limit", 20))
    rows = db.execute("SELECT * FROM watch_log ORDER BY date DESC, watch_start DESC LIMIT ?", (limit,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/watch-log", methods=["POST"])
def add_watch_log():
    data = request.json
    db = get_db()
    db.execute(
        """INSERT INTO watch_log (date, watch_start, watch_end, position_lat, position_lon,
           course, speed, weather, wind_direction, wind_force, sea_state,
           visibility_nm, events, handover_notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (data["date"], data["watch_start"], data["watch_end"],
         data.get("position_lat"), data.get("position_lon"),
         data.get("course"), data.get("speed"), data.get("weather"),
         data.get("wind_direction"), data.get("wind_force"), data.get("sea_state"),
         data.get("visibility_nm"), data.get("events"), data.get("handover_notes"))
    )
    db.commit()
    db.close()
    return jsonify({"status": "ok"}), 201


# ── Voyage Log ───────────────────────────────────────────────

@bp.route("/voyage-log", methods=["GET"])
def get_voyage_log():
    db = get_db()
    limit = int(request.args.get("limit", 50))
    rows = db.execute("SELECT * FROM voyage_log ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/voyage-log", methods=["POST"])
def add_voyage_entry():
    data = request.json
    db = get_db()
    db.execute(
        """INSERT INTO voyage_log (timestamp, event_type, port, position_lat, position_lon,
           course, speed, fuel_rob, distance_run, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (data["timestamp"], data["event_type"], data.get("port"),
         data.get("position_lat"), data.get("position_lon"),
         data.get("course"), data.get("speed"), data.get("fuel_rob"),
         data.get("distance_run"), data.get("notes"))
    )
    db.commit()
    db.close()
    return jsonify({"status": "ok"}), 201


# ── Data Export ──────────────────────────────────────────────

@bp.route("/export/<table>", methods=["GET"])
def export_table(table):
    """Export any table as JSON for backup or inspection."""
    allowed = ["rest_hours", "workouts", "meals", "mood_logs", "tasks",
               "watch_log", "voyage_log", "drills", "certificates",
               "ctrb_tasks", "colregs_scores"]
    if table not in allowed:
        return jsonify({"error": f"Unknown table: {table}"}), 404
    db = get_db()
    rows = db.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])
import json

from flask import Blueprint, request, jsonify

phase_state = {"currentPhase": "Pre-Tow"}

@bp.route("/phase", methods=["GET"])
def get_phase():
    return jsonify(phase_state)

@bp.route("/phase", methods=["POST"])
def set_phase():
    data = request.json
    if "phase" in data:
        phase_state["currentPhase"] = data["phase"]
    return jsonify({"status": "ok", "currentPhase": phase_state["currentPhase"]})
