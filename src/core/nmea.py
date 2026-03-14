"""NMEA 0183 / Signal K / serial AIS data sources.

Provides multiple ways to get AIS data beyond aisstream.io:
1. Serial port (USB AIS receiver / pilot plug via RS422 adapter)
2. TCP/UDP network stream (WiFi AIS receivers, shipboard NMEA network)
3. Signal K server (standardized marine data)

All sources feed into the same vessel store used by ais.py.
"""

import json
import logging
import socket
import threading
import time

logger = logging.getLogger(__name__)

_sources = {}  # name -> thread
_running = {}  # name -> bool


def decode_ais_sentence(sentence):
    """Decode NMEA AIS sentence (!AIVDM/!AIVDO) to position dict.

    Uses pyais if available, falls back to basic parsing.
    Returns dict with mmsi, lat, lon, cog, sog, name or None.
    """
    sentence = sentence.strip()
    if not sentence.startswith(("!AIVDM", "!AIVDO")):
        return None

    try:
        from pyais import decode as pyais_decode
        msgs = pyais_decode(sentence)
        for msg in msgs:
            d = msg.asdict()
            result = {"mmsi": str(d.get("mmsi", ""))}
            if d.get("lon") is not None and d.get("lat") is not None:
                # pyais returns lon/lat in degrees * 10000 for some types
                result["lon"] = d["lon"]
                result["lat"] = d["lat"]
            if d.get("course") is not None:
                result["cog"] = d["course"]
            if d.get("speed") is not None:
                result["sog"] = d["speed"]
            if d.get("shipname"):
                result["name"] = d["shipname"].strip()
            if d.get("heading") is not None:
                result["heading"] = d["heading"]
            if result.get("mmsi"):
                return result
    except ImportError:
        logger.debug("pyais not installed — raw NMEA sentences not decoded")
    except Exception as e:
        logger.debug("NMEA decode error: %s", e)

    return None


def _feed_vessel(data):
    """Feed decoded vessel data into the AIS vessel store."""
    from .ais import _update_vessel
    mmsi = data.get("mmsi")
    if mmsi and data.get("lat") is not None and data.get("lon") is not None:
        _update_vessel(mmsi, data)


def start_tcp_source(name, host, port):
    """Connect to a TCP NMEA stream (e.g. WiFi AIS receiver, shipboard network).

    Common setups:
    - Quark-elec QK-A027: 192.168.1.1:2000
    - dAISy HAT: raspberrypi.local:10110
    - Ship's NMEA distribution: varies by installation
    """
    if name in _running and _running[name]:
        logger.info("Source '%s' already running", name)
        return

    _running[name] = True
    t = threading.Thread(target=_tcp_worker, args=(name, host, port), daemon=True)
    _sources[name] = t
    t.start()
    logger.info("NMEA TCP source '%s' started → %s:%d", name, host, port)


def start_udp_source(name, port, bind_addr="0.0.0.0"):
    """Listen for UDP NMEA broadcasts (common for shipboard networks)."""
    if name in _running and _running[name]:
        return

    _running[name] = True
    t = threading.Thread(target=_udp_worker, args=(name, port, bind_addr), daemon=True)
    _sources[name] = t
    t.start()
    logger.info("NMEA UDP source '%s' started → %s:%d", name, bind_addr, port)


def start_signalk_source(name, host="localhost", port=3000):
    """Connect to a Signal K server's WebSocket stream.

    Signal K is the open marine data standard. If a Signal K server is
    connected to the vessel's NMEA network, it provides clean JSON data
    for all AIS targets, GPS, wind, depth, etc.

    Default port 3000 is the Signal K standard.
    """
    if name in _running and _running[name]:
        return

    _running[name] = True
    t = threading.Thread(target=_signalk_worker, args=(name, host, port), daemon=True)
    _sources[name] = t
    t.start()
    logger.info("Signal K source '%s' started → %s:%d", name, host, port)


def stop_source(name):
    """Stop a named data source."""
    _running[name] = False
    logger.info("Source '%s' stop requested", name)


def get_source_status():
    """Return status of all configured data sources."""
    return {name: {"running": _running.get(name, False)} for name in _sources}


def _tcp_worker(name, host, port):
    """TCP NMEA stream reader with auto-reconnect."""
    while _running.get(name):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            logger.info("TCP connected to %s:%d", host, port)
            buf = ""
            while _running.get(name):
                try:
                    data = sock.recv(4096).decode("ascii", errors="ignore")
                    if not data:
                        break
                    buf += data
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        vessel = decode_ais_sentence(line)
                        if vessel:
                            _feed_vessel(vessel)
                except socket.timeout:
                    continue
            sock.close()
        except Exception as e:
            logger.error("TCP source '%s' error: %s", name, e)
        if _running.get(name):
            time.sleep(5)


def _udp_worker(name, port, bind_addr):
    """UDP NMEA listener."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        sock.bind((bind_addr, port))
        logger.info("UDP listening on %s:%d", bind_addr, port)
        while _running.get(name):
            try:
                data, _ = sock.recvfrom(4096)
                for line in data.decode("ascii", errors="ignore").split("\n"):
                    vessel = decode_ais_sentence(line)
                    if vessel:
                        _feed_vessel(vessel)
            except socket.timeout:
                continue
        sock.close()
    except Exception as e:
        logger.error("UDP source '%s' error: %s", name, e)


def _signalk_worker(name, host, port):
    """Signal K WebSocket stream reader."""
    try:
        import websocket
    except ImportError:
        logger.error("websocket-client not installed for Signal K")
        _running[name] = False
        return

    url = f"ws://{host}:{port}/signalk/v1/stream?subscribe=all"

    while _running.get(name):
        try:
            ws = websocket.WebSocket()
            ws.settimeout(10)
            ws.connect(url)
            logger.info("Signal K connected to %s:%d", host, port)

            while _running.get(name):
                try:
                    raw = ws.recv()
                    if not raw:
                        continue
                    msg = json.loads(raw)
                    _process_signalk_delta(msg)
                except websocket.WebSocketTimeoutException:
                    continue
                except websocket.WebSocketConnectionClosedException:
                    break

            ws.close()
        except Exception as e:
            logger.error("Signal K source '%s' error: %s", name, e)
        if _running.get(name):
            time.sleep(5)


def _process_signalk_delta(msg):
    """Process Signal K delta message for AIS vessel data."""
    context = msg.get("context", "")
    updates = msg.get("updates", [])

    # Only process AIS vessel contexts: "vessels.urn:mrn:imo:mmsi:XXXXXXXXX"
    if not context.startswith("vessels."):
        return

    # Extract MMSI from context
    parts = context.split(":")
    mmsi = parts[-1] if parts else ""
    if not mmsi.isdigit():
        return

    vessel = {"mmsi": mmsi}

    for update in updates:
        for val in update.get("values", []):
            path = val.get("path", "")
            value = val.get("value")
            if value is None:
                continue

            if path == "navigation.position":
                vessel["lat"] = value.get("latitude")
                vessel["lon"] = value.get("longitude")
            elif path == "navigation.courseOverGroundTrue":
                vessel["cog"] = value * 180 / 3.14159  # radians to degrees
            elif path == "navigation.speedOverGround":
                vessel["sog"] = value * 1.94384  # m/s to knots
            elif path == "navigation.headingTrue":
                vessel["heading"] = value * 180 / 3.14159
            elif path == "name":
                vessel["name"] = value

    if vessel.get("lat") is not None and vessel.get("lon") is not None:
        _feed_vessel(vessel)
