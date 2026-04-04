# seaforge-colregs

**The only free, open-source COLREGS classification engine.**

COLREGS (Collision Avoidance Rules) knowledge is required for every STCW
(Standards of Training, Certification and Watchkeeping) certificate globally.
Until now, no open-source reference implementation existed.
`seaforge-colregs` fills that gap: pure geometry, zero external dependencies,
and 95 training scenarios.

## Quick Start

```python
from seaforge_colregs import classify_encounter, get_scenario

# Classify an encounter
situation, role, rule, action = classify_encounter(
    own_cog=0, target_cog=180, rel_bearing=45
)
print(f"{situation} - {rule}: {action}")
# Output: crossing - Rule 15: Target on STARBOARD...

# Get a random training scenario
scenario = get_scenario(random=True)
print(scenario['scenario'])
```

## What This Does

**COLREGS Classification Engine**
- Implements Rules 13–15 (overtaking, head-on, crossing encounters)
- Classifies vessel relationship: who gives way, who stands on
- Returns navigational action for each scenario

**Collision Risk Assessment**
- Computes CPA (Closest Point of Approach) in nautical miles
- Calculates TCPA (Time to CPA) in minutes
- Predicts future collision point with geometry

**Great Circle Navigation**
- True bearing between two positions (handles antimeridian)
- Haversine distance calculation in nautical miles

**Training Scenarios**
- 95 vetted scenarios across 10 STCW categories
- Covers lights, shapes, sound signals, special vessels
- Calibrated difficulty levels for cadet progression

**Zero Dependencies**
- Pure Python 3.8+, no external packages
- Single file, ~200 lines of implementation
- 4 KB of embedded scenario data

## Installation

```bash
pip install seaforge-colregs
```

Requires Python 3.8 or later.

## API Reference

### `classify_encounter(own_cog, target_cog, rel_bearing)`

Classify a two-vessel encounter per COLREGS Rules 13–15.

**Parameters:**
- `own_cog` (float): Your vessel's course over ground (0–360°)
- `target_cog` (float): Target vessel's course over ground (0–360°)
- `rel_bearing` (float): Target's relative bearing from your bow (0–360°)

**Returns:** tuple of four strings
- `situation` – encounter type: `"head-on"`, `"crossing"`, or `"overtaking"`
- `role` – your vessel's duty: `"give-way"` or `"stand-on"`
- `rule` – applicable COLREGS rule: `"Rule 13"`, `"Rule 14"`, or `"Rule 15"`/`"Rule 17"`
- `action` – plain-English navigational instruction

**Example:**
```python
situation, role, rule, action = classify_encounter(0, 180, 45)
assert situation == "crossing"
assert role == "give-way"
assert rule == "Rule 15"
```

### `compute_cpa_tcpa(own_lat, own_lon, own_cog, own_sog, tgt_lat, tgt_lon, tgt_cog, tgt_sog)`

Compute Closest Point of Approach and time to CPA.

**Parameters:**
- `own_lat`, `own_lon` (float): Your vessel's latitude and longitude (decimal degrees, WGS84)
- `own_cog`, `own_sog` (float): Your course over ground (°), speed over ground (knots)
- `tgt_lat`, `tgt_lon` (float): Target's latitude and longitude
- `tgt_cog`, `tgt_sog` (float): Target's course (°), speed (knots)

**Returns:** tuple
- `cpa_nm` (float): Closest point of approach distance in nautical miles
- `tcpa_min` (float): Time to CPA in minutes (or 0 if target is already astern)
- `cpa_lat`, `cpa_lon` (float): Latitude and longitude at CPA

**Example:**
```python
cpa, tcpa, lat, lon = compute_cpa_tcpa(
    51.4769, 1.3912, 90, 12,      # Own: North Sea, heading E at 12 kts
    51.4600, 1.4200, 270, 10       # Target: NE of us, heading W at 10 kts
)
print(f"CPA: {cpa} nm in {tcpa} minutes")
```

### `bearing_to(own_lat, own_lon, tgt_lat, tgt_lon)`

Calculate true bearing from own vessel to target.

**Parameters:**
- `own_lat`, `own_lon` (float): Own position (decimal degrees, WGS84)
- `tgt_lat`, `tgt_lon` (float): Target position

**Returns:** float
- True bearing (0–360°) using great circle navigation

**Example:**
```python
bearing = bearing_to(37.7749, -122.4194, 51.4769, 1.3912)  # SF to Dover
print(f"True bearing: {bearing}°")
```

### `range_nm(lat1, lon1, lat2, lon2)`

Calculate great circle distance in nautical miles.

**Parameters:**
- `lat1`, `lon1` (float): First position (decimal degrees, WGS84)
- `lat2`, `lon2` (float): Second position

**Returns:** float
- Distance in nautical miles

**Example:**
```python
distance = range_nm(51.4769, 1.3912, 51.5074, 0.1278)  # Dover to Greenwich
print(f"Distance: {distance:.1f} nm")  # ~20.5 nm
```

### `get_scenario(category=None, difficulty=None, random_choice=False, random=None)`

Retrieve a training scenario.

**Parameters:**
- `category` (str, optional): One of the packaged categories such as `"lights"`, `"encounters"`, or `"tss"`
- `difficulty` (int, optional): `1`, `2`, or `3`
- `random_choice` (bool): If True, return a random scenario matching filters
- `random` (bool, optional): Backward-compatible alias for `random_choice`

**Returns:** dict
- `scenario` (str) – descriptive text of encounter
- `answer` (str) – expected answer text
- `rule` (str) – COLREGS rule reference
- `category` (str) – training category
- `difficulty` (int) – difficulty level from 1 to 3

**Example:**
```python
scenario = get_scenario(category="lights", difficulty=1, random=True)
print(scenario['scenario'])
print(scenario['answer'])
print(scenario['rule'])  # e.g., "Rule 23(a)"
```

### `load_scenarios()`

Load all 95 scenarios into memory.

**Returns:** list of dict
- Each dict has keys: `scenario`, `answer`, `rule`, `category`, `difficulty`

**Example:**
```python
all_scenarios = load_scenarios()
print(f"Total: {len(all_scenarios)} scenarios")
for sc in all_scenarios:
    print(f"  {sc['category']} ({sc['difficulty']}): {sc['scenario'][:50]}...")
```

## Use Cases

**Maritime Training & Certification**
- STCW exam preparation apps for deck cadets
- Scenario-based learning for COLREGS competency
- Integrated with ship bridge simulators

**Collision Avoidance Systems**
- Autonomous vessel decision support
- Real-time CPA/TCPA monitoring
- Rule-based action recommendations

**Maritime Simulation & Gaming**
- Training game engines (non-commercial and commercial)
- Sea-school curriculum support
- Officer of the Watch competency validation

**Recreational & Commercial Boating**
- Navigation training for RYA/ICC certifications
- Mobile apps for skippers and helmsmen
- Incident debriefing and analysis tools

**Research & Analysis**
- Near-miss or collision investigation
- Vessel traffic service (VTS) decision support
- Maritime law and Rules of the Road precedent analysis

## Contributing

Found a scenario bug, ambiguity, or unrealistic outcome? [Open an issue](https://github.com/seaforge-maritime/seaforge-colregs/issues).

Want to add scenarios for ICC regulations, regional rules, or special cases? [Submit a PR](https://github.com/seaforge-maritime/seaforge-colregs/pulls). All scenarios are reviewed for accuracy against COLREGS, ICS model, and maritime precedent.

**Scenario format:**
```python
{
    "scenario": "You see TWO masthead lights (vertical), sidelights, and a sternlight.",
    "answer": "Power-driven vessel underway, length 50m or more (Rule 23a).",
    "rule": "Rule 23(a)",
    "category": "lights",
    "difficulty": 1,
}
```

## License

MIT License — free for commercial and non-commercial use. See `LICENSE` file for details.

---

**Built with ⚓ for the maritime community.** Maintained by [SeaForge](https://github.com/seaforge-maritime).
