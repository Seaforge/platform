"""Wellbeing API — rest hours, workouts, meals, mood tracking."""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from ..data.models import get_db

bp = Blueprint("wellbeing", __name__, url_prefix="/api/wellbeing")


# ── Rest Hours (MLC 2006 Compliant) ──────────────────────────

@bp.route("/rest-hours", methods=["GET"])
def get_rest_hours():
    """Get rest hours for a date range. Default: last 7 days."""
    db = get_db()
    end = request.args.get("end", datetime.now().strftime("%Y-%m-%d"))
    start = request.args.get("start", (datetime.strptime(end, "%Y-%m-%d") - timedelta(days=6)).strftime("%Y-%m-%d"))
    rows = db.execute(
        "SELECT * FROM rest_hours WHERE date BETWEEN ? AND ? ORDER BY date, start_time",
        (start, end)
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/rest-hours", methods=["POST"])
def add_rest_hours():
    """Log a rest/work period."""
    data = request.json
    db = get_db()
    db.execute(
        "INSERT INTO rest_hours (date, start_time, end_time, type, notes) VALUES (?, ?, ?, ?, ?)",
        (data["date"], data["start_time"], data["end_time"], data.get("type", "rest"), data.get("notes"))
    )
    db.commit()
    db.close()
    return jsonify({"status": "ok"}), 201


@bp.route("/rest-hours/compliance", methods=["GET"])
def rest_hours_compliance():
    """Check MLC rest hour compliance for current period."""
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")

    rows = db.execute(
        "SELECT * FROM rest_hours WHERE date BETWEEN ? AND ? AND type = 'rest' ORDER BY date, start_time",
        (week_ago, today)
    ).fetchall()
    db.close()

    # Calculate total rest hours in last 24h and 7 days
    total_rest_7d = 0
    total_rest_24h = 0
    now = datetime.now()

    for row in rows:
        start = datetime.strptime(f"{row['date']} {row['start_time']}", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{row['date']} {row['end_time']}", "%Y-%m-%d %H:%M")
        if end < start:
            end += timedelta(days=1)
        hours = (end - start).total_seconds() / 3600
        total_rest_7d += hours
        if (now - start).total_seconds() < 86400:
            total_rest_24h += hours

    # MLC 2006 limits
    compliant_24h = total_rest_24h >= 10
    compliant_7d = total_rest_7d >= 77

    status = "green"
    if not compliant_24h or not compliant_7d:
        status = "red"
    elif total_rest_24h < 12 or total_rest_7d < 84:
        status = "amber"

    return jsonify({
        "status": status,
        "rest_24h": round(total_rest_24h, 1),
        "rest_7d": round(total_rest_7d, 1),
        "compliant_24h": compliant_24h,
        "compliant_7d": compliant_7d,
        "limits": {"min_24h": 10, "min_7d": 77}
    })


# ── Workouts ─────────────────────────────────────────────────

@bp.route("/workouts", methods=["GET"])
def get_workouts():
    db = get_db()
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    rows = db.execute("SELECT * FROM workouts WHERE date = ? ORDER BY created_at", (date,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/workouts", methods=["POST"])
def add_workout():
    data = request.json
    db = get_db()
    db.execute(
        "INSERT INTO workouts (date, type, exercise, duration_min, sets, reps, weight_kg, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (data["date"], data["type"], data["exercise"], data.get("duration_min"),
         data.get("sets"), data.get("reps"), data.get("weight_kg"), data.get("notes"))
    )
    db.commit()
    db.close()
    return jsonify({"status": "ok"}), 201


# ── Meals ────────────────────────────────────────────────────

@bp.route("/meals", methods=["GET"])
def get_meals():
    db = get_db()
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    rows = db.execute("SELECT * FROM meals WHERE date = ? ORDER BY created_at", (date,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/meals", methods=["POST"])
def add_meal():
    data = request.json
    db = get_db()
    db.execute(
        "INSERT INTO meals (date, meal_type, description, calories, protein_g, is_galley, rating, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (data["date"], data["meal_type"], data["description"], data.get("calories"),
         data.get("protein_g"), data.get("is_galley", 1), data.get("rating"), data.get("notes"))
    )
    db.commit()
    db.close()
    return jsonify({"status": "ok"}), 201


# ── Mood & Energy ────────────────────────────────────────────

@bp.route("/mood", methods=["GET"])
def get_mood():
    db = get_db()
    days = int(request.args.get("days", 7))
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    rows = db.execute("SELECT * FROM mood_logs WHERE date >= ? ORDER BY date, time", (start,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/mood", methods=["POST"])
def add_mood():
    data = request.json
    db = get_db()
    db.execute(
        "INSERT INTO mood_logs (date, time, energy, mood, sleep_quality, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (data["date"], data.get("time"), data["energy"], data["mood"],
         data.get("sleep_quality"), data.get("notes"))
    )
    db.commit()
    db.close()
    return jsonify({"status": "ok"}), 201
