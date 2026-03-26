# SeaForge API Reference

Base URL: `http://localhost:5000`

---

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | App status, AIS stream state, vessel count |

---

## Navigation

### COLREGS Analysis

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/colregs` | Classify encounter between own ship and target |

**Body:**
```json
{
  "own": {"lat": 51.0, "lon": 1.0, "cog": 0, "sog": 10},
  "target": {"lat": 51.1, "lon": 1.0, "cog": 180, "sog": 10}
}
```
**Response:** `{bearing, range_nm, relative_bearing, situation, role, rule, action, cpa_nm, tcpa_min}`

### Fleet

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/fleet` | All fleets (optionally filter by `?company=`) |
| GET | `/api/fleet/<company>` | Vessels for a specific company |

### Lights (COLREGS Training Scenarios)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/lights` | Get scenarios. Params: `?category=`, `?difficulty=1-3`, `?random=N` |

### AIS

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/ais/vessels` | Tracked vessels. Params: `?n=&s=&e=&w=` (bounding box) |
| GET | `/api/ais/status` | Stream status, vessel count, data sources |
| POST | `/api/ais/sources` | Add data source: `{type: "tcp"|"udp"|"signalk", name, host, port}` |

### Man Overboard (MOB)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/mob/trigger` | Trigger MOB alarm: `{lat, lon, cog, sog, wind_dir?, wind_speed?}` |
| GET | `/api/mob/status` | Current MOB event with updated datum position |
| POST | `/api/mob/search-pattern` | Generate search pattern: `{pattern, radius_nm?, spacing_nm?}` |
| POST | `/api/mob/cancel` | Cancel active MOB event |
| GET | `/api/mob/procedure` | Full GMDSS MOB procedure checklist |

---

## Wellbeing (`/api/wellbeing`)

### Rest Hours (MLC 2006)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/wellbeing/rest-hours` | Get rest periods. Params: `?start=&end=` (YYYY-MM-DD, default last 7d) |
| POST | `/api/wellbeing/rest-hours` | Log rest/work period: `{date, start_time, end_time, type?, notes?}` |
| GET | `/api/wellbeing/rest-hours/compliance` | MLC compliance check (10h/24h, 77h/7d) |

### Workouts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/wellbeing/workouts` | Get workouts. Params: `?date=` (default today) |
| POST | `/api/wellbeing/workouts` | Log workout: `{date, type, exercise, duration_min?, sets?, reps?, weight_kg?, notes?}` |

### Meals

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/wellbeing/meals` | Get meals. Params: `?date=` (default today) |
| POST | `/api/wellbeing/meals` | Log meal: `{date, meal_type, description, calories?, protein_g?, is_galley?, rating?, notes?}` |

### Mood & Energy

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/wellbeing/mood` | Get mood logs. Params: `?days=7` |
| POST | `/api/wellbeing/mood` | Log mood: `{date, energy, mood, time?, sleep_quality?, notes?}` |

---

## Training (`/api/training`)

### COLREGS Scores

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/training/colregs-scores` | Last 50 scores |
| POST | `/api/training/colregs-scores` | Add score: `{date, category, total_questions, correct, time_seconds?}` |

### CTRB Tasks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/training/ctrb` | Get tasks. Params: `?section=`, `?status=` |
| PATCH | `/api/training/ctrb/<task_id>` | Update task: `{status?, evidence?, completed_date?, signed_off_by?}` |

### Drills

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/training/drills` | Get drills. Params: `?status=` (default last 50) |
| POST | `/api/training/drills` | Add drill: `{date, type, title, scenario?, participants?, duration_min?, lessons_learned?, next_drill_due?, status?}` |
| PATCH | `/api/training/drills/<id>` | Update drill: `{status?, lessons_learned?, duration_min?, participants?}` |

### Certificates

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/training/certificates` | All certificates, ordered by expiry |
| POST | `/api/training/certificates` | Add certificate: `{name, issuer?, issue_date?, expiry_date?, certificate_number?, notes?}` |

---

## Operations (`/api/ops`)

### Tasks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/ops/tasks` | Get tasks. Params: `?status=`, `?date=` (sorted by priority) |
| POST | `/api/ops/tasks` | Add task: `{title, date?, description?, category?, priority?, status?, due_date?}` |
| PATCH | `/api/ops/tasks/<id>` | Update task: `{status?, title?, description?, priority?, due_date?}` |
| DELETE | `/api/ops/tasks/<id>` | Delete task |

### Watch Log

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/ops/watch-log` | Get entries. Params: `?limit=20` |
| POST | `/api/ops/watch-log` | Add entry: `{date, watch_start, watch_end, position_lat?, position_lon?, course?, speed?, weather?, wind_direction?, wind_force?, sea_state?, visibility_nm?, events?, handover_notes?}` |

### Voyage Log

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/ops/voyage-log` | Get entries. Params: `?limit=50` |
| POST | `/api/ops/voyage-log` | Add entry: `{timestamp, event_type, port?, position_lat?, position_lon?, course?, speed?, fuel_rob?, distance_run?, notes?}` |

### Data Export

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/ops/export/<table>` | Export table as JSON. Allowed: `rest_hours`, `workouts`, `meals`, `mood_logs`, `tasks`, `watch_log`, `voyage_log`, `drills`, `certificates`, `ctrb_tasks`, `colregs_scores` |
