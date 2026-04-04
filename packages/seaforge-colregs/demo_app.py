#!/usr/bin/env python3
"""Interactive Flask demo for testing the seaforge-colregs package."""

from __future__ import annotations

import argparse
import random
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, render_template, request

from seaforge_colregs import (
    classify_encounter,
    count_scenarios,
    get_categories,
    get_difficulty_breakdown,
    load_scenarios,
)


class DemoSession:
    """Track a user's in-memory demo state."""

    def __init__(self, session_id: int):
        self.id = session_id
        self.demo: Optional[str] = None
        self.current_question = 0
        self.score = 0
        self.answers: List[Dict[str, Any]] = []
        self.scenarios: List[Dict[str, Any]] = []
        # DP Training state
        self.dp_phase = 0
        self.dp_position = {"x": 100.0, "y": 100.0}
        self.dp_target = {"x": 0.0, "y": 0.0}
        self.dp_error = 141.4  # Initial distance
        self.dp_fuel = 100.0
        self.dp_on_station_time = 0.0

    def start_trainer(self, num_questions: int = 5) -> None:
        """Start an interactive trainer session with unique scenarios."""
        total_available = count_scenarios()
        requested = max(1, min(num_questions, total_available))
        self.demo = "trainer"
        self.current_question = 0
        self.score = 0
        self.answers = []
        self.scenarios = random.sample(load_scenarios(), k=requested)

    def start_bridge_sim(self) -> None:
        """Start the bridge simulator session."""
        self.demo = "bridge"
        self.current_question = 0
        self.score = 0
        self.answers = []
        self.scenarios = [
            {
                "encounter": 1,
                "vessel": "Container Ship A",
                "own_cog": 90,
                "target_cog": 270,
                "rel_bearing": 180,
                "distance": 6.33,
                "bearing": 89.9,
            },
            {
                "encounter": 2,
                "vessel": "Fishing Vessel B",
                "own_cog": 90,
                "target_cog": 180,
                "rel_bearing": 0,
                "distance": 6.0,
                "bearing": 0.0,
            },
            {
                "encounter": 3,
                "vessel": "Tanker C",
                "own_cog": 90,
                "target_cog": 90,
                "rel_bearing": 180,
                "distance": 6.0,
                "bearing": 180.0,
            },
        ]

    def start_dp_sim(self) -> None:
        """Start the OOW DP training session."""
        self.demo = "dp"
        self.dp_phase = 0
        self.dp_position = {"x": 100.0, "y": 100.0}
        self.dp_target = {"x": 0.0, "y": 0.0}
        self.dp_error = 141.4  # sqrt(100^2 + 100^2)
        self.dp_fuel = 100.0
        self.dp_on_station_time = 0.0
        self.answers = []


def generate_trainer_options(scenario: Dict[str, Any]) -> List[str]:
    """Generate 4 multiple-choice options from a scenario.

    Returns a shuffled list with realistic, confusing distractors that require actual knowledge.
    """
    correct_answer = scenario.get("answer", "Unknown")
    category = scenario.get("category", "").lower()

    # Category-specific PLAUSIBLE distractors (commonly confused answers)
    distractors_map = {
        "lights": [
            "Vessel engaged in fishing (when it's power-driven)",
            "Vessel at anchor (when underway)",
            "Constrained by draft (when not restricted)",
            "Vessel not under command (when it's anchored)",
        ],
        "day_shapes": [
            "Ball over two cones (different meaning)",
            "Two balls over a cone (restricted maneuverability)",
            "Diamond with cone below (vessel aground)",
            "Single cone (different rule applies)",
        ],
        "encounters": [
            "Both vessels alter course to port (Rule 14 mistake)",
            "Give-way vessel maintains course (collision risk)",
            "Stand-on vessel initiates early action (timing)",
            "Neither vessel alters (assumes earliest awareness)",
        ],
        "sound_signals": [
            "One prolonged blast (wrong signal intent)",
            "Three short blasts (backing signal, not turn)",
            "Repeated short blasts (danger signal, not helm)",
            "One long one short (different maneuver)",
        ],
        "tss": [
            "Vessel crossing traffic lane (opposing direction)",
            "Vessel joining separation zone (wrong entry point)",
            "Vessel overtaking in lane (same direction but restricted)",
            "Vessel anchored in lane (different prohibition)",
        ],
        "narrow": [
            "Vessel meeting head-on (wider waters rule applies)",
            "Give-way vessel in narrow channel (wrong role assessment)",
            "Smaller vessel gives way (not applicable in narrow channels)",
            "Any vessel can alter freely (channels restrict maneuvers)",
        ],
        "default": [
            "Different rule applies to this situation",
            "Applicable only in restricted visibility",
            "Requires prior communication between vessels",
            "Depends on vessel maneuverability class",
        ],
    }

    # Get distractors for category, fallback to default
    distractors = distractors_map.get(category, distractors_map["default"])

    # Build options: correct answer + 3 random distractors
    # Shuffle all 4 to randomize position
    options = [correct_answer] + random.sample(distractors, 3)
    random.shuffle(options)
    return options


def serialize_trainer_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Shape a trainer scenario for the frontend."""
    return {
        "category": scenario.get("category", "Unknown").upper(),
        "difficulty": "⭐" * scenario.get("difficulty", 1),
        "question": scenario.get("scenario"),
        "rule": scenario.get("rule"),
        "answer": scenario.get("answer", ""),
        "options": generate_trainer_options(scenario),
    }


def serialize_bridge_encounter(encounter: Dict[str, Any]) -> Dict[str, Any]:
    """Shape a bridge encounter for the frontend."""
    return {
        "vessel_name": encounter["vessel"],
        "own_cog": encounter["own_cog"],
        "target_cog": encounter["target_cog"],
        "rel_bearing": encounter["rel_bearing"],
        "distance_nm": encounter["distance"],
        "bearing": encounter["bearing"],
        "question": (
            f"Encounter with {encounter['vessel']}. " "What is your role? (give-way or stand-on)"
        ),
    }


def create_app() -> Flask:
    """Create the interactive demo Flask app."""
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.config["DEMO_SESSIONS"] = {}

    @app.route("/")
    def index() -> str:
        return render_template("demo_dashboard.html")

    @app.route("/api/library/stats")
    def library_stats():
        scenarios = load_scenarios()
        categories = get_categories()
        counts_by_category = {
            category: count_scenarios(category=category) for category in categories
        }
        return jsonify(
            {
                "total_scenarios": len(scenarios),
                "categories": categories,
                "counts_by_category": counts_by_category,
                "difficulty_breakdown": get_difficulty_breakdown(),
            }
        )

    @app.route("/api/trainer/start", methods=["POST"])
    def trainer_start():
        data = request.get_json(silent=True) or {}
        num_questions = int(data.get("num_questions", 5))
        session_id = int(data.get("session_id", random.randint(1000, 9999)))

        session = DemoSession(session_id)
        session.start_trainer(num_questions)
        app.config["DEMO_SESSIONS"][session_id] = session

        return jsonify(
            {
                "session_id": session_id,
                "demo": "trainer",
                "total_questions": len(session.scenarios),
                "current_question": 1,
                "scenario": serialize_trainer_scenario(session.scenarios[0]),
            }
        )

    @app.route("/api/trainer/answer", methods=["POST"])
    def trainer_answer():
        data = request.get_json(silent=True) or {}
        session_id = data.get("session_id")
        user_answer = data.get("answer", "").strip()

        if session_id not in app.config["DEMO_SESSIONS"]:
            return jsonify({"error": "Session not found"}), 404

        session = app.config["DEMO_SESSIONS"][session_id]
        current_idx = session.current_question
        scenario = session.scenarios[current_idx]

        correct_answer = scenario.get("answer", "")
        # For multiple-choice: exact match after stripping whitespace
        is_correct = user_answer == correct_answer

        if is_correct:
            session.score += 1

        feedback = {
            "question": current_idx + 1,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "correct": is_correct,
            "rule": scenario.get("rule"),
            "category": scenario.get("category"),
        }
        session.answers.append(feedback)
        session.current_question += 1

        if session.current_question < len(session.scenarios):
            next_scenario = session.scenarios[session.current_question]
            return jsonify(
                {
                    "status": "next_question",
                    "feedback": feedback,
                    "current_question": session.current_question + 1,
                    "total_questions": len(session.scenarios),
                    "scenario": serialize_trainer_scenario(next_scenario),
                }
            )

        accuracy = (session.score / len(session.scenarios)) * 100
        return jsonify(
            {
                "status": "complete",
                "score": session.score,
                "total": len(session.scenarios),
                "accuracy": f"{accuracy:.0f}%",
                "answers": session.answers,
            }
        )

    @app.route("/api/bridge/start", methods=["POST"])
    def bridge_start():
        data = request.get_json(silent=True) or {}
        session_id = int(data.get("session_id", random.randint(1000, 9999)))

        session = DemoSession(session_id)
        session.start_bridge_sim()
        app.config["DEMO_SESSIONS"][session_id] = session

        return jsonify(
            {
                "session_id": session_id,
                "demo": "bridge",
                "total_encounters": len(session.scenarios),
                "current_encounter": 1,
                "scenario": serialize_bridge_encounter(session.scenarios[0]),
            }
        )

    @app.route("/api/bridge/answer", methods=["POST"])
    def bridge_answer():
        data = request.get_json(silent=True) or {}
        session_id = data.get("session_id")
        user_role = data.get("role", "").lower()

        if session_id not in app.config["DEMO_SESSIONS"]:
            return jsonify({"error": "Session not found"}), 404

        session = app.config["DEMO_SESSIONS"][session_id]
        current_idx = session.current_question
        encounter = session.scenarios[current_idx]

        situation, correct_role, rule, action = classify_encounter(
            encounter["own_cog"],
            encounter["target_cog"],
            encounter["rel_bearing"],
        )

        is_correct = user_role.replace(" ", "-") == correct_role.replace(" ", "-")

        if is_correct:
            session.score += 1

        feedback = {
            "encounter": current_idx + 1,
            "vessel": encounter["vessel"],
            "situation": situation,
            "user_role": user_role,
            "correct_role": correct_role,
            "rule": rule,
            "action": action,
            "correct": is_correct,
        }
        session.answers.append(feedback)
        session.current_question += 1

        if session.current_question < len(session.scenarios):
            next_encounter = session.scenarios[session.current_question]
            return jsonify(
                {
                    "status": "next_encounter",
                    "feedback": feedback,
                    "current_encounter": session.current_question + 1,
                    "total_encounters": len(session.scenarios),
                    "scenario": serialize_bridge_encounter(next_encounter),
                }
            )

        accuracy = (session.score / len(session.scenarios)) * 100
        return jsonify(
            {
                "status": "complete",
                "score": session.score,
                "total": len(session.scenarios),
                "accuracy": f"{accuracy:.0f}%",
                "answers": session.answers,
            }
        )

    @app.route("/api/colregs/classify", methods=["POST"])
    def classify():
        data = request.get_json(silent=True) or {}
        own_cog = data.get("own_cog")
        target_cog = data.get("target_cog")
        rel_bearing = data.get("rel_bearing")

        if None in [own_cog, target_cog, rel_bearing]:
            return jsonify({"error": "Missing parameters"}), 400

        situation, role, rule, action = classify_encounter(
            own_cog,
            target_cog,
            rel_bearing,
        )

        return jsonify(
            {
                "situation": situation,
                "role": role,
                "rule": rule,
                "action": action,
            }
        )

    @app.route("/api/dp/start", methods=["POST"])
    def dp_start():
        """Start OOW DP training session."""
        data = request.get_json(silent=True) or {}
        session_id = int(data.get("session_id", random.randint(1000, 9999)))

        session = DemoSession(session_id)
        session.start_dp_sim()
        app.config["DEMO_SESSIONS"][session_id] = session

        return jsonify(
            {
                "session_id": session_id,
                "demo": "dp",
                "phase": 1,
                "phase_name": "Initial Approach",
                "scenario": {
                    "vessel_name": "MV DP SENTINEL",
                    "start_position": {"x": 100.0, "y": 100.0},
                    "target_position": {"x": 0.0, "y": 0.0},
                    "wind": {"speed": 25, "direction": 180},
                    "current": {"speed": 1.5, "direction": 90},
                    "initial_error": 141.4,
                },
            }
        )

    @app.route("/api/dp/control", methods=["POST"])
    def dp_control():
        """Process DP training phase advancement."""
        data = request.get_json(silent=True) or {}
        session_id = data.get("session_id")

        if session_id not in app.config["DEMO_SESSIONS"]:
            return jsonify({"error": "Session not found"}), 404

        session = app.config["DEMO_SESSIONS"][session_id]

        # Simulate phase progression with error reduction
        phase_names = ["Initial Approach", "Fine Positioning", "Station-Keeping"]
        error_reductions = [50, 25, 5]  # Expected error reduction per phase

        # Simulate user reducing error (in real scenario, based on thruster commands)
        error_reduction = error_reductions[session.dp_phase] if session.dp_phase < 3 else 0
        fuel_cost = (3 - session.dp_phase) * 5  # More fuel needed in earlier phases

        session.dp_error = max(0, session.dp_error - error_reduction)
        session.dp_fuel = max(0, session.dp_fuel - fuel_cost)
        session.dp_phase += 1

        # Calculate on-station percentage (when error < 10m in phase 3)
        if session.dp_phase > 3:
            on_station_pct = 100 if session.dp_error < 10 else max(0, 100 - (session.dp_error * 5))
        else:
            on_station_pct = 0

        session.dp_on_station_time = on_station_pct

        # Determine assessment
        if session.dp_phase <= 3:
            return jsonify(
                {
                    "status": "next_phase",
                    "phase": session.dp_phase + 1,
                    "phase_name": phase_names[session.dp_phase] if session.dp_phase < 3 else "Complete",
                    "error": round(session.dp_error, 1),
                    "fuel": round(session.dp_fuel, 1),
                    "on_station": round(on_station_pct, 1),
                }
            )

        # Training complete
        if session.dp_fuel > 60 and session.dp_error < 10:
            assessment = "Excellent"
            points = 95
        elif session.dp_fuel > 40 and session.dp_error < 15:
            assessment = "Good"
            points = 80
        elif session.dp_fuel > 20:
            assessment = "Fair"
            points = 60
        else:
            assessment = "Poor"
            points = 40

        return jsonify(
            {
                "status": "complete",
                "assessment": assessment,
                "points": points,
                "final_error": round(session.dp_error, 1),
                "final_fuel": round(session.dp_fuel, 1),
                "on_station_time": round(on_station_pct, 1),
            }
        )

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "version": "0.1.0a1"})

    return app


def main() -> None:
    """Run the local demo server."""
    parser = argparse.ArgumentParser(description="Run the interactive COLREGS demo")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Flask debug mode",
    )
    args = parser.parse_args()

    app = create_app()

    print("\n" + "=" * 70)
    print("SEAFORGE COLREGS INTERACTIVE DEMO")
    print("=" * 70)
    print(f"\nStarting Flask app on http://{args.host}:{args.port}\n")
    print("Open your browser and navigate to:")
    print(f"   http://{args.host}:{args.port}\n")
    print("Tools available:")
    print("   • Interactive COLREGS Trainer")
    print("   • Bridge Simulator")
    print("   • Rule Sandbox")
    print("=" * 70 + "\n")

    app.run(debug=args.debug, port=args.port, host=args.host)


if __name__ == "__main__":
    main()
