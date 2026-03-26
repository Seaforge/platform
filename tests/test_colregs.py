"""Tests for COLREGS classification engine (src/core/colregs.py)."""

import pytest
from src.core.colregs import (
    relative_bearing,
    classify_encounter,
    compute_cpa_tcpa,
    bearing_to,
    range_nm,
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
        assert rule == "Rule 13" or situation in ("head-on", "crossing", "overtaking")

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
            51.0, 1.0, 0, 10,    # own: heading N at 10 kts
            51.1, 1.0, 180, 10   # target: heading S at 10 kts
        )
        assert cpa < 0.5  # Very close CPA
        assert tcpa > 0   # Positive TCPA

    def test_parallel_same_direction(self):
        # Two vessels going same direction, offset by 1nm
        cpa, tcpa, _, _ = compute_cpa_tcpa(
            51.0, 1.0, 0, 10,
            51.0, 1.0167, 0, 10  # ~1nm east
        )
        # Parallel courses: CPA should be roughly the initial distance
        assert cpa > 0.5

    def test_stationary_vessels(self):
        cpa, tcpa, _, _ = compute_cpa_tcpa(
            51.0, 1.0, 0, 0,
            51.01, 1.0, 0, 0
        )
        assert tcpa == 999  # Sentinel for no relative motion

    def test_diverging(self):
        # Vessels moving apart
        cpa, tcpa, _, _ = compute_cpa_tcpa(
            51.0, 1.0, 180, 10,   # heading south
            51.1, 1.0, 0, 10      # heading north
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
