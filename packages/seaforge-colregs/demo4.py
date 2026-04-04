#!/usr/bin/env python3
"""
Demo 4: KONGSBERG BRIDGE SIMULATOR CONCEPT
A realistic multi-vessel encounter scenario testing COLREGS decision-making
under time pressure with environmental conditions.

Simulates: Constrained navigation area with 3 simultaneous encounters.
Scoring: Rule correctness + decision speed + action effectiveness.
"""

import json
import math
import time
from typing import Dict, List, Tuple
from seaforge_colregs import classify_encounter, compute_cpa_tcpa, bearing_to, range_nm, relative_bearing


class BridgeSimulatorScenario:
    """Multi-vessel encounter scenario with time progression."""

    def __init__(self):
        self.own_vessel = {
            "name": "MV SEAFORGE",
            "position": [58.2, 5.7],  # Bergen harbor approach
            "cog": 90,  # Heading East
            "sog": 12,   # Speed 12 knots
            "length": 190,  # meters
            "beam": 32,
            "status": "underway"
        }

        # Three simultaneous encounters
        self.targets = [
            {
                "name": "CONTAINER SHIP A",
                "position": [58.2, 5.9],  # 1.5nm East
                "cog": 270,  # Heading West (head-on)
                "sog": 14,
                "class": "container",
                "rule_type": "head_on"
            },
            {
                "name": "FISHING VESSEL B",
                "position": [58.3, 5.7],  # 0.6nm North (crossing)
                "cog": 180,  # Heading South
                "sog": 8,
                "class": "fishing",
                "rule_type": "crossing"
            },
            {
                "name": "TANKER C",
                "position": [58.1, 5.7],  # 0.6nm South (overtaking)
                "cog": 90,  # Same direction
                "sog": 15,  # Faster (overtaking)
                "class": "tanker",
                "rule_type": "overtaking"
            }
        ]

        self.scenario_time = 0  # seconds elapsed
        self.decisions = []
        self.violations = []
        self.score = {"rule_correct": 0, "decision_time": 0, "total": 0}

    def progress_scenario(self, seconds: int = 60) -> None:
        """Advance scenario time, update vessel positions."""
        for vessel in [self.own_vessel] + self.targets:
            # Convert COG/SOG to position change (simplified)
            rad = math.radians(vessel["cog"])
            lat_change = (vessel["sog"] * seconds) / 3600 / 60  # nm to degrees approximation
            vessel["position"][0] += lat_change * math.cos(rad)
            vessel["position"][1] += lat_change * math.sin(rad)
        self.scenario_time += seconds

    def evaluate_encounter(self, target_idx: int, decision: str) -> Dict:
        """Evaluate a COLREGS decision against a target vessel."""
        target = self.targets[target_idx]
        own_lat, own_lon = self.own_vessel["position"]
        tgt_lat, tgt_lon = target["position"]

        brg = bearing_to(own_lat, own_lon, tgt_lat, tgt_lon)
        dist = range_nm(own_lat, own_lon, tgt_lat, tgt_lon)
        rel_brg = relative_bearing(self.own_vessel["cog"], brg)

        # Get COLREGS classification
        situation, role, rule, action = classify_encounter(
            self.own_vessel["cog"],
            target["cog"],
            rel_brg
        )

        # Calculate collision risk
        cpa, tcpa, _, _ = compute_cpa_tcpa(
            own_lat, own_lon, self.own_vessel["cog"], self.own_vessel["sog"],
            tgt_lat, tgt_lon, target["cog"], target["sog"]
        )

        # Score the decision
        correct = (decision.lower() == role.lower())
        decision_time = min(300 / max(1, self.scenario_time), 100)  # Speed bonus
        collision_risk = "CRITICAL" if cpa < 0.3 else "HIGH" if cpa < 0.5 else "MODERATE"

        result = {
            "target": target["name"],
            "distance_nm": round(dist, 2),
            "bearing": round(brg, 1),
            "cpa_nm": round(cpa, 3),
            "tcpa_min": round(tcpa, 1),
            "situation": situation,
            "correct_role": role,
            "player_decision": decision,
            "correct": correct,
            "rule": rule,
            "required_action": action,
            "collision_risk": collision_risk,
            "points": 10 if correct else 0,
            "time_bonus": round(decision_time, 1)
        }

        if correct:
            self.score["rule_correct"] += 1
        else:
            self.violations.append(f"{target['name']}: Expected {role}, got {decision}")

        self.decisions.append(result)
        return result

    def get_summary(self) -> Dict:
        """Get scenario summary with scoring."""
        total_encounters = len(self.targets)
        correct_decisions = sum(1 for d in self.decisions if d["correct"])

        return {
            "scenario": "Bergen Harbor Multi-Vessel Approach",
            "duration_seconds": self.scenario_time,
            "encounters": total_encounters,
            "decisions_made": len(self.decisions),
            "correct_decisions": correct_decisions,
            "accuracy": f"{(correct_decisions / total_encounters * 100):.0f}%" if total_encounters > 0 else "0%",
            "violations": self.violations,
            "all_decisions": self.decisions,
            "final_score": f"{correct_decisions}/{total_encounters}"
        }


def run_bridge_simulator_demo() -> Dict:
    """Run the Kongsberg bridge simulator demo."""
    print("\n" + "="*70)
    print("DEMO 4: KONGSBERG BRIDGE SIMULATOR CONCEPT")
    print("="*70)
    print("\n🌊 SCENARIO: Bergen Harbor Approach — Multiple Simultaneous Encounters\n")

    sim = BridgeSimulatorScenario()

    # Display initial state
    print("📍 OWN VESSEL:")
    print(f"   {sim.own_vessel['name']} | Hdg {sim.own_vessel['cog']}° | {sim.own_vessel['sog']} kts")
    print(f"   Position: {sim.own_vessel['position'][0]:.2f}°N, {sim.own_vessel['position'][1]:.2f}°E\n")

    print("⚓ TARGETS DETECTED:\n")
    for idx, target in enumerate(sim.targets, 1):
        dist = range_nm(
            sim.own_vessel["position"][0], sim.own_vessel["position"][1],
            target["position"][0], target["position"][1]
        )
        brg = bearing_to(
            sim.own_vessel["position"][0], sim.own_vessel["position"][1],
            target["position"][0], target["position"][1]
        )
        print(f"   {idx}. {target['name']:20s} | Bearing {brg:3.0f}° | Distance {dist:.2f}nm")
        print(f"      Hdg {target['cog']}° | {target['sog']} kts | Type: {target['class'].upper()}\n")

    print("📋 SCENARIO DECISIONS:\n")

    # Simulate decision-making for each encounter
    decisions_made = [
        ("stand-on", "CONTAINER SHIP A - Head-on situation"),
        ("give-way", "FISHING VESSEL B - Crossing situation"),
        ("give-way", "TANKER C - Overtaking situation")
    ]

    for i, (decision, description) in enumerate(decisions_made):
        print(f"   [{i+1}] {description}")
        result = sim.evaluate_encounter(i, decision)

        status = "✓ CORRECT" if result["correct"] else "✗ INCORRECT"
        print(f"       Your decision: {decision.upper():12s} {status}")
        print(f"       COLREGS: {result['situation'].upper():15s} → {result['correct_role'].upper()}")
        print(f"       Collision Risk: {result['collision_risk']:10s} (CPA {result['cpa_nm']:.3f}nm)\n")

    # Progress time and recalculate
    sim.progress_scenario(300)

    # Final summary
    summary = sim.get_summary()
    print("\n" + "="*70)
    print("SCENARIO COMPLETE — PERFORMANCE REVIEW")
    print("="*70)
    print(f"\nAccuracy: {summary['correct_decisions']}/{summary['encounters']} decisions correct ({summary['accuracy']})")
    print(f"Final Score: {summary['final_score']}")

    if summary['violations']:
        print("\n⚠️  VIOLATIONS:")
        for v in summary['violations']:
            print(f"   - {v}")
    else:
        print("\n✓ No violations! Excellent COLREGS knowledge.")

    print("\n📊 ENCOUNTER DETAILS:")
    for d in summary['all_decisions']:
        print(f"\n   {d['target']}:")
        print(f"      Distance: {d['distance_nm']}nm | Bearing: {d['bearing']}°")
        print(f"      CPA: {d['cpa_nm']}nm in {d['tcpa_min']}min | Situation: {d['situation']}")
        print(f"      Rule: {d['rule']}")

    print("\n" + "="*70 + "\n")

    return {
        "status": "pass",
        "demo": "bridge_simulator",
        "summary": summary,
        "decisions": summary['all_decisions']
    }


if __name__ == "__main__":
    result = run_bridge_simulator_demo()
    print(f"Demo result: {json.dumps(result, indent=2)}")
