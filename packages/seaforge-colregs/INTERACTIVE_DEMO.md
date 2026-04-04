# 🌊 Interactive COLREGS Demo — Web UI Testing Tool

Test your seamanship skills with a modern web interface. Answer real COLREGS scenarios and get instant feedback from the library.

## Quick Start

### 1. Install Demo Dependencies

```bash
source venv/bin/activate
pip install -e '.[demo]'
```

### 2. Run the Demo App

```bash
python demo_app.py
```

You should see:

```
================================================================================
🌊 SEAFORGE COLREGS INTERACTIVE DEMO
================================================================================

🚀 Starting Flask app on http://localhost:5000

Open your browser and navigate to:
   http://localhost:5000

Demos available:
   • Interactive COLREGS Trainer (5-question quiz)
   • Bridge Simulator (3-vessel encounters)
   • Rule Sandbox (manual encounter classification)
================================================================================
```

### 3. Open Your Browser

Navigate to: **http://localhost:5000**

---

## Features

### 📚 COLREGS Trainer
- **5 random scenarios** from 95-scenario database
- Real-time feedback on your answers
- COLREGS rule references
- Score tracking and accuracy calculation

**How it works:**
1. Click "Start Trainer"
2. Read the maritime scenario
3. Type your answer in the text box
4. Click "Submit Answer"
5. See if you're correct + rule explanation
6. Progress to next question

### 🌊 Bridge Simulator
- **3 simultaneous vessel encounters**
- Realistic multi-vessel decision scenarios
- Determine your role: give-way or stand-on
- Professional scoring and feedback

### 🧭 Rule Sandbox
- **Manual course/bearing inputs**
- Instant classification using the real library API
- Clear output for situation, role, rule, and action
- Useful for UI testing and edge-case verification

**How it works:**
1. Click "Start Simulator"
2. Read each encounter details (bearing, distance, vessel type)
3. Select your role: "Give-way Vessel" or "Stand-on Vessel"
4. Click "Submit Decision"
5. Get feedback on your COLREGS knowledge
6. See final score and encounter log

---

## What You're Testing

### Core Library Functions

All demos use real seaforge-colregs library functions:

```python
# Encounter classification
situation, role, rule, action = classify_encounter(own_cog, target_cog, rel_bearing)

# Collision risk calculation
cpa, tcpa = compute_cpa_tcpa(own_lat, own_lon, own_cog, own_sog,
                              tgt_lat, tgt_lon, tgt_cog, tgt_sog)

# Navigation calculations
bearing = bearing_to(lat1, lon1, lat2, lon2)
distance = range_nm(lat1, lon1, lat2, lon2)
rel_brg = relative_bearing(own_hdg, target_bearing)
```

### Example Scenarios

**Trainer Scenario:**
- Category: Lights (Rule 23)
- Difficulty: ⭐⭐
- Q: "You see a red light above a white light. What type of vessel?"
- A: "Power-driven vessel"

**Bridge Simulator Encounter:**
- Vessel: Container Ship A
- Distance: 6.3nm
- Bearing: 90°
- Decision: Give-way or Stand-on?

---

## API Endpoints (For Developers)

### Start Trainer

```bash
POST /api/trainer/start
{
  "num_questions": 5
}
```

Response:
```json
{
  "session_id": 1234,
  "demo": "trainer",
  "total_questions": 5,
  "current_question": 1,
  "scenario": {
    "category": "LIGHTS",
    "difficulty": "⭐⭐",
    "question": "You see TWO masthead lights...",
    "rule": "Rule 23(a)"
  }
}
```

### Submit Answer

```bash
POST /api/trainer/answer
{
  "session_id": 1234,
  "answer": "Power-driven vessel"
}
```

### Start Bridge Simulator

```bash
POST /api/bridge/start
{}
```

### Submit Bridge Decision

```bash
POST /api/bridge/answer
{
  "session_id": 1234,
  "role": "give-way"
}
```

---

## Keyboard Shortcuts (Coming in Phase 1+)

- `?` — Help
- `n` — Next question (when feedback shown)
- `r` — Restart
- `⌘+K` — Search scenarios

---

## Troubleshooting

### Port 5000 Already in Use?

```bash
python demo_app.py --port 5001
```

Then visit: http://localhost:5001

### Demo Dependencies Missing?

```bash
source venv/bin/activate
pip install -e '.[demo]'
python demo_app.py
```

### Browser Shows "Connection Refused"?

Make sure the Flask app is running:
```bash
python demo_app.py
```

And check that you're visiting: **http://localhost:5000** (not https)

---

## Design Inspiration

- **Signal K dashboards** — Professional maritime UI aesthetics
- **OpenBridge components** — Gauge styling and dark theme
- **Maritime academies** — Scenario progression and difficulty levels

---

## What's Next (Phase 1 Roadmap)

- [ ] SVG encounter diagram visualization
- [ ] Real-time vessel position tracking (animated)
- [ ] Spaced repetition algorithm (adapt difficulty)
- [ ] Database logging (save your scores)
- [ ] Mobile responsive optimization
- [ ] Real-time coaching (explain rules DURING scenarios, not after)
- [ ] Scenario export (for classroom use)
- [ ] Leaderboard (compare with other users)

---

## File Structure

```
demo_app.py                          ← Flask backend
templates/
  demo_dashboard.html                ← Web UI (HTML + CSS + JS)
INTERACTIVE_DEMO.md                  ← This file
```

---

## Testing Your Seamanship

### Beginner Path (Start Easy)
1. Trainer: Start with questions on Lights (Rule 23)
2. Trainer: Progress to Encounters
3. Bridge Sim: Test with 3-vessel scenario

### Intermediate Path
1. Trainer: Do 5 random questions
2. Check which categories you struggle with
3. Bridge Sim: Make correct decisions on all encounters

### Advanced Path
1. Trainer: Aim for 100% accuracy
2. Bridge Sim: Perfect score on 3-vessel encounters
3. Challenge yourself with hard scenarios (⭐⭐⭐)

---

## Feedback & Scoring

### Trainer Feedback
- **Correct:** Shows green checkmark + rule explanation
- **Incorrect:** Shows red X + correct answer + rule reference

### Bridge Simulator Feedback
- **Correct Decision:** Green background, shows action taken
- **Incorrect Decision:** Red background, shows correct role + action
- **Final Score:** X/3 correct decisions with detailed encounter log

---

## Integration with SeaForge Platform

This demo app is a prototype for **Phase 1 Integration**:

- Dashboard will embed in Mission Control React app
- Scores logged to compliance vault
- Real AIS data can feed scenarios automatically
- COLREGS trainer becomes part of crew training workflow

---

## Questions?

See `DEMO_GUIDE.md` for full documentation of all 5 demos.
See `DEMO_SUITE_STATUS.md` for validation and technical details.

---

**Status:** ✅ Ready to use | Test your seamanship now!

Generated: 2026-03-27 | SeaForge Maritime Platform
