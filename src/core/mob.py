"""Man Overboard (MOB) module — position recording, drift calculation, search patterns, GMDSS procedure.

When MOB is triggered:
1. Record exact position + time
2. Calculate drift (current + leeway)
3. Generate search patterns
4. Guide GMDSS alerting procedure step by step
"""

import math
import time
from datetime import datetime, timezone


def create_mob_event(lat, lon, cog, sog, wind_dir=None, wind_speed=None):
    """Create a MOB event with all initial data.

    Args:
        lat, lon: Position at time of MOB alarm
        cog, sog: Ship's course/speed at time of alarm
        wind_dir: Wind direction (degrees true) — for leeway calc
        wind_speed: Wind speed (knots) — for leeway calc

    Returns:
        MOB event dict with datum point, initial position, timestamps
    """
    now = datetime.now(timezone.utc)

    return {
        "id": int(time.time()),
        "timestamp": now.isoformat(),
        "unix_ts": time.time(),
        "position": {"lat": lat, "lon": lon},
        "ship_cog": cog,
        "ship_sog": sog,
        "wind_dir": wind_dir,
        "wind_speed": wind_speed,
        "datum": {"lat": lat, "lon": lon},  # Updated with drift
        "status": "active",
        "search_pattern": None,
    }


def calculate_datum(mob_event, elapsed_minutes, current_dir=None, current_speed=None):
    """Calculate datum point (most probable position of person in water).

    Drift factors:
    - Sea current: direct drift
    - Leeway (wind effect on person): ~3% of wind speed, downwind
    - Person in water drifts ~0.7-1.0 kts in 20kt wind

    Args:
        mob_event: The MOB event dict
        elapsed_minutes: Time since MOB in minutes
        current_dir: Current direction (degrees, direction flowing TO)
        current_speed: Current speed in knots

    Returns:
        Updated datum position {lat, lon} and drift distance in NM
    """
    orig = mob_event["position"]
    lat, lon = orig["lat"], orig["lon"]
    elapsed_hours = elapsed_minutes / 60.0
    total_drift_nm = 0

    # Current drift
    if current_dir is not None and current_speed:
        drift_nm = current_speed * elapsed_hours
        lat, lon = _offset_position(lat, lon, current_dir, drift_nm)
        total_drift_nm += drift_nm

    # Leeway (wind effect on person in water)
    if mob_event.get("wind_dir") is not None and mob_event.get("wind_speed"):
        # Person drifts downwind at ~3-4% of wind speed
        leeway_speed = mob_event["wind_speed"] * 0.035  # knots
        leeway_nm = leeway_speed * elapsed_hours
        lat, lon = _offset_position(lat, lon, mob_event["wind_dir"], leeway_nm)
        total_drift_nm += leeway_nm

    return {"lat": lat, "lon": lon, "drift_nm": round(total_drift_nm, 2)}


def generate_search_pattern(datum, pattern_type, search_radius_nm=1.0, track_spacing_nm=0.1):
    """Generate search pattern waypoints around datum point.

    Args:
        datum: {lat, lon} center point
        pattern_type: 'expanding_square' | 'sector' | 'parallel'
        search_radius_nm: Radius of search area
        track_spacing_nm: Distance between tracks (visibility-dependent)

    Returns:
        List of waypoint dicts [{lat, lon, label}, ...]
    """
    lat, lon = datum["lat"], datum["lon"]

    if pattern_type == "expanding_square":
        return _expanding_square(lat, lon, track_spacing_nm, legs=12)
    elif pattern_type == "sector":
        return _sector_search(lat, lon, search_radius_nm)
    elif pattern_type == "parallel":
        return _parallel_track(lat, lon, search_radius_nm, track_spacing_nm)
    else:
        return _expanding_square(lat, lon, track_spacing_nm, legs=12)


def get_gmdss_procedure():
    """Return step-by-step GMDSS MOB alerting procedure.

    This is the standard procedure per STCW and GMDSS requirements.
    The UI should present these as a checklist the OOW works through.
    """
    return {
        "immediate_actions": [
            {"step": 1, "action": "Release lifebuoy with light & smoke", "detail": "Throw nearest lifebuoy toward casualty. Deploy MOB marker."},
            {"step": 2, "action": "Press MOB button on GPS/ECDIS", "detail": "Records exact position and time. If no GPS, note position from chart."},
            {"step": 3, "action": "Sound 3 long blasts on whistle", "detail": "Alert all crew. Announce on PA: 'MAN OVERBOARD [PORT/STARBOARD SIDE]'"},
            {"step": 4, "action": "Post lookout — point at casualty", "detail": "Assign dedicated lookout. Never lose visual contact."},
            {"step": 5, "action": "Inform Master", "detail": "Call bridge/master immediately if not already present."},
        ],
        "manoeuvre": [
            {"step": 6, "action": "Execute recovery manoeuvre", "detail": "Williamson Turn (delayed discovery), Anderson Turn (immediate, day), Scharnow Turn (immediate, restricted visibility)"},
            {"step": 7, "action": "Williamson Turn", "detail": "Hard rudder to side of casualty → when 60° off original course → hard rudder opposite → when heading 180° from original → midships. Best for delayed discovery."},
            {"step": 8, "action": "Anderson Turn", "detail": "Hard rudder to side of casualty → when 250° from original course → midships. Fastest, best in good visibility."},
            {"step": 9, "action": "Scharnow Turn", "detail": "Hard rudder to side of casualty → when 240° off → hard opposite → when on reciprocal course → midships. Best for large vessels."},
        ],
        "gmdss_alert": [
            {"step": 10, "action": "DSC Distress Alert (if warranted)", "detail": "VHF Ch70: Nature of distress = 'Man Overboard'. Include position, time, MMSI. Only if unable to recover independently."},
            {"step": 11, "action": "MAYDAY voice call on VHF Ch16", "detail": "MAYDAY MAYDAY MAYDAY — This is [vessel name x3] — MMSI [number] — My position is [lat/lon] — Man overboard at [time UTC] — [number] persons in water — I require immediate assistance — OVER"},
            {"step": 12, "action": "Activate EPIRB if warranted", "detail": "406 MHz EPIRB for extended search. Sends distress to COSPAS-SARSAT."},
            {"step": 13, "action": "Broadcast SECURITÉ on Ch16", "detail": "If not full distress but alerting nearby traffic to keep lookout."},
            {"step": 14, "action": "Contact nearest MRCC/Coast Guard", "detail": "Via VHF, MF/HF DSC, or Inmarsat. Provide: position, time, persons in water, weather, drift estimate."},
        ],
        "recovery": [
            {"step": 15, "action": "Approach from downwind/downcurrent", "detail": "Create lee for casualty. Approach at minimum speed."},
            {"step": 16, "action": "Deploy rescue equipment", "detail": "Scramble net, Jason's Cradle, rescue boat if conditions allow."},
            {"step": 17, "action": "Recover casualty", "detail": "Horizontal lift preferred (reduces cardiac stress). Prepare for hypothermia treatment."},
            {"step": 18, "action": "Provide first aid", "detail": "Treat for hypothermia, drowning, injuries. Medical advice via radio if needed."},
            {"step": 19, "action": "Cancel distress if issued", "detail": "If MAYDAY was sent: transmit MAYDAY RELAY — SILENCE FINI on Ch16."},
        ],
        "search_patterns": {
            "expanding_square": "Best when datum is reliable and search area small. Start at datum, expand outward in square spiral.",
            "sector": "Best for immediate MOB with good datum. Triangular pattern through datum point.",
            "parallel": "Best for large search area or poor datum. Parallel tracks across the area.",
        }
    }


# ── Internal helpers ──

def _offset_position(lat, lon, bearing_deg, distance_nm):
    """Offset a position by bearing and distance."""
    R = 3440.065  # Earth radius in NM
    brg = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(distance_nm / R) +
        math.cos(lat1) * math.sin(distance_nm / R) * math.cos(brg)
    )
    lon2 = lon1 + math.atan2(
        math.sin(brg) * math.sin(distance_nm / R) * math.cos(lat1),
        math.cos(distance_nm / R) - math.sin(lat1) * math.sin(lat2)
    )

    return math.degrees(lat2), math.degrees(lon2)


def _expanding_square(lat, lon, spacing_nm, legs=12):
    """Generate expanding square search pattern waypoints."""
    waypoints = [{"lat": lat, "lon": lon, "label": "DATUM"}]
    current_lat, current_lon = lat, lon
    leg_num = 1

    for i in range(legs):
        # Alternating: N, E, S, W with increasing distances
        bearings = [0, 90, 180, 270]
        bearing = bearings[i % 4]
        distance = spacing_nm * ((i // 2) + 1)

        current_lat, current_lon = _offset_position(
            current_lat, current_lon, bearing, distance
        )
        waypoints.append({
            "lat": round(current_lat, 6),
            "lon": round(current_lon, 6),
            "label": f"WP{leg_num}"
        })
        leg_num += 1

    return waypoints


def _sector_search(lat, lon, radius_nm):
    """Generate sector (triangle) search pattern."""
    waypoints = [{"lat": lat, "lon": lon, "label": "DATUM"}]

    # Three legs through datum at 120° apart
    for i, bearing in enumerate([0, 120, 240]):
        out_lat, out_lon = _offset_position(lat, lon, bearing, radius_nm)
        waypoints.append({"lat": round(out_lat, 6), "lon": round(out_lon, 6), "label": f"S{i+1}"})
        waypoints.append({"lat": round(lat, 6), "lon": round(lon, 6), "label": "DATUM"})

        # Offset tracks
        out_lat2, out_lon2 = _offset_position(lat, lon, bearing + 30, radius_nm)
        waypoints.append({"lat": round(out_lat2, 6), "lon": round(out_lon2, 6), "label": f"S{i+1}b"})
        waypoints.append({"lat": round(lat, 6), "lon": round(lon, 6), "label": "DATUM"})

    return waypoints


def _parallel_track(lat, lon, width_nm, spacing_nm):
    """Generate parallel track search pattern."""
    waypoints = []
    half = width_nm / 2
    num_tracks = int(width_nm / spacing_nm)

    for i in range(num_tracks):
        offset = -half + i * spacing_nm
        start_lat, start_lon = _offset_position(lat, lon, 90, offset)
        end_lat, end_lon = _offset_position(start_lat, start_lon, 0 if i % 2 == 0 else 180, width_nm)

        waypoints.append({"lat": round(start_lat, 6), "lon": round(start_lon, 6), "label": f"T{i+1}S"})
        waypoints.append({"lat": round(end_lat, 6), "lon": round(end_lon, 6), "label": f"T{i+1}E"})

    return waypoints
