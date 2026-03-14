#!/bin/bash
# Verify all SeaForge API endpoints are responding
BASE="http://localhost:5000"
PASS=0
FAIL=0

check() {
    local url="$1"
    local name="$2"
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    if [ "$status" = "200" ]; then
        echo "  OK  $name ($url)"
        PASS=$((PASS + 1))
    else
        echo "  FAIL $name ($url) → HTTP $status"
        FAIL=$((FAIL + 1))
    fi
}

echo "SeaForge Endpoint Verification"
echo "=============================="

check "$BASE/api/health" "Health"
check "$BASE/api/ais/status" "AIS Status"
check "$BASE/api/fleet" "Fleet DB"
check "$BASE/api/lights" "Lights DB"
check "$BASE/api/mob/status" "MOB Status"
check "$BASE/api/mob/procedure" "MOB Procedure"
check "$BASE/" "Web UI"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
