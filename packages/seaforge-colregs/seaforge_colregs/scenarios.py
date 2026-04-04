"""COLREGS training scenarios loader for STCW Table A-II/1-aligned content.

This module provides access to 95 COLREGS training scenarios covering all 10
mandatory categories: lights, day_shapes, encounters,
sound_signals_maneuvering, sound_signals_fog, restricted_visibility, tss,
narrow_channels, general_rules, and responsibilities.

Scenarios are sourced from Popeye OOW/SAR workspace and aligned with:
- IMO STCW Table A-II/1 (Competence requirements for OOW)
- ICC COLREGS Consolidated 2026
- IAMSAR Vol. III (Search and Rescue operations)

The data is stored as JSON in seaforge_colregs/data/scenarios.json for
easy integration with web frontends, mobile apps, and training engines.
"""

import os
import json
import random as random_module
from typing import Any, Dict, List, Optional, cast


def _load_scenarios_data() -> List[Dict[str, Any]]:
    """Load scenarios from JSON file.

    Returns:
        List of scenario dictionaries.

    Raises:
        FileNotFoundError: If scenarios.json is not found.
        json.JSONDecodeError: If JSON is malformed.
    """
    scenarios_path = os.path.join(os.path.dirname(__file__), "data", "scenarios.json")

    with open(scenarios_path, "r", encoding="utf-8") as f:
        return cast(List[Dict[str, Any]], json.load(f))


# Module-level cache (lazy-loaded on first access)
_SCENARIOS_CACHE: Optional[List[Dict[str, Any]]] = None


def _get_scenarios() -> List[Dict[str, Any]]:
    """Get cached scenarios, loading once on first access."""
    global _SCENARIOS_CACHE
    if _SCENARIOS_CACHE is None:
        _SCENARIOS_CACHE = _load_scenarios_data()
    return _SCENARIOS_CACHE


def load_scenarios() -> List[Dict[str, Any]]:
    """Load and return all 95 COLREGS training scenarios.

    Returns:
        List of scenario dictionaries, each with keys:
        - scenario (str): The training question or situation description
        - answer (str): The correct answer or action required
        - rule (str): The COLREGS rule reference (e.g., "Rule 14")
        - category (str): Scenario category (see get_categories())
        - difficulty (int): 1-3 (beginner to advanced)

    Example:
        >>> scenarios = load_scenarios()
        >>> len(scenarios)
        95
        >>> scenarios[0]['rule']
        'Rule 23(a)'
    """
    return _get_scenarios()


def get_categories() -> List[str]:
    """Return list of all available scenario categories.

    Categories align with STCW Table A-II/1 and cover all aspects of the
    COLREGS regulations:

    - lights: Vessels' lights and shapes (Rules 20-31)
    - day_shapes: Daytime signals (Rules 20-31)
    - encounters: Collision avoidance and courses (Rules 11-18)
    - sound_signals_maneuvering: Whistle signals in sight (Rule 34)
    - sound_signals_fog: Fog and restricted visibility signals (Rule 35)
    - restricted_visibility: Operations in fog (Rule 19)
    - tss: Traffic Separation Schemes (Rule 10)
    - narrow_channels: Narrow channel navigation (Rule 9)
    - general_rules: Fundamental rules (Rules 2-8)
    - responsibilities: Vessel hierarchies and priorities (Rule 18)

    Returns:
        Sorted list of unique category names.

    Example:
        >>> cats = get_categories()
        >>> 'lights' in cats
        True
        >>> len(cats)
        10
    """
    scenarios = _get_scenarios()
    categories = set(s["category"] for s in scenarios)
    return sorted(list(categories))


def get_scenario(
    category: Optional[str] = None,
    difficulty: Optional[int] = None,
    random_choice: bool = False,
    *,
    random: Optional[bool] = None,
) -> Optional[Dict[str, Any]]:
    """Get a scenario, optionally filtered by category and/or difficulty.

    Filters are applied conjunctively (AND). Returns first matching scenario
    unless `random_choice=True`.

    Args:
        category: Filter by category name. If None, all categories included.
                 Must be one of get_categories() or KeyError is raised.
        difficulty: Filter by difficulty level (1, 2, or 3). If None, all
                   levels included.
        random_choice: If True, return a random matching scenario instead of
            the first.
        random: Backward-compatible alias for `random_choice`.

    Returns:
        A scenario dictionary matching the criteria, or None if no match found.

    Raises:
        ValueError: If category is invalid (not in get_categories()).
        ValueError: If difficulty is not 1, 2, or 3.

    Example:
        >>> s = get_scenario(category='lights', difficulty=1)
        >>> s['rule']
        'Rule 23(a)'

        >>> s = get_scenario(category='encounters', random_choice=True)
        >>> s['scenario']  # Random encounter scenario

        >>> first = get_scenario()
        >>> first['category']
    """
    if random is not None:
        random_choice = random

    # Validate inputs
    if category is not None:
        valid_categories = get_categories()
        if category not in valid_categories:
            raise ValueError(
                f"Invalid category '{category}'. " f"Must be one of: {', '.join(valid_categories)}"
            )

    if difficulty is not None:
        if difficulty not in (1, 2, 3):
            raise ValueError("Difficulty must be 1, 2, or 3")

    # Filter scenarios
    scenarios = _get_scenarios()
    matches = scenarios

    if category is not None:
        matches = [s for s in matches if s["category"] == category]

    if difficulty is not None:
        matches = [s for s in matches if s["difficulty"] == difficulty]

    # Return result
    if not matches:
        return None

    if random_choice:
        return random_module.choice(matches)

    return matches[0]


def get_scenarios_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all scenarios for a specific category.

    Args:
        category: Category name (must be in get_categories()).

    Returns:
        List of all scenarios in that category, sorted by difficulty (1, 2, 3).

    Raises:
        ValueError: If category is invalid.

    Example:
        >>> lights = get_scenarios_by_category('lights')
        >>> len(lights)
        20
        >>> lights[0]['difficulty']
        1
    """
    valid_categories = get_categories()
    if category not in valid_categories:
        raise ValueError(
            f"Invalid category '{category}'. " f"Must be one of: {', '.join(valid_categories)}"
        )

    scenarios = _get_scenarios()
    matches = [s for s in scenarios if s["category"] == category]
    return sorted(matches, key=lambda s: s["difficulty"])


def count_scenarios(category: Optional[str] = None, difficulty: Optional[int] = None) -> int:
    """Count scenarios matching optional filters.

    Args:
        category: Filter by category (optional).
        difficulty: Filter by difficulty level (optional).

    Returns:
        Number of matching scenarios.

    Example:
        >>> count_scenarios()
        95
        >>> count_scenarios(category='lights')
        20
        >>> count_scenarios(difficulty=1)
        37
    """
    if category is not None:
        valid_categories = get_categories()
        if category not in valid_categories:
            raise ValueError(
                f"Invalid category '{category}'. " f"Must be one of: {', '.join(valid_categories)}"
            )

    if difficulty is not None:
        if difficulty not in (1, 2, 3):
            raise ValueError("Difficulty must be 1, 2, or 3")

    scenarios = _get_scenarios()
    matches = scenarios

    if category is not None:
        matches = [s for s in matches if s["category"] == category]

    if difficulty is not None:
        matches = [s for s in matches if s["difficulty"] == difficulty]

    return len(matches)


def get_difficulty_breakdown(category: Optional[str] = None) -> Dict[int, int]:
    """Get count of scenarios by difficulty level.

    Args:
        category: If specified, return breakdown for that category only.

    Returns:
        Dictionary mapping difficulty (1, 2, 3) to count.

    Raises:
        ValueError: If category is invalid.

    Example:
        >>> breakdown = get_difficulty_breakdown()
        >>> breakdown[1]  # Easy scenarios
        35
        >>> breakdown = get_difficulty_breakdown(category='lights')
        >>> sum(breakdown.values())
        20
    """
    if category is not None:
        valid_categories = get_categories()
        if category not in valid_categories:
            raise ValueError(
                f"Invalid category '{category}'. " f"Must be one of: {', '.join(valid_categories)}"
            )

    result = {1: 0, 2: 0, 3: 0}

    scenarios = _get_scenarios()
    if category is not None:
        scenarios = [s for s in scenarios if s["category"] == category]

    for scenario in scenarios:
        result[scenario["difficulty"]] += 1

    return result
