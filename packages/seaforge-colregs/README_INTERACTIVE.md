# 🌊 Interactive COLREGS Demo — Test Your Seamanship

Want to test your maritime knowledge **interactively**? The web-based demo lets you answer real COLREGS scenarios and get instant feedback from the library.

## Live Demo

```bash
pip install seaforge-colregs flask
python -m seaforge_colregs.demo_app
```

Then open: **http://localhost:5000**

## What You Get

### 📚 COLREGS Trainer
- **5 random scenarios** from 95-scenario database
- Real-time scoring and feedback
- Rule explanations with each answer
- Track your accuracy

### 🌊 Bridge Simulator  
- **3 simultaneous vessel encounters** (realistic multi-vessel decision-making)
- Determine your role: give-way or stand-on
- COLREGS rule classification for each decision
- Professional maritime scenario environment

## Example

```
┌─────────────────────────────────────────────────────────────┐
│ 📚 COLREGS Trainer                                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ Question 1/5 | LIGHTS | Difficulty: ⭐⭐                   │
│                                                               │
│ You see TWO masthead lights (vertical), sidelights, and a  │
│ sternlight. What type of vessel is this?                   │
│                                                               │
│ Your Answer: _____________________________                  │
│                                                               │
│ [Submit Answer]                                            │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│ ✓ Correct! Power-driven vessel (Rule 23a)                 │
│ Rule: Masthead lights in a vertical line = power-driven    │
└─────────────────────────────────────────────────────────────┘
```

## Files Included

- `demo_app.py` — Flask backend
- `templates/demo_dashboard.html` — Professional web UI
- `INTERACTIVE_DEMO.md` — Full documentation

## Requirements

```bash
pip install flask seaforge-colregs
```

## Roadmap (Phase 1+)

- [ ] SVG encounter diagram visualization
- [ ] Real-time position animation
- [ ] Spaced repetition algorithm
- [ ] Score database logging
- [ ] Mobile optimization
- [ ] Real-time coaching (explain DURING scenarios)
- [ ] Classroom/institutional features

## Architecture

```
User Input
    ↓
Flask Backend (demo_app.py)
    ↓
seaforge-colregs Library
    ↓
COLREGS Classification + Scoring
    ↓
JSON Response
    ↓
Web UI (HTML/CSS/JS)
    ↓
Instant Feedback + Rule Explanations
```

**Zero external dependencies** — uses only Flask + seaforge-colregs (which itself uses only stdlib).

---

**Ready to test your seamanship?** Start the demo and challenge yourself! 🎯
