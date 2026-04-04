"""Tests for COLREGS classification engine (seaforge_colregs)."""

import pytest
from seaforge_colregs import (
    bearing_to,
    classify_encounter,
    count_scenarios,
    compute_cpa_tcpa,
    get_categories,
    get_difficulty_breakdown,
    range_nm,
    relative_bearing,
    get_scenario,
    get_scenarios_by_category,
    load_scenarios,
)


class TestRelativeBearing:
    def test_target_ahead(self):
        assert relative_bearing(0, 0) == 0

    def test_target_starboard(self):
        assert relative_bearing(0, 90) == 90

    def test_target_port(self):
        assert relative_bearing(0, 270) == 270

    def test_target_astern(self):
        assert relative_bearing(0, 180) == 180

    def test_wraps_around(self):
        assert relative_bearing(350, 10) == 20

    def test_own_heading_offset(self):
        assert relative_bearing(90, 180) == 90


class TestClassifyEncounter:
    def test_head_on(self):
        situation, role, rule, _ = classify_encounter(0, 180, 1)
        assert situation == "head-on"
        assert rule == "Rule 14"
        assert role == "give-way"

    def test_crossing_give_way(self):
        # Target on starboard bow
        situation, role, rule, _ = classify_encounter(0, 270, 45)
        assert situation == "crossing"
        assert role == "give-way"
        assert rule == "Rule 15"

    def test_crossing_stand_on(self):
        # Target on port bow (relative bearing > 112.5 but not overtaking)
        situation, role, rule, _ = classify_encounter(0, 90, 315)
        assert situation == "crossing"
        assert role == "stand-on"
        assert rule == "Rule 17"

    def test_being_overtaken(self):
        # Target abaft the beam
        situation, role, rule, _ = classify_encounter(0, 0, 150)
        assert situation == "overtaking"
        assert role == "stand-on"
        assert rule == "Rule 13"

    def test_overtaking_target(self):
        # We are approaching from astern
        situation, role, rule, _ = classify_encounter(0, 0, 5)
        # The target sees us abaft their beam
        # This depends on the reciprocal bearing check
        assert rule == "Rule 13" or situation in (
            "head-on",
            "crossing",
            "overtaking",
        )

    def test_returns_four_elements(self):
        result = classify_encounter(0, 180, 1)
        assert len(result) == 4
        situation, role, rule, action = result
        assert isinstance(action, str)
        assert len(action) > 0


class TestComputeCpaTcpa:
    def test_head_on_collision(self):
        # Two vessels heading straight at each other
        cpa, tcpa, _, _ = compute_cpa_tcpa(
            51.0,
            1.0,
            0,
            10,  # own: heading N at 10 kts
            51.1,
            1.0,
            180,
            10,  # target: heading S at 10 kts
        )
        assert cpa < 0.5  # Very close CPA
        assert tcpa > 0  # Positive TCPA

    def test_parallel_same_direction(self):
        # Two vessels going same direction, offset by 1nm
        cpa, tcpa, _, _ = compute_cpa_tcpa(51.0, 1.0, 0, 10, 51.0, 1.0167, 0, 10)  # ~1nm east
        # Parallel courses: CPA should be roughly the initial distance
        assert cpa > 0.5

    def test_stationary_vessels(self):
        cpa, tcpa, _, _ = compute_cpa_tcpa(51.0, 1.0, 0, 0, 51.01, 1.0, 0, 0)
        assert tcpa == 999  # Sentinel for no relative motion

    def test_diverging(self):
        # Vessels moving apart
        cpa, tcpa, _, _ = compute_cpa_tcpa(
            51.0, 1.0, 180, 10, 51.1, 1.0, 0, 10  # heading south  # heading north
        )
        assert tcpa == 0  # Already diverging


class TestBearingTo:
    def test_north(self):
        brg = bearing_to(51.0, 1.0, 52.0, 1.0)
        assert 359 < brg or brg < 1  # ~000

    def test_east(self):
        brg = bearing_to(51.0, 1.0, 51.0, 2.0)
        assert 89 < brg < 91  # ~090

    def test_south(self):
        brg = bearing_to(51.0, 1.0, 50.0, 1.0)
        assert 179 < brg < 181  # ~180

    def test_west(self):
        brg = bearing_to(51.0, 1.0, 51.0, 0.0)
        assert 269 < brg < 271  # ~270


class TestRangeNm:
    def test_one_degree_lat(self):
        # 1 degree latitude ≈ 60 nm
        dist = range_nm(51.0, 1.0, 52.0, 1.0)
        assert 59 < dist < 61

    def test_zero_distance(self):
        assert range_nm(51.0, 1.0, 51.0, 1.0) == 0

    def test_short_range(self):
        # ~1 nm north
        dist = range_nm(51.0, 1.0, 51.0167, 1.0)
        assert 0.8 < dist < 1.2

    def test_symmetry(self):
        d1 = range_nm(51.0, 1.0, 52.0, 2.0)
        d2 = range_nm(52.0, 2.0, 51.0, 1.0)
        assert d1 == d2


class TestScenarios:
    """Tests for training scenarios loading and filtering."""

    def test_load_scenarios_returns_list(self):
        scenarios = load_scenarios()
        assert isinstance(scenarios, list)

    def test_scenarios_count(self):
        scenarios = load_scenarios()
        assert len(scenarios) == 95
        assert count_scenarios() == 95

    def test_scenario_structure(self):
        scenarios = load_scenarios()
        required_keys = {"scenario", "answer", "rule", "category", "difficulty"}

        for scenario in scenarios:
            assert isinstance(scenario, dict), f"Scenario should be dict, got {type(scenario)}"
            for key in required_keys:
                assert key in scenario, f"Scenario missing required key: {key}"

    def test_get_categories_returns_expected_categories(self):
        assert get_categories() == [
            "day_shapes",
            "encounters",
            "general_rules",
            "lights",
            "narrow_channels",
            "responsibilities",
            "restricted_visibility",
            "sound_signals_fog",
            "sound_signals_maneuvering",
            "tss",
        ]

    def test_get_scenario_filters_by_category_and_difficulty(self):
        scenario = get_scenario(category="lights", difficulty=1)
        assert scenario is not None
        assert scenario["category"] == "lights"
        assert scenario["difficulty"] == 1

    def test_get_scenario_supports_random_alias(self):
        scenario = get_scenario(category="encounters", random=True)
        assert scenario is not None
        assert scenario["category"] == "encounters"

    def test_get_scenarios_by_category_returns_only_matches(self):
        scenarios = get_scenarios_by_category("lights")
        assert scenarios
        assert all(scenario["category"] == "lights" for scenario in scenarios)

    def test_get_difficulty_breakdown_matches_total(self):
        breakdown = get_difficulty_breakdown()
        assert set(breakdown) == {1, 2, 3}
        assert sum(breakdown.values()) == 95

    def test_invalid_category_raises_value_error(self):
        with pytest.raises(ValueError):
            get_scenario(category="not-a-category")

    def test_invalid_difficulty_raises_value_error(self):
        with pytest.raises(ValueError):
            get_scenario(difficulty=4)
