"""Compliance vault integrity — SHA-256 hashing for tamper detection."""

import hashlib
import json
from typing import Any, Dict, List


def compute_record_hash(table: str, record: dict) -> str:
    """
    Compute SHA-256 hash of a record for tamper detection.

    Hash includes:
    - table name
    - all record fields EXCEPT 'id', 'record_hash', 'created_at'

    This allows detecting if any compliance-critical field was modified.
    """
    # Exclude internal fields
    excluded = {'id', 'record_hash', 'created_at'}
    payload = {k: v for k, v in record.items() if k not in excluded}

    # Canonical JSON for consistent hashing
    canonical = json.dumps(
        {"table": table, "record": payload},
        sort_keys=True,
        default=str  # Handle datetime, None, etc.
    )

    return hashlib.sha256(canonical.encode()).hexdigest()


def verify_export_integrity(records: List[Dict[str, Any]], table: str) -> Dict[str, Any]:
    """
    Verify integrity of exported records by re-computing hashes.

    Returns:
        {
            "valid": bool,           # all hashes matched
            "failures": [id, ...],   # records with hash mismatches
            "count": int,            # total records verified
            "integrity_timestamp": str
        }
    """
    from datetime import datetime

    failures = []
    for record in records:
        expected = compute_record_hash(table, dict(record))
        actual = record.get('record_hash')

        if actual != expected:
            failures.append({
                "id": record.get('id'),
                "expected_hash": expected,
                "actual_hash": actual
            })

    return {
        "valid": len(failures) == 0,
        "failures": failures,
        "count": len(records),
        "integrity_timestamp": datetime.utcnow().isoformat() + "Z"
    }


def chain_hash_export(records: List[Dict[str, Any]]) -> str:
    """
    Compute a chain hash across all exported records.

    Allows detecting if records were added/removed from an export.
    """
    hashes = [record.get('record_hash', '') for record in records]
    chain = json.dumps(hashes)
    return hashlib.sha256(chain.encode()).hexdigest()
