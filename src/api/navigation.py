"""Navigation API — COLREGS, fleet, AIS endpoints."""

from flask import Blueprint, request, jsonify
from ..core.colregs import classify_encounter, compute_cpa_tcpa, bearing_to, range_nm, relative_bearing
from ..data.fleet_db import FLEET_DB
from ..data.lights_db import LIGHTS_DB

bp = Blueprint("navigation", __name__, url_prefix="/api")


@bp.route("/colregs", methods=["POST"])
def colregs_analysis():
    """Classify encounter between own ship and target."""
    data = request.json
    own = data["own"]
    target = data["target"]

    brg = bearing_to(own["lat"], own["lon"], target["lat"], target["lon"])
    dist = range_nm(own["lat"], own["lon"], target["lat"], target["lon"])
    rel_brg = relative_bearing(own["cog"], brg)
    situation, role, rule, action = classify_encounter(own["cog"], target["cog"], rel_brg)
    cpa, tcpa, _, _ = compute_cpa_tcpa(
        own["lat"], own["lon"], own["cog"], own["sog"],
        target["lat"], target["lon"], target["cog"], target["sog"]
    )

    return jsonify({
        "bearing": brg,
        "range_nm": dist,
        "relative_bearing": rel_brg,
        "situation": situation,
        "role": role,
        "rule": rule,
        "action": action,
        "cpa_nm": cpa,
        "tcpa_min": tcpa
    })


@bp.route("/fleet", methods=["GET"])
def get_fleet():
    """Get all fleets or filter by company."""
    company = request.args.get("company")
    if company and company in FLEET_DB:
        return jsonify({company: FLEET_DB[company]})
    return jsonify(FLEET_DB)


@bp.route("/fleet/<company>", methods=["GET"])
def get_fleet_company(company):
    """Get vessels for a specific company."""
    if company not in FLEET_DB:
        return jsonify({"error": f"Unknown company: {company}"}), 404
    return jsonify(FLEET_DB[company])


@bp.route("/lights", methods=["GET"])
def get_lights():
    """Get lights & shapes training scenarios."""
    category = request.args.get("category")
    if category:
        filtered = [l for l in LIGHTS_DB if l["category"] == category]
        return jsonify(filtered)
    return jsonify(LIGHTS_DB)
