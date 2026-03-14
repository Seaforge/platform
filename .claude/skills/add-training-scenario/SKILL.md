---
name: add-training-scenario
description: "Add COLREGS training scenarios (lights, shapes, sound signals, encounters)"
---

# Add Training Scenario

## Instructions

1. Read `src/data/lights_db.py` to understand existing scenario format
2. Read references/colregs-categories.md for the full list of training categories
3. Ask user which category to add scenarios for
4. Create scenarios following the format:
   ```python
   {
       "id": <next_id>,
       "category": "<category>",
       "scenario": "<description of what the cadet sees/hears>",
       "answer": "<correct identification and required action>",
       "rule": "Rule <number>",
       "difficulty": <1-3>
   }
   ```
5. Add to `LIGHTS_DB` list in `src/data/lights_db.py`
6. Verify the rule citation is correct per COLREGS
7. Run `/deploy` to rebuild

## References
- references/colregs-categories.md — all 10 training categories with examples
