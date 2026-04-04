"""Tests for the interactive demo Flask app."""

from demo_app import create_app


def test_health_endpoint():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_library_stats_endpoint():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/library/stats")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["total_scenarios"] == 95
    assert "lights" in payload["categories"]
    assert payload["counts_by_category"]["lights"] == 20


def test_classifier_endpoint():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/colregs/classify",
        json={"own_cog": 0, "target_cog": 270, "rel_bearing": 45},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["situation"] == "crossing"
    assert payload["role"] == "give-way"
    assert payload["rule"] == "Rule 15"


def test_trainer_flow_returns_feedback_and_completion():
    app = create_app()
    client = app.test_client()

    start_response = client.post(
        "/api/trainer/start", json={"num_questions": 1, "session_id": 4321}
    )
    start_payload = start_response.get_json()
    session = app.config["DEMO_SESSIONS"][start_payload["session_id"]]
    scenario = session.scenarios[0]

    answer_response = client.post(
        "/api/trainer/answer",
        json={"session_id": 4321, "answer": scenario["answer"]},
    )
    answer_payload = answer_response.get_json()

    assert start_response.status_code == 200
    assert start_payload["current_question"] == 1
    assert answer_response.status_code == 200
    assert answer_payload["status"] == "complete"
    assert answer_payload["score"] == 1


def test_bridge_flow_returns_feedback():
    app = create_app()
    client = app.test_client()

    start_response = client.post("/api/bridge/start", json={"session_id": 9876})
    answer_response = client.post(
        "/api/bridge/answer",
        json={"session_id": 9876, "role": "stand-on"},
    )
    answer_payload = answer_response.get_json()

    assert start_response.status_code == 200
    assert answer_response.status_code == 200
    assert answer_payload["status"] == "next_encounter"
    assert "feedback" in answer_payload
    assert "correct_role" in answer_payload["feedback"]
