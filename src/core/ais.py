"""AIS stream processor — connects to aisstream.io WebSocket for live vessel data."""

import json
import logging
import os
import threading
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# In-memory vessel store: MMSI -> vessel data
_vessels = {}
_lock = threading.Lock()
_ws_thread = None
_running = False

# Stale vessel timeout (seconds) — remove vessels not updated in 10 minutes
VESSEL_TTL = 600


def get_vessels(bounds=None):
    """Return current vessel positions.

    Args:
        bounds: optional dict with n, s, e, w (lat/lon bounding box)
    """
    _purge_stale()
    with _lock:
        if bounds:
            return {
                mmsi: v for mmsi, v in _vessels.items()
                if bounds["s"] <= v["lat"] <= bounds["n"]
                and bounds["w"] <= v["lon"] <= bounds["e"]
            }
        return dict(_vessels)


def get_vessel_count():
    """Return number of tracked vessels."""
    with _lock:
        return len(_vessels)


def _purge_stale():
    """Remove vessels not updated recently."""
    cutoff = time.time() - VESSEL_TTL
    with _lock:
        stale = [k for k, v in _vessels.items() if v.get("_ts", 0) < cutoff]
        for k in stale:
            del _vessels[k]


def _update_vessel(mmsi, data):
    """Update or insert vessel record."""
    data["_ts"] = time.time()
    with _lock:
        if mmsi in _vessels:
            _vessels[mmsi].update(data)
        else:
            _vessels[mmsi] = data


def _process_message(msg):
    """Process a single aisstream.io message."""
    msg_type = msg.get("MessageType")
    meta = msg.get("MetaData", {})
    mmsi = str(meta.get("MMSI", ""))
    if not mmsi:
        return

    vessel = {
        "mmsi": mmsi,
        "name": meta.get("ShipName", "").strip(),
        "lat": meta.get("latitude"),
        "lon": meta.get("longitude"),
        "last_update": meta.get("time_utc", ""),
    }

    if msg_type == "PositionReport":
        report = msg.get("Message", {}).get("PositionReport", {})
        vessel.update({
            "cog": report.get("Cog"),
            "sog": report.get("Sog"),
            "heading": report.get("TrueHeading"),
            "nav_status": report.get("NavigationalStatus"),
        })

    elif msg_type == "ShipStaticData":
        static = msg.get("Message", {}).get("ShipStaticData", {})
        vessel.update({
            "ship_type": static.get("Type"),
            "imo": static.get("ImoNumber"),
            "callsign": static.get("CallSign", "").strip(),
            "destination": static.get("Destination", "").strip(),
            "draught": static.get("MaximumStaticDraught"),
        })

    elif msg_type == "StandardClassBPositionReport":
        report = msg.get("Message", {}).get("StandardClassBPositionReport", {})
        vessel.update({
            "cog": report.get("Cog"),
            "sog": report.get("Sog"),
            "heading": report.get("TrueHeading"),
        })

    # Only store if we have a valid position
    if vessel.get("lat") is not None and vessel.get("lon") is not None:
        _update_vessel(mmsi, vessel)


def start_stream(api_key, bounding_boxes=None):
    """Start the AIS WebSocket stream in a background thread.

    Args:
        api_key: aisstream.io API key
        bounding_boxes: list of [[lat_min, lon_min], [lat_max, lon_max]] boxes.
                       Defaults to Western Europe / North Sea area.
    """
    global _ws_thread, _running

    if _running:
        logger.info("AIS stream already running")
        return

    if not api_key:
        logger.warning("No AISSTREAM_API_KEY set — AIS stream disabled")
        return

    if bounding_boxes is None:
        # Default: North Sea + English Channel + Baltic approaches
        bounding_boxes = [
            [[48.0, -5.0], [62.0, 15.0]]
        ]

    _running = True
    _ws_thread = threading.Thread(
        target=_stream_worker,
        args=(api_key, bounding_boxes),
        daemon=True,
        name="ais-stream"
    )
    _ws_thread.start()
    logger.info("AIS stream started (bounding boxes: %s)", bounding_boxes)


def stop_stream():
    """Stop the AIS stream."""
    global _running
    _running = False
    logger.info("AIS stream stop requested")


def _stream_worker(api_key, bounding_boxes):
    """WebSocket worker — reconnects on failure."""
    global _running

    try:
        import websocket
    except ImportError:
        logger.error("websocket-client not installed — pip install websocket-client")
        _running = False
        return

    subscribe_msg = json.dumps({
        "APIKey": api_key,
        "BoundingBoxes": bounding_boxes,
        "FiltersShipMMSI": [],
        "FilterMessageTypes": [
            "PositionReport",
            "ShipStaticData",
            "StandardClassBPositionReport"
        ]
    })

    while _running:
        try:
            logger.info("Connecting to aisstream.io...")
            ws = websocket.WebSocket()
            ws.settimeout(30)
            ws.connect("wss://stream.aisstream.io/v0/stream")
            ws.send(subscribe_msg)
            logger.info("AIS WebSocket connected, subscribed")

            while _running:
                try:
                    raw = ws.recv()
                    if raw:
                        msg = json.loads(raw)
                        _process_message(msg)
                except websocket.WebSocketTimeoutException:
                    continue
                except websocket.WebSocketConnectionClosedException:
                    logger.warning("AIS WebSocket closed, reconnecting...")
                    break
                except json.JSONDecodeError:
                    continue

        except Exception as e:
            logger.error("AIS stream error: %s", e)

        if _running:
            logger.info("AIS reconnecting in 5s...")
            time.sleep(5)

    logger.info("AIS stream stopped")
