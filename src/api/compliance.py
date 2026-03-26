"""Compliance vault API — read-only endpoints for regulatory audit trails."""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import uuid

from src.data.vault_models import get_vault_db
from src.core.vault_integrity import compute_record_hash, verify_export_integrity, chain_hash_export

compliance_bp = Blueprint("compliance", __name__, url_prefix="/api/compliance")


# ════════════════════════════════════════════════════════
# AUDIT LOG
# ════════════════════════════════════════════════════════

def log_audit_event(event: str, table_name: str = None, record_id: int = None, endpoint: str = None, ip: str = None, details: str = None):
    """Log access/export events to audit trail."""
    vault_db = get_vault_db()
    vault_db.execute(
        """INSERT INTO audit_log (event, table_name, record_id, endpoint, ip, details)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (event, table_name, record_id, endpoint, ip, details)
    )
    vault_db.commit()


# ════════════════════════════════════════════════════════
# MLC 2006 REST HOURS
# ════════════════════════════════════════════════════════

@compliance_bp.route('/rest-hours', methods=['GET'])
def get_rest_hours():
    """Retrieve MLC 2006 rest/work period records with integrity verification."""
    start = request.args.get('start')  # ISO date
    end = request.args.get('end')
    fmt = request.args.get('format', 'json')  # json | csv

    vault_db = get_vault_db()

    query = "SELECT * FROM rest_hours"
    params = []

    if start:
        query += " AND date >= ?"
        params.append(start)
    if end:
        query += " AND date <= ?"
        params.append(end)

    query += " ORDER BY date ASC"

    rows = vault_db.execute(query if not start and not end else query.replace("SELECT * FROM rest_hours AND", "SELECT * FROM rest_hours WHERE"), params).fetchall()

    # Fix query construction
    if start or end:
        query = "SELECT * FROM rest_hours WHERE"
        conditions = []
        if start:
            conditions.append("date >= ?")
        if end:
            conditions.append("date <= ?")
        query += " AND ".join(conditions)
        query += " ORDER BY date ASC"
        rows = vault_db.execute(query, params).fetchall()
    else:
        rows = vault_db.execute("SELECT * FROM rest_hours ORDER BY date ASC").fetchall()

    records = [dict(row) for row in rows]

    # Verify integrity
    integrity = verify_export_integrity(records, 'rest_hours')

    # Log access
    log_audit_event('READ', 'rest_hours', endpoint=request.path, ip=request.remote_addr)

    if fmt == 'csv':
        return csv_response_mlc_rest_hours(records), 200, {'Content-Type': 'text/csv'}

    return jsonify({
        'count': len(records),
        'integrity': integrity,
        'data': records
    })


@compliance_bp.route('/rest-hours/compliance-report', methods=['GET'])
def mlc_compliance_report():
    """MLC 2006 compliance check: rolling 24h and 7-day rest totals."""
    period = request.args.get('period', '7d')  # 24h | 7d | 30d

    vault_db = get_vault_db()

    # Determine lookback period
    if period == '24h':
        lookback = 1
    elif period == '7d':
        lookback = 7
    else:  # 30d
        lookback = 30

    # Get rest hours in last N days
    rows = vault_db.execute(
        """SELECT SUM(CAST((julianday(end_time) - julianday(start_time)) * 24 AS INTEGER)) as total_rest_hours
           FROM rest_hours
           WHERE date >= date('now', '-' || ? || ' days')
           AND type IN ('rest', 'standby')""",
        (lookback,)
    ).fetchone()

    total_rest_hours = rows['total_rest_hours'] or 0

    # MLC minimums: 10h/24h, 77h/7d
    min_hours = 10 if lookback == 1 else 77 if lookback == 7 else 77  # 30d uses 7d standard

    status = 'green' if total_rest_hours >= min_hours else 'amber' if total_rest_hours >= (min_hours * 0.9) else 'red'

    log_audit_event('READ', 'rest_hours', endpoint=request.path, ip=request.remote_addr)

    return jsonify({
        'period': period,
        'lookback_days': lookback,
        'minimum_required_hours': min_hours,
        'actual_rest_hours': total_rest_hours,
        'status': status,
        'compliance': total_rest_hours >= min_hours,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


def csv_response_mlc_rest_hours(records):
    """Format rest hours as MLC standardized CSV."""
    lines = [
        'Date,Start Work,End Work,Hours Work,Start Rest,End Rest,Hours Rest,24h Total Rest,7d Total Rest,Status,Notes'
    ]

    for record in records:
        lines.append(
            f"{record['date']},{record['start_time']},{record['end_time']},"
            f",,,,,,{record['type']},{record['notes'] or ''}"
        )

    return '\n'.join(lines)


# ════════════════════════════════════════════════════════
# DRILLS (SOLAS / ISM)
# ════════════════════════════════════════════════════════

@compliance_bp.route('/drills', methods=['GET'])
def get_drills():
    """Retrieve SOLAS drill records."""
    drill_type = request.args.get('type')
    start = request.args.get('start')
    end = request.args.get('end')

    vault_db = get_vault_db()

    query = "SELECT * FROM drills WHERE 1=1"
    params = []

    if drill_type:
        query += " AND type = ?"
        params.append(drill_type)
    if start:
        query += " AND conducted_at >= ?"
        params.append(start)
    if end:
        query += " AND conducted_at <= ?"
        params.append(end)

    query += " ORDER BY conducted_at DESC"

    rows = vault_db.execute(query, params).fetchall()
    records = [dict(row) for row in rows]

    integrity = verify_export_integrity(records, 'drills')
    log_audit_event('READ', 'drills', endpoint=request.path, ip=request.remote_addr)

    return jsonify({
        'count': len(records),
        'integrity': integrity,
        'data': records
    })


# ════════════════════════════════════════════════════════
# CERTIFICATES (STCW)
# ════════════════════════════════════════════════════════

@compliance_bp.route('/certificates', methods=['GET'])
def get_certificates():
    """Retrieve seafarer/ROC operator certificates with expiry tracking."""
    expiring_before = request.args.get('expiring_before')

    vault_db = get_vault_db()

    query = "SELECT * FROM certificates WHERE 1=1"
    params = []

    if expiring_before:
        query += " AND expiry_date <= ?"
        params.append(expiring_before)

    query += " ORDER BY expiry_date ASC"

    rows = vault_db.execute(query, params).fetchall()
    records = [dict(row) for row in rows]

    integrity = verify_export_integrity(records, 'certificates')
    log_audit_event('READ', 'certificates', endpoint=request.path, ip=request.remote_addr)

    return jsonify({
        'count': len(records),
        'integrity': integrity,
        'data': records
    })


# ════════════════════════════════════════════════════════
# OPERATIONAL LOGS (Watch, Voyage)
# ════════════════════════════════════════════════════════

@compliance_bp.route('/watch-log', methods=['GET'])
def get_watch_log():
    """Retrieve OOW watch records."""
    start = request.args.get('start')
    end = request.args.get('end')

    vault_db = get_vault_db()

    query = "SELECT * FROM watch_log WHERE 1=1"
    params = []

    if start:
        query += " AND date >= ?"
        params.append(start)
    if end:
        query += " AND date <= ?"
        params.append(end)

    query += " ORDER BY date DESC"

    rows = vault_db.execute(query, params).fetchall()
    records = [dict(row) for row in rows]

    integrity = verify_export_integrity(records, 'watch_log')
    log_audit_event('READ', 'watch_log', endpoint=request.path, ip=request.remote_addr)

    return jsonify({
        'count': len(records),
        'integrity': integrity,
        'data': records
    })


@compliance_bp.route('/voyage-log', methods=['GET'])
def get_voyage_log():
    """Retrieve voyage event records."""
    start = request.args.get('start')
    end = request.args.get('end')

    vault_db = get_vault_db()

    query = "SELECT * FROM voyage_log WHERE 1=1"
    params = []

    if start:
        query += " AND timestamp >= ?"
        params.append(start)
    if end:
        query += " AND timestamp <= ?"
        params.append(end)

    query += " ORDER BY timestamp DESC"

    rows = vault_db.execute(query, params).fetchall()
    records = [dict(row) for row in rows]

    integrity = verify_export_integrity(records, 'voyage_log')
    log_audit_event('READ', 'voyage_log', endpoint=request.path, ip=request.remote_addr)

    return jsonify({
        'count': len(records),
        'integrity': integrity,
        'data': records
    })


# ════════════════════════════════════════════════════════
# ROC — REMOTE OPERATIONS CENTRE (MASS Code)
# ════════════════════════════════════════════════════════

@compliance_bp.route('/roc/sessions', methods=['GET', 'POST'])
def roc_sessions():
    """Get ROC sessions or start a new session."""
    if request.method == 'GET':
        start = request.args.get('start')
        end = request.args.get('end')

        vault_db = get_vault_db()

        query = "SELECT * FROM roc_sessions WHERE 1=1"
        params = []

        if start:
            query += " AND login_at >= ?"
            params.append(start)
        if end:
            query += " AND login_at <= ?"
            params.append(end)

        query += " ORDER BY login_at DESC"

        rows = vault_db.execute(query, params).fetchall()
        records = [dict(row) for row in rows]

        integrity = verify_export_integrity(records, 'roc_sessions')
        log_audit_event('READ', 'roc_sessions', endpoint=request.path, ip=request.remote_addr)

        return jsonify({
            'count': len(records),
            'integrity': integrity,
            'data': records
        })

    # POST — create new session
    data = request.get_json() or {}
    required = ['operator_id', 'vessel_id', 'mode']

    if not all(k in data for k in required):
        return jsonify({'error': f'missing required fields: {required}'}), 400

    vault_db = get_vault_db()
    session_id = str(uuid.uuid4())

    vault_db.execute(
        """INSERT INTO roc_sessions (session_id, operator_id, vessel_id, mode, handover_from, vessel_state_snapshot)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (session_id, data['operator_id'], data['vessel_id'], data['mode'],
         data.get('handover_from'), data.get('vessel_state_snapshot'))
    )
    vault_db.commit()

    log_audit_event('WRITE', 'roc_sessions', details=session_id, endpoint=request.path, ip=request.remote_addr)

    return jsonify({'session_id': session_id, 'created_at': datetime.utcnow().isoformat() + 'Z'}), 201


@compliance_bp.route('/roc/sessions/<int:session_id>/close', methods=['PATCH'])
def close_roc_session(session_id):
    """Close an active ROC session (only allowed mutation)."""
    vault_db = get_vault_db()

    row = vault_db.execute("SELECT * FROM roc_sessions WHERE id = ?", (session_id,)).fetchone()
    if not row:
        return jsonify({'error': 'session not found'}), 404

    if row['logout_at']:
        return jsonify({'error': 'session already closed'}), 400

    vault_db.execute(
        "UPDATE roc_sessions SET logout_at = datetime('now') WHERE id = ?",
        (session_id,)
    )
    vault_db.commit()

    log_audit_event('UPDATE', 'roc_sessions', record_id=session_id, endpoint=request.path, ip=request.remote_addr)

    return jsonify({'session_id': row['session_id'], 'closed_at': datetime.utcnow().isoformat() + 'Z'}), 200


@compliance_bp.route('/roc/interventions', methods=['GET', 'POST'])
def roc_interventions():
    """Get ROC interventions or log a new intervention."""
    if request.method == 'GET':
        session_id = request.args.get('session_id')
        start = request.args.get('start')
        end = request.args.get('end')

        vault_db = get_vault_db()

        query = "SELECT * FROM roc_interventions WHERE 1=1"
        params = []

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        if start:
            query += " AND ts >= ?"
            params.append(start)
        if end:
            query += " AND ts <= ?"
            params.append(end)

        query += " ORDER BY ts DESC"

        rows = vault_db.execute(query, params).fetchall()
        records = [dict(row) for row in rows]

        integrity = verify_export_integrity(records, 'roc_interventions')
        log_audit_event('READ', 'roc_interventions', endpoint=request.path, ip=request.remote_addr)

        return jsonify({
            'count': len(records),
            'integrity': integrity,
            'data': records
        })

    # POST — log intervention
    data = request.get_json() or {}
    required = ['session_id', 'vessel_id', 'intervention_type']

    if not all(k in data for k in required):
        return jsonify({'error': f'missing required fields: {required}'}), 400

    vault_db = get_vault_db()

    record_hash = compute_record_hash('roc_interventions', data)

    vault_db.execute(
        """INSERT INTO roc_interventions (session_id, vessel_id, intervention_type, reason, details, outcome, record_hash)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (data['session_id'], data['vessel_id'], data['intervention_type'],
         data.get('reason'), data.get('details'), data.get('outcome'), record_hash)
    )
    vault_db.commit()

    log_audit_event('WRITE', 'roc_interventions', details=data['intervention_type'], endpoint=request.path, ip=request.remote_addr)

    return jsonify({'created': True, 'timestamp': datetime.utcnow().isoformat() + 'Z'}), 201


# ════════════════════════════════════════════════════════
# AUTONOMY EVENTS (MASS autonomous mode transitions)
# ════════════════════════════════════════════════════════

@compliance_bp.route('/autonomy/events', methods=['GET', 'POST'])
def autonomy_events():
    """Get autonomy mode transitions or log a new event."""
    if request.method == 'GET':
        start = request.args.get('start')
        end = request.args.get('end')

        vault_db = get_vault_db()

        query = "SELECT * FROM autonomy_events WHERE 1=1"
        params = []

        if start:
            query += " AND ts >= ?"
            params.append(start)
        if end:
            query += " AND ts <= ?"
            params.append(end)

        query += " ORDER BY ts DESC"

        rows = vault_db.execute(query, params).fetchall()
        records = [dict(row) for row in rows]

        integrity = verify_export_integrity(records, 'autonomy_events')
        log_audit_event('READ', 'autonomy_events', endpoint=request.path, ip=request.remote_addr)

        return jsonify({
            'count': len(records),
            'integrity': integrity,
            'data': records
        })

    # POST — log autonomy event
    data = request.get_json() or {}
    required = ['vessel_id', 'to_mode']

    if not all(k in data for k in required):
        return jsonify({'error': f'missing required fields: {required}'}), 400

    vault_db = get_vault_db()

    record_hash = compute_record_hash('autonomy_events', data)

    vault_db.execute(
        """INSERT INTO autonomy_events (vessel_id, from_mode, to_mode, trigger_event, triggered_by, position_lat, position_lon, notes, record_hash)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (data['vessel_id'], data.get('from_mode'), data['to_mode'],
         data.get('trigger_event'), data.get('triggered_by'),
         data.get('position_lat'), data.get('position_lon'),
         data.get('notes'), record_hash)
    )
    vault_db.commit()

    log_audit_event('WRITE', 'autonomy_events', details=f"{data.get('from_mode')}->{data['to_mode']}", endpoint=request.path, ip=request.remote_addr)

    return jsonify({'created': True, 'timestamp': datetime.utcnow().isoformat() + 'Z'}), 201


# ════════════════════════════════════════════════════════
# HEALTH / INFO
# ════════════════════════════════════════════════════════

@compliance_bp.route('/health', methods=['GET'])
def vault_health():
    """Vault health and metadata."""
    vault_db = get_vault_db()

    # Count records in each table
    counts = {}
    for table in ['rest_hours', 'drills', 'certificates', 'watch_log', 'voyage_log', 'roc_sessions', 'roc_interventions', 'autonomy_events', 'non_conformities', 'cyber_events', 'audit_log']:
        row = vault_db.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
        counts[table] = row['count']

    return jsonify({
        'status': 'ok',
        'vault_path': 'data/compliance_vault.db',
        'record_counts': counts,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })
