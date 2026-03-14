---
name: deploy
description: "Build, deploy, and verify SeaForge Docker container"
---

# Deploy SeaForge

## Instructions

1. Check for uncommitted changes: `git status`
2. If changes exist, ask user whether to commit first
3. Build and restart the container:
   ```bash
   cd ~/projects/seaforge && docker compose up --build -d
   ```
4. Wait 3 seconds, then run the health check:
   ```bash
   curl -s http://localhost:5000/api/health | python3 -m json.tool
   ```
5. Run scripts/verify.sh to validate all endpoints
6. Report: container status, AIS vessel count, any errors from `docker logs seaforge --tail 10`

## Tools
- scripts/verify.sh — validates all API endpoints return 200
