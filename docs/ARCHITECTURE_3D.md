# SeaForge 3D Globe MVP: Technical Specification

## 1. Overview

This document outlines the architecture for upgrading the SeaForge platform from a 2D Leaflet map to a 3D globe experience. The goal is to provide a "Google Earth for the Ocean" interface, enhancing situational awareness and data visualization for seafarers.

This upgrade will be an MVP (Minimum Viable Product) focused on integrating core 3D globe functionality, data layers for AIS and weather, and a backend service for A* voyage optimization.

The key technology changes are:
-   **Replacing Leaflet.js with Cesium.js** for the core globe rendering.
-   **Using deck.gl** for high-performance data visualization layers (AIS vessels, weather).
-   **Integrating a commercial routing API** (e.g., Searoutes, Datalastic) on the backend for voyage planning.

## 2. Architecture Changes

### 2.1. Frontend Architecture

The frontend will move from a pure Leaflet implementation to a hybrid approach using Cesium.js as the base globe and deck.gl for data overlays.

-   **`index.html`**: Will be updated to include the Cesium.js and deck.gl libraries. The main map container div will be initialized as a Cesium Viewer.
-   **`static/js/app.js`**: Will be significantly refactored.
    -   The Leaflet map initialization will be replaced with Cesium Viewer initialization.
    -   Map event handlers (zoom, pan) will be updated to use the Cesium Camera API.
    -   Data fetching logic will remain the same, but the rendering will be passed to new deck.gl layers.

### 2.2. Data Layers (deck.gl)

deck.gl will be used to render dynamic data on top of the Cesium globe. This provides better performance and visual quality for large datasets compared to native Cesium entities.

-   **AIS Layer**: A `ScatterplotLayer` or `IconLayer` will be used to display AIS targets. This layer will be updated in real-time from the existing `/api/ais/vessels` endpoint.
-   **Weather Layer**: A `TileLayer` or `BitmapLayer` will be used to display weather data (wind, waves, currents) from Open-Meteo and other sources.

### 2.3. Backend Architecture

The existing Flask backend will be extended to support voyage optimization.

-   **New Route Optimization Endpoint**: A new API endpoint, `/api/navigation/optimize-route`, will be created.
-   **Routing API Integration**: This endpoint will act as a proxy to a commercial routing service. It will take start/end coordinates and voyage parameters, call the external API, and return an optimized route as a GeoJSON LineString.

## 3. Backend API for Voyage Optimization

A new endpoint will be added to the `navigation.py` blueprint.

### POST `/api/navigation/optimize-route`

This endpoint computes an optimized voyage plan using a third-party service.

**Request Body:**

```json
{
  "origin": { "lat": 51.5074, "lon": -0.1278 },
  "destination": { "lat": 40.7128, "lon": -74.0060 },
  "parameters": {
    "vessel_type": "tanker",
    "speed_kn": 12,
    "constraints": ["avoid_piracy", "eca_zones"]
  }
}
```

**Backend Logic:**

1.  Receive the request.
2.  Validate the input parameters.
3.  Format a request to the chosen commercial routing API (e.g., Searoutes).
4.  Send the request with an API key stored in server-side configuration.
5.  Receive the optimized route from the external API.
6.  Format the response as a GeoJSON `FeatureCollection` containing the route `LineString` and waypoints `Point`s.
7.  Return the GeoJSON to the client.

**Response Body (Success):**

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [-0.1278, 51.5074],
          /* ... more coordinates ... */
          [-74.0060, 40.7128]
        ]
      },
      "properties": {
        "total_distance_nm": 3200,
        "estimated_duration_h": 266
      }
    }
    /* ... additional Point features for waypoints ... */
  ]
}
```

## 4. Data Flow

1.  **User opens SeaForge**: The browser loads `index.html`.
2.  **Globe Initialization**: `app.js` initializes the Cesium Viewer.
3.  **Data Layer Initialization**: `app.js` creates deck.gl layers for AIS and weather.
4.  **AIS Data**: The frontend periodically fetches AIS data from `/api/ais/vessels` and updates the deck.gl AIS layer.
5.  **Voyage Planning**:
    -   The user clicks a "Plan Voyage" button on the UI.
    -   The UI prompts for origin, destination, and parameters.
    -   On submission, the frontend sends a POST request to `/api/navigation/optimize-route`.
    -   The Flask backend calls the external routing API.
    -   The backend returns the optimized route as GeoJSON.
    -   The frontend renders the GeoJSON route on the Cesium globe using a `PathLayer` in deck.gl.

## 5. Initial File Changes

To begin implementation of this MVP, the following files will need to be created or modified:

**1. `templates/index.html`**
-   **Modification**: Add `<script>` and `<link>` tags for Cesium.js and deck.gl libraries.
-   **Modification**: Change the map container `<div>` to be compatible with Cesium.

**2. `static/js/app.js`**
-   **Modification**: Remove Leaflet initialization code.
-   **Modification**: Add Cesium Viewer initialization code.
-   **Modification**: Implement data fetching and rendering logic for deck.gl layers (AIS, Weather).
-   **Modification**: Add UI logic for the new voyage planning feature.

**3. `src/api/navigation.py`**
-   **Modification**: Add a new Flask route for `POST /api/navigation/optimize-route`.
-   **Modification**: Implement the logic to call the external routing API (using the `requests` library). A placeholder or mock API can be used initially.

**4. `requirements.txt`**
-   **Modification**: Add the `requests` library if it's not already present.

**5. `docs/ARCHITECTURE_3D.md`**
-   **Creation**: This file will be created to document the new architecture.

This MVP provides a clear path to integrating 3D functionality and advanced voyage planning into the SeaForge platform, laying the foundation for future development.
