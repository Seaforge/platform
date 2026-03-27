"""Navigation API — COLREGS, fleet, AIS, MOB endpoints."""

from flask import Blueprint, request, jsonify
try:
    from seaforge_colregs import classify_encounter, compute_cpa_tcpa, bearing_to, range_nm, relative_bearing, get_scenario, load_scenarios
except ImportError:
    from ..core.colregs import classify_encounter, compute_cpa_tcpa, bearing_to, range_nm, relative_bearing
    from ..data.lights_db import LIGHTS_DB

    def get_scenario(category=None, difficulty=None, random=False):
        """Fallback to local LIGHTS_DB if library not available."""
        result = LIGHTS_DB
        if category:
            result = [s for s in result if s["category"] == category]
        if difficulty:
            result = [s for s in result if s.get("difficulty") == difficulty]
        if random and result:
            import random as _random
            return _random.choice(result)
        return result

    def load_scenarios():
        """Fallback to local LIGHTS_DB if library not available."""
        return LIGHTS_DB

from ..core.ais import get_vessels, get_vessel_count
from ..core.mob import create_mob_event, calculate_datum, generate_search_pattern, get_gmdss_procedure
from ..data.fleet_db import FLEET_DB

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
    """Get COLREGS training scenarios.

    Query params: category, difficulty (1-3), random (true|false)
    """
    category = request.args.get("category")
    difficulty = request.args.get("difficulty", type=int)
    random_choice = request.args.get("random", "").lower() == "true"

    # Use library function (or fallback to local)
    if random_choice:
        result = get_scenario(category=category, difficulty=difficulty, random=True)
        result = [result] if result else []
    else:
        result = get_scenario(category=category, difficulty=difficulty, random=False)
        if not isinstance(result, list):
            result = [result] if result else []

    return jsonify(result)


# ── AIS endpoints ──

@bp.route("/ais/vessels", methods=["GET"])
def ais_vessels():
    """Get all tracked AIS vessels, optionally filtered by bounding box.

    Query params: n, s, e, w (lat/lon bounds)
    """
    n = request.args.get("n", type=float)
    s = request.args.get("s", type=float)
    e = request.args.get("e", type=float)
    w = request.args.get("w", type=float)

    bounds = None
    if all(v is not None for v in [n, s, e, w]):
        bounds = {"n": n, "s": s, "e": e, "w": w}

    vessels = get_vessels(bounds)
    # Strip internal _ts field
    result = []
    for mmsi, v in vessels.items():
        vessel = {k: val for k, val in v.items() if not k.startswith("_")}
        result.append(vessel)

    return jsonify({"vessels": result, "count": len(result)})


@bp.route("/ais/status", methods=["GET"])
def ais_status():
    """Get AIS stream status."""
    from ..core.ais import _running
    from ..core.nmea import get_source_status
    return jsonify({
        "streaming": _running,
        "vessel_count": get_vessel_count(),
        "sources": get_source_status()
    })


@bp.route("/ais/sources", methods=["POST"])
def add_ais_source():
    """Add a new AIS data source (TCP, UDP, Signal K).

    Body: {type: "tcp"|"udp"|"signalk", name: str, host: str, port: int}
    """
    from ..core.nmea import start_tcp_source, start_udp_source, start_signalk_source
    data = request.json
    src_type = data.get("type")
    name = data.get("name", src_type)
    host = data.get("host", "localhost")
    port = data.get("port", 10110)

    if src_type == "tcp":
        start_tcp_source(name, host, port)
    elif src_type == "udp":
        start_udp_source(name, port, host)
    elif src_type == "signalk":
        start_signalk_source(name, host, port)
    else:
        return jsonify({"error": "Unknown source type. Use tcp, udp, or signalk."}), 400

    return jsonify({"status": "started", "name": name, "type": src_type})


# ── MOB (Man Overboard) ──

# In-memory MOB event (only one active at a time)
_active_mob = None


@bp.route("/mob/trigger", methods=["POST"])
def mob_trigger():
    """Trigger MOB alarm. Records position and starts tracking.

    Body: {lat, lon, cog, sog, wind_dir?, wind_speed?}
    """
    global _active_mob
    data = request.json
    _active_mob = create_mob_event(
        lat=data["lat"], lon=data["lon"],
        cog=data.get("cog", 0), sog=data.get("sog", 0),
        wind_dir=data.get("wind_dir"), wind_speed=data.get("wind_speed")
    )
    return jsonify(_active_mob)


@bp.route("/mob/status", methods=["GET"])
def mob_status():
    """Get current MOB event status with updated datum."""
    if not _active_mob:
        return jsonify({"active": False})

    import time
    elapsed = (time.time() - _active_mob["unix_ts"]) / 60.0
    datum = calculate_datum(_active_mob, elapsed)
    _active_mob["datum"] = datum

    return jsonify({
        "active": True,
        "event": _active_mob,
        "elapsed_minutes": round(elapsed, 1),
        "datum": datum
    })


@bp.route("/mob/search-pattern", methods=["POST"])
def mob_search_pattern():
    """Generate search pattern around current datum.

    Body: {pattern: "expanding_square"|"sector"|"parallel", radius_nm?, spacing_nm?}
    """
    if not _active_mob:
        return jsonify({"error": "No active MOB event"}), 400

    data = request.json
    import time
    elapsed = (time.time() - _active_mob["unix_ts"]) / 60.0
    datum = calculate_datum(_active_mob, elapsed)

    waypoints = generate_search_pattern(
        datum=datum,
        pattern_type=data.get("pattern", "expanding_square"),
        search_radius_nm=data.get("radius_nm", 1.0),
        track_spacing_nm=data.get("spacing_nm", 0.1)
    )

    return jsonify({"datum": datum, "pattern": data.get("pattern", "expanding_square"), "waypoints": waypoints})


@bp.route("/mob/cancel", methods=["POST"])
def mob_cancel():
    """Cancel active MOB event."""
    global _active_mob
    _active_mob = None
    return jsonify({"status": "cancelled"})


@bp.route("/mob/procedure", methods=["GET"])
def mob_procedure():
    """Get full GMDSS MOB procedure checklist."""
    return jsonify(get_gmdss_procedure())
