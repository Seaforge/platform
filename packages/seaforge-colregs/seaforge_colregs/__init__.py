"""SeaForge COLREGS — Free, open-source COLREGS classification engine.

No external dependencies. Pure Python.

Usage:
    from seaforge_colregs import classify_encounter, get_scenario

    # Classify an encounter per COLREGS Rules 13-15
    situation, role, rule, action = classify_encounter(
        own_cog=0, target_cog=180, rel_bearing=45
    )

    # Get a random COLREGS training scenario
    scenario = get_scenario(random=True)
"""

__version__ = "0.1.0a1"
__author__ = "SeaForge Contributors"
__license__ = "MIT"

from .engine import (
    bearing_to,
    classify_encounter,
    compute_cpa_tcpa,
    range_nm,
    relative_bearing,
)
from .scenarios import get_scenario, get_categories, load_scenarios

__all__ = [
    "classify_encounter",
    "compute_cpa_tcpa",
    "bearing_to",
    "range_nm",
    "relative_bearing",
    "get_scenario",
    "get_categories",
    "load_scenarios",
]
