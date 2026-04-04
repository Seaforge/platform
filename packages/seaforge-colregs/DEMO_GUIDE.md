# SeaForge COLREGS Demo Suite v0.1.0a1

Five interactive demonstrations showing the versatility of the `seaforge-colregs` library for maritime training, simulation, and decision-making.

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run all demos
python run_all_demos.py

# Or run individual demos
python demo1.py   # Head-on encounter classification
python demo2.py   # Scenario database exploration
python demo3.py   # Interactive COLREGS trainer (quiz)
python demo4.py   # Kongsberg bridge simulator concept
python demo5.py   # OOW DP (dynamic positioning) training
```

---

## Demo Overview

| # | Name | Purpose | Time | Difficulty |
|---|------|---------|------|------------|
| **1** | Head-on Encounter | COLREGS engine demonstration | 2 min | ⭐ Easy |
| **2** | Scenario Database | Training scenario exploration | 2 min | ⭐ Easy |
| **3** | Interactive Trainer | 5-question COLREGS quiz | 3 min | ⭐ Easy |
| **4** | Bridge Simulator | 3-vessel multi-encounter scenario | 5 min | ⭐⭐ Medium |
| **5** | OOW DP Training | Station-keeping under environmental stress | 3 min | ⭐⭐ Medium |

---

## Demo 1: Head-on Encounter Classification

**What it demonstrates:**
- Core COLREGS rule classification (Rule 14)
- Bearing, range, and CPA/TCPA calculations
- Collision risk assessment

**Scenario:**
```
Own vessel:     MV SEAFORGE, heading 0° (North), 12 knots
Target vessel:  Bulk carrier, heading 180° (South), 10 knots
Situation:      Head-on, closing at 22 knots combined
```

**Output:**
- Bearing to target, range, relative bearing
- COLREGS classification: HEAD-ON situation
- Required action: "Stand-on" or "Give-way" determination
- Collision risk: CPA (Closest Point of Approach), TCPA (Time to CPA)
- Alert if CPA < 0.5nm

**COLREGS Reference:**
- Rule 14: Head-on situations — both vessels alter course to starboard
- Rule 8: Action to avoid collision — sufficient time and distance

---

## Demo 2: Scenario Database Exploration

**What it demonstrates:**
- Loading and filtering 95 COLREGS training scenarios
- Category-based scenario retrieval
- Difficulty-level organization

**Scenario Database:**
- 95 total scenarios across 10 categories
- Categories: lights, day shapes, encounters, sound signals (fog), TSS, narrow channels, etc.
- Difficulty levels: 1-3 (easy to hard)

**Output:**
```
Total Scenarios: 95
Categories: 10
  - Lights: 20
  - Day Shapes: 12
  - Encounters: 15
  - Sound Signals (Fog): 8
  - ... [etc]

[Random scenario example]
Q: "Two vessels approaching head-on at night. You see
    a red light above a white light to starboard. What
    type of vessel is this?"
A: "Power-driven vessel (Rule 25(a))"
```

**Training Application:**
- Spaced repetition on weak scenarios
- Category progression: lights → shapes → encounters → rules
- Real-time coaching during quiz mode

---

## Demo 3: Interactive COLREGS Trainer

**What it demonstrates:**
- Interactive quiz format with instant feedback
- Scenario-based learning
- Performance scoring

**Format:**
```
[5 random scenarios from scenario database]

Question 1/5: [Scenario card with lights/shapes/encounter description]
  A) [Option 1]
  B) [Option 2]
  C) [Option 3]
  D) [Option 4]

[User presses ENTER to reveal answer]
✓ Correct! Rule 25(c) — Sailing vessel.

[After 5 questions]
Score: 3/5 (60%)
```

**Features:**
- Randomized question order
- Optional difficulty filter (`random=true` parameter in library)
- Score tracking and feedback
- Rule reference for each answer

---

## Demo 4: Kongsberg Bridge Simulator Concept

**What it demonstrates:**
- Multi-vessel encounter scenario (realistic complexity)
- Simultaneous COLREGS decision-making
- Time-pressure decision scoring
- Professional maritime simulation

**Scenario:**
```
Location:       Bergen Harbor approach (constrained waterway)
Own vessel:     MV SEAFORGE (190m, 12 knots)
Encounter 1:    Container Ship A (head-on from East, 14 knots)
Encounter 2:    Fishing Vessel B (crossing from North, 8 knots)
Encounter 3:    Tanker C (overtaking from South, 15 knots)
```

**Decision Points:**
For each encounter, determine:
- Situation classification (head-on, crossing, overtaking)
- Your vessel's role (give-way or stand-on)
- Required action per COLREGS rule
- Effectiveness (did you avoid collision?)

**Scoring:**
```
Correct Decisions:  [N]/3
Accuracy:           [X]%
Violations:         [Rule breaches]
Collision Risks:    [High/Moderate/Low encounters]
```

**Training Value:**
- Combines COLREGS knowledge with situational awareness
- Realistic: multiple simultaneous encounters (bridge reality)
- Pressure test: decision quality under time constraints
- Performance feedback: compare role vs. rule requirements

**Real-World Application:**
- Maritime academy OOW (Officer of the Watch) training
- Bridge team decision-making drills
- Rule knowledge validation under scenario complexity

---

## Demo 5: OOW DP (Dynamic Positioning) Training

**What it demonstrates:**
- Station-keeping scenario (holding fixed position)
- Thruster management and fuel optimization
- Environmental disturbance handling (wind, current, waves)
- Real-time position feedback and control loops

**Scenario:**
```
Operation:      Offshore supply vessel approaching platform
Environment:    Wind 25 knots (180°), Current 1.5 knots (90°)
Vessel:         MV DP SENTINEL (Platform Supply Vessel)
Task:           Hold position within 5m of target (X=0, Y=0)
Starting error: 141.4 meters (must approach and station-keep)
```

**Vessel Systems:**
```
Thrusters:
  - Main engine (forward thrust, 0-100%)
  - Bow thruster (lateral thrust, 0-100%)
  - Port azimuth thruster (omnidirectional, angle + power)
  - Starboard azimuth thruster (omnidirectional, angle + power)

Resources:
  - Fuel tank: 100% capacity
  - Consumption rate: ~0.5% per minute at full power
```

**Control Phases:**
1. **Initial Approach (30s)** — Close distance rapidly
   - Main engine 80% → 60% → 40%
   - Monitor position error

2. **Fine Positioning (30s)** — Reduce approach velocity
   - Main engine 20% → 15% → 10%
   - Azimuth thrusters for lateral control
   - Target: <5m error

3. **Station-Keeping (30s)** — Hold position against forces
   - Low throttle (8-12%)
   - Continuous thruster micro-adjustments
   - Minimize fuel consumption

**Performance Metrics:**
```
Station-Keeping Metrics:
  Final Error:          [Distance in meters]
  Average Error:        [Mean position deviation]
  Time On-Station:      [% of time within 5m acceptance]

Resource Management:
  Fuel Consumed:        [Total % used]
  Fuel Remaining:       [% left]
  Efficiency Rating:    [Good/Moderate/Poor]

Assessment:
  Excellent:   On-station >80% + fuel >60%
  Good:        On-station >60% + fuel >30%
  Fair:        On-station >40%
  Poor:        On-station <40% (retraining needed)
```

**Training Value:**
- Teaches thruster vectoring and fuel optimization
- Realistic environmental disturbance modeling
- Situational awareness: real-time feedback loops
- Stress management: maintaining precision under dynamic conditions

**Real-World Application:**
- Offshore supply vessel crew training (PSV operations)
- Platform supply operations (critical for safety)
- Emergency DP procedures (loss of system, thruster failure)
- Fuel optimization for commercial efficiency

---

## Demo Output Format

All demos return structured JSON output suitable for:
- Web UI rendering
- Performance analysis
- Training record logging
- Integration with larger simulation platforms

**Example (Demo 4 - Bridge Simulator):**
```json
{
  "status": "pass",
  "demo": "bridge_simulator",
  "summary": {
    "scenario": "Bergen Harbor Multi-Vessel Approach",
    "encounters": 3,
    "correct_decisions": 1,
    "accuracy": "33%",
    "violations": ["Rule 14 breach: head-on"]
  },
  "decisions": [
    {
      "target": "CONTAINER SHIP A",
      "situation": "head-on",
      "correct_role": "give-way",
      "player_decision": "stand-on",
      "correct": false,
      "rule": "Rule 14",
      "collision_risk": "CRITICAL"
    }
  ]
}
```

---

## Progression Path (Recommended)

**For absolute beginners:**
1. Demo 1 → Demo 2 → Demo 3
   - Learn engine → explore scenarios → apply knowledge

**For maritime students:**
1. Demo 1 → Demo 3 (repeated) → Demo 4
   - Master individual rules → multiple scenarios → pressure test

**For experienced mariners (bridge team):**
1. Demo 4 → Demo 5
   - Bridge simulator (COLREGS under pressure) → DP training (specialized ops)

---

## Technical Details

**Dependencies:**
- `seaforge-colregs` (zero external dependencies)
- Python 3.8+

**Library Functions Used:**
- `classify_encounter(own_cog, target_cog, rel_bearing)`
- `compute_cpa_tcpa(own_lat, own_lon, own_cog, own_sog, tgt_lat, tgt_lon, tgt_cog, tgt_sog)`
- `bearing_to(lat1, lon1, lat2, lon2)`
- `range_nm(lat1, lon1, lat2, lon2)`
- `relative_bearing(own_hdg, target_bearing)`
- `get_scenario(category, difficulty, random)`
- `load_scenarios()`

**Demo Code Structure:**

```
demo1.py    — Simple function call, direct output
demo2.py    — Data loading, filtering, random selection
demo3.py    — Interactive loop, user input, scoring
demo4.py    — Multi-object simulation, decision evaluation
demo5.py    — Physical simulation (forces, control loops)
```

---

## Future Extensions (MVP 1–2)

**Web UI Dashboard:**
- HTML/CSS/JS interface for running demos
- SVG visualization of encounter diagrams
- Real-time DP position tracking (animated)
- Professional bridge-simulator aesthetics

**Advanced Scenarios:**
- Restricted visibility (fog, night)
- Traffic separation schemes (TSS)
- Narrow channels and shallow water
- Emergency maneuvers (engine failure, steering loss)

**Integration with Mission Control:**
- COLREGS trainer embedded in React dashboard
- Live AIS feed → automatic scenario generation
- Kaizen loop: adaptive difficulty based on weak rules
- Compliance vault: signed training records

---

## Testing Checklist

- [ ] All 5 demos execute without errors
- [ ] JSON output is valid and parseable
- [ ] No external API calls (fully offline)
- [ ] Computation is deterministic (same inputs = same outputs)
- [ ] Performance: each demo completes in <10 seconds
- [ ] Reasonable scenario difficulty progression
- [ ] Scoring accurately reflects COLREGS rules
- [ ] Environmental simulation is physically plausible

---

## Author Notes

These demos showcase the versatility of the `seaforge-colregs` library beyond a simple training app. The library is:
- **Modular**: Can be embedded in any maritime software (bridge simulators, LMS, autonomous systems)
- **Headless**: No UI dependency — output is pure data
- **Deterministic**: No randomness in core calculations (reproducible for verification)
- **Educational**: Full rule references and explanations included

The progression from simple (Demo 1) to complex (Demo 5) demonstrates the library's readiness for both academic and professional maritime training environments.

For questions or contributions: https://github.com/seaforge-maritime/seaforge-colregs

---

**Version:** 0.1.0a1 (Alpha)
**Last Updated:** 2026-03-27
**Status:** Ready for MVP 1 (web UI + advanced scenarios)
