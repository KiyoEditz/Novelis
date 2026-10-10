# API-SPEC: Control Plane Protocol Specification

---
Document Status: Approved & Locked
Document Version: 1.0.0
NSPEC Compatibility: 1.x
API Compatibility: 1.0.0
Owner: Infrastructure & Control Plane Engineering Team
Last Updated: 2026-10-10
Normative Standard: RFC 2119 Compliance
---

## Document Rules

This specification is normative and defines the HTTP REST APIs, transactional commands, pagination standards, and error payloads for the Novelis Control Plane.

All endpoints MUST strictly observe universal headers and compatibility guidelines defined in `API-SPEC.md`.

---

## 1. Universal Headers & Conventions

All client requests and server responses MUST include:

| Header Name | Type | Requirement | Description |
| :--- | :--- | :--- | :--- |
| `X-API-Version` | String | REQUIRED | SemVer string, e.g. `1.0.0` |
| `X-Correlation-ID` | String | REQUIRED | Unique trace ID, e.g. `req_01h9x88a` |
| `Idempotency-Key` | String | OPTIONAL | UUIDv4 for POST requests to guarantee safe retries |
| `Authorization` | String | REQUIRED | Bearer token authorization header |

---

## 2. Universal Error Format (RFC 7807 Problem Details)

All non-2xx HTTP responses MUST emit `application/problem+json` payloads:

```json
{
  "type": "https://api.novelis.dev/errors/CANON_PRECONDITION_FAILED",
  "title": "Canon Precondition Failed",
  "status": 409,
  "detail": "Character 'char_kael' is marked DECEASED and cannot be placed in active scene.",
  "instance": "/api/v1/builds/bld_01h9x7a2/scenes/scn_c01_s01",
  "error_code": "E_CANON_PRECONDITION_FAILED",
  "timestamp": "2026-10-10T12:10:00Z"
}
```

---

## 3. Endpoint Suite: Build Lifecycle

### 3.1 Initiate Story Build
* **Method:** `POST /api/v1/builds`
* **Description:** Initiates a novel build from a validated Story Blueprint. Supports `Idempotency-Key`.
* **Request Body:**
```json
{
  "project_id": "proj_solaris_chronicles",
  "blueprint_id": "bp_01h9x7a2",
  "mode": "AUTONOMOUS",
  "target_chapters": [1, 2, 3],
  "engine_options": {
    "renderer_plugin": "novelis-renderer-gemini",
    "enable_self_healing": true
  }
}
```
* **Response (202 Accepted):**
```json
{
  "build_id": "bld_01h9x7a2",
  "status": "PLANNING",
  "created_at": "2026-10-10T12:00:00Z",
  "telemetry_stream_url": "/api/v1/builds/bld_01h9x7a2/telemetry"
}
```

### 3.2 List Builds
* **Method:** `GET /api/v1/builds`
* **Query Parameters:** `cursor` (String), `limit` (Integer, default 20, max 100), `status` (String).
* **Response (200 OK):**
```json
{
  "items": [
    {
      "build_id": "bld_01h9x7a2",
      "project_id": "proj_solaris_chronicles",
      "status": "RUNNING",
      "current_chapter": 1,
      "current_scene": 2,
      "words_generated": 3450,
      "created_at": "2026-10-10T12:00:00Z"
    }
  ],
  "next_cursor": "cur_01h9x99b",
  "has_more": true
}
```

### 3.3 Get Build Status & Summary
* **Method:** `GET /api/v1/builds/{id}`
* **Response (200 OK):**
```json
{
  "build_id": "bld_01h9x7a2",
  "status": "RUNNING",
  "current_epoch": 14,
  "active_task_id": "task_c01_s02",
  "progress_percentage": 18.5,
  "words_generated": 3450,
  "target_words": 85000,
  "errors_count": 0,
  "warnings_count": 1
}
```

### 3.4 Build State Transitions (Pause, Resume, Cancel)
* **`POST /api/v1/builds/{id}/pause`:** Gracefully suspends background workers after current scene commit. Transitions status to `PAUSED`.
* **`POST /api/v1/builds/{id}/resume`:** Restores active build from the latest valid snapshot.
* **`POST /api/v1/builds/{id}/cancel`:** Triggers immediate cancellation token, cancels active LLM calls, and rolls back uncommitted state deltas.

---

## 4. Endpoint Suite: Inspection & Conflict Resolution

### 4.1 State Snapshot & Inspector Sync
* **Method:** `GET /api/v1/builds/{id}/snapshot`
* **Description:** Retrieves atomic project state for client reconnection or state synchronization.
* **Response (200 OK):** Returns composite bundle of Story Graph, Active Timelines, and Character States.

### 4.2 Narrative Explainability API
* **Method:** `GET /api/v1/builds/{id}/explain`
* **Query Parameters:** `entity_id` (String, required), `epoch` (Integer, optional).
* **Description:** Explains causal rationale for a character death, attitude change, or item state by querying the Event Store.
* **Response (200 OK):**
```json
{
  "entity_id": "char_kael",
  "attribute": "trust_score_towards_aria",
  "current_value": 0.2,
  "causal_chain": [
    {
      "epoch": 1,
      "scene_id": "scn_c01_s01",
      "event": "Aria uncovered the Inquisitor seal in the scriptorium",
      "delta": -0.4
    }
  ]
}
```

### 4.3 Conflict Resolution Submission (Interactive Mode)
* **Method:** `POST /api/v1/builds/{id}/conflicts/{conflict_id}/resolve`
* **Request Body:**
```json
{
  "resolution_choice": "OPT_REWRITE_PROSE",
  "author_instruction": "Rewrite the dialogue so Aria remains suspicious without knowing his official title."
}
```
* **Response (200 OK):**
```json
{
  "conflict_id": "cnf_01h9x88a",
  "status": "RESOLVED",
  "action_taken": "SCENE_REGENERATING"
}
```
