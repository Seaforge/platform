# IBS Smart Advisor - Technical Test Scenarios

This document outlines the technical test scenarios for the new Integrated Bridge System (IBS) Smart Advisor architecture. The tests are designed to validate the functionality, performance, and resilience of the system's key components.

## Test Scenario Matrix

| **ID** | **Component** | **Test Type** | **Scenario Description** | **Complexity** | **Success Criteria** | **Notes** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FL-01** | Flask Backend | Unit | Test `/api/v1/status` endpoint for `200 OK` response. | Simple | Returns `{"status": "ok"}`. | Basic health check. |
| **FL-02** | Flask Backend | Integration | Test `/api/v1/ais/targets` endpoint with mock data source. | Simple | Returns a valid GeoJSON FeatureCollection with at least 1 mock target. | Validates data serialization. |
| **FL-03** | Flask Backend | Integration | Test `/api/v1/ais/targets` endpoint with pagination (`?page=2&limit=50`). | Simple | Returns the second page of 50 targets. | Verifies pagination logic. |
| **FL-04** | Flask Backend | Load | Simulate 100 concurrent requests to `/api/v1/ais/targets`. | Medium | Average response time remains < 200ms. No 5xx errors. | Gunicorn worker stress test. |
| **FL-05** | Flask Backend | Error Handling | Request a non-existent route like `/api/v1/foo`. | Simple | Returns a `404 Not Found` error in JSON format. | Validates error handling middleware. |
| **CZ-01** | Cesium.js | Performance | Render 1,000 static mock AIS targets (Point entities). | Medium | Initial load time < 2 seconds. Frame rate remains >= 30 FPS when panning/zooming. | Establishes baseline rendering performance. |
| **CZ-02** | Cesium.js | Performance | Render 5,000 static mock AIS targets. | Complex | Frame rate remains >= 20 FPS. | Stress test for high-density traffic areas. |
| **CZ-03** | Cesium.js | Performance | Update positions of 1,000 mock AIS targets every 1 second. | Complex | Frame rate remains >= 25 FPS. No visible stuttering. | Simulates real-time vessel movement. |
| **CZ-04** | Cesium.js | Interaction | Click on an AIS target entity. | Simple | An info-box appears with the correct vessel details. | Validates user interaction and data binding. |
| **CZ-05** | Cesium.js | Filtering | Apply a filter to show only cargo vessels. | Medium | Only entities with `shipType: "cargo"` are visible. | Tests client-side filtering logic. |
| **DG-01** | deck.gl | Unit | Render a single static tether line using `LineLayer`. | Simple | The line is rendered correctly between two specified points. | Basic layer rendering test. |
| **DG-02** | deck.gl | Integration | Fetch tether stress data from a mock `/api/v1/tether/stress` endpoint. | Medium | The tether line is color-graded according to the mock stress data. | Validates data-driven visualization. |
| **DG-03** | deck.gl | Visualization | Apply Morison equation loads to the tether, generating >100 stress points. | Complex | The line color gradient smoothly represents the calculated stress distribution. | Tests the core visualization feature for tether analysis. |
| **DG-04** | deck.gl | Performance | Update tether stress visualization with new data every 500ms. | Complex | UI remains responsive. Frame rate >= 30 FPS. No memory leaks over a 5-minute period. | Simulates real-time environmental load changes. |
| **DG-05** | deck.gl | Interaction | Hover over a point on the tether line. | Medium | A tooltip appears showing the precise stress value at that point. | Enhances usability for detailed analysis. |

## Test Environment

-   **Backend:** Python 3.11+, Flask 2.x, Gunicorn
-   **Frontend:** Modern browser with WebGL2 support (Chrome, Firefox, Edge)
-   **Data Generation:** Mock data scripts for AIS targets and Morison equation outputs.
-   **Load Testing:** `k6` or `JMeter` for simulating concurrent users.
-   **Performance Monitoring:** Browser DevTools (Performance and Memory tabs).
