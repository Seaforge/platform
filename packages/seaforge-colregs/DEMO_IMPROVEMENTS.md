# 🚀 Demo Improvements Roadmap

## Phase 1: Multiple-Choice Trainer (TODAY) ✅

**What:** Convert free-text trainer to multiple-choice format

**Why:**
- Fair grading (no phrasing ambiguity)
- Cleaner UX
- Better learning (see all possible answers)
- Faster development

**Implementation:**
1. Update scenario format to include 4 answer options
2. Modify HTML to show radio buttons
3. Update Flask API to return options
4. Simplify answer validation (just match selected option)

**Status:** Ready to build

---

## Phase 2: Advanced Visualizations & Pedagogy (BONUS) 📊

**What:** Compass diagrams, rule explanations, CPA/TCPA, edge case testing

**Components:**
1. **Compass Visualization** — Show relative vessel positions
2. **Rule Explanation Chain** — Why you're give-way/stand-on
3. **Collision Risk** — CPA/TCPA values + visual danger zones
4. **Boundary Testing** — Interactive adjustment of bearings
5. **Learning Progression** — Easy → Medium → Hard

**Status:** Designed, ready for implementation when desired

---

## Scoring Criteria (Phase 2)

When Phase 2 is rated:

| Metric | Points |
|--------|--------|
| Compass visualization (SVG) | 15 |
| Rule explanation chain | 15 |
| CPA/TCPA display | 10 |
| Interactive boundary testing | 10 |
| Mobile responsive | 10 |
| Performance (<200ms) | 10 |
| Code quality + docs | 15 |
| **Total** | **85** |

---

## Build Order

**NOW (Phase 1):**
```
1. Add options[] to scenario format ✅
2. Update demo_dashboard.html (radio buttons) ✅
3. Update demo_app.py (return options) ✅
4. Test trainer end-to-end ✅
5. Deploy to localhost:5001 ✅
```

**LATER (Phase 2 - Bonus):**
```
6. Add SVG compass to Bridge Sim
7. Add rule explanation cards
8. Add CPA/TCPA calculator display
9. Add interactive bearing adjuster
10. Mobile optimization
```

---

## Expected Result (Phase 1)

**Trainer Tab:**
```
Question 1/5 | LIGHTS | Difficulty: ⭐⭐

You see TWO masthead lights (vertical), sidelights, and a sternlight.
What type of vessel is this?

○ Sailing vessel
○ Fishing vessel
◉ Power-driven vessel
○ Vessel restricted in ability to manoeuvre

[Submit Answer]

✓ Correct! Power-driven vessel (Rule 23a)
Rule: Masthead lights in vertical line = power-driven vessel
```

---

Ready to build? 🔨
