"""COLREGS classification engine — pure geometry, no external dependencies.

Implements encounter classification per COLREGS Rules 13-15 and
CPA/TCPA computation for collision risk assessment.
"""

import math


def relative_bearing(own_hdg: float, target_bearing: float) -> float:
    """Relative bearing from own heading to target (0-360)."""
    return (target_bearing - own_hdg) % 360


def classify_encounter(own_cog: float, target_cog: float, rel_bearing: float) -> tuple:
    """Classify encounter per COLREGS Rules 13-15.

    Returns: (situation, own_role, rule, action)
    """
    course_diff = abs((own_cog - target_cog + 180) % 360 - 180)

    # Overtaking — Rule 13: target abaft the beam
    if 112.5 < rel_bearing < 247.5:
        return ("overtaking", "stand-on", "Rule 13",
                "Maintain course and speed. Target is overtaking you.")

    # Check if we are overtaking target
    target_rel = relative_bearing(target_cog, (rel_bearing + own_cog + 180) % 360)
    if 112.5 < target_rel < 247.5:
        return ("overtaking", "give-way", "Rule 13",
                "You are overtaking. Keep clear. Any alteration permitted.")

    # Head-on — Rule 14: courses roughly reciprocal, target ahead
    if course_diff > 170 and (rel_bearing < 6 or rel_bearing > 354):
        return ("head-on", "give-way", "Rule 14",
                "HEAD-ON. Both vessels alter course to STARBOARD.")

    # Crossing — Rules 15/17
    if rel_bearing < 112.5:
        return ("crossing", "give-way", "Rule 15",
                "Target on STARBOARD. You are GIVE-WAY. Alter course to STARBOARD "
                "or reduce speed. Avoid crossing ahead.")
    else:
        return ("crossing", "stand-on", "Rule 17",
                "Target on PORT. You are STAND-ON. Maintain course and speed. "
                "Be ready to act if give-way vessel doesn't.")


def compute_cpa_tcpa(own_lat: float, own_lon: float, own_cog: float, own_sog: float,
                     tgt_lat: float, tgt_lon: float, tgt_cog: float, tgt_sog: float) -> tuple:
    """Compute CPA and TCPA between two vessels.

    Returns: (cpa_nm, tcpa_min, cpa_lat, cpa_lon)
    """
    def to_xy(lat, lon, ref_lat, ref_lon):
        x = (lon - ref_lon) * 60 * math.cos(math.radians(ref_lat))
        y = (lat - ref_lat) * 60
        return x, y

    def cog_to_vxy(cog, sog):
        rad = math.radians(cog)
        return sog * math.sin(rad), sog * math.cos(rad)

    tx, ty = to_xy(tgt_lat, tgt_lon, own_lat, own_lon)
    ovx, ovy = cog_to_vxy(own_cog, own_sog)
    tvx, tvy = cog_to_vxy(tgt_cog, tgt_sog)

    rx, ry = tx, ty
    rvx, rvy = tvx - ovx, tvy - ovy

    rv_sq = rvx * rvx + rvy * rvy
    if rv_sq < 0.0001:
        cpa = math.sqrt(rx * rx + ry * ry)
        return cpa, 999, tgt_lat, tgt_lon

    tcpa_hrs = -(rx * rvx + ry * rvy) / rv_sq
    tcpa_min = tcpa_hrs * 60

    if tcpa_min < 0:
        cpa = math.sqrt(rx * rx + ry * ry)
        return cpa, 0, tgt_lat, tgt_lon

    cpa_rx = rx + rvx * tcpa_hrs
    cpa_ry = ry + rvy * tcpa_hrs
    cpa = math.sqrt(cpa_rx * cpa_rx + cpa_ry * cpa_ry)

    return round(cpa, 2), round(tcpa_min, 1), tgt_lat, tgt_lon


def bearing_to(own_lat: float, own_lon: float, tgt_lat: float, tgt_lon: float) -> float:
    """True bearing from own ship to target."""
    dlon = math.radians(tgt_lon - own_lon)
    lat1 = math.radians(own_lat)
    lat2 = math.radians(tgt_lat)
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    return round(math.degrees(math.atan2(x, y)) % 360, 1)


def range_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great circle distance in nautical miles."""
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(c * 3440.065, 2)
