---
name: add-fleet
description: "Add a new carrier fleet to SeaForge's fleet database"
---

# Add Fleet

## Instructions

1. Read `src/data/fleet_db.py` to understand the existing format
2. Ask user for: company name, list of vessel names
3. For each vessel, research and verify:
   - IMO number (7 digits)
   - MMSI number (9 digits)
   - Vessel type
   - Flag state
   - DWT (if available)
   - Source: MarineTraffic, VesselFinder, or Equasis
4. Add the fleet to `FLEET_DB` dict in `src/data/fleet_db.py`
5. Add a fleet color to `fleetColors` in `static/js/app.js`
6. Add a toggle button in `templates/index.html` fleet panel
7. Run `/deploy` to rebuild and verify
