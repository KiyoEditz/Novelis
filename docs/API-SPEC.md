# API-SPEC: Dual-Plane Architecture & Data Contracts Master Protocol

---
Document Status: Approved & Locked
Document Version: 1.1.0
NSPEC Compatibility:
minimum: 1.0
maximum: 1.x
API Compatibility:
minimum: 1.0
maximum: 1.x
Owner: Engine & Infrastructure Architecture Team
Contributors: Product Experience Architecture Team
Last Updated: 2026-08-05
Normative Standard: RFC 2119 Compliance
---

## Document Rules

This specification is normative and governs all HTTP REST endpoints, Server-Sent Events (SSE), and JSON Data Plane schemas in the Novelis ecosystem.

All implementations MUST adhere strictly to the modular API documents under `docs/api/`.

Normative terms MUST follow GLOSSARY.md v1.1.0 and NSPEC-000 v1.1.0.

Breaking changes to any endpoint, event payload, or schema contract REQUIRE a major version bump per NSPEC-000 Article VI.

---

## 1. System Architecture & Modular Organization

The Novelis API system decouples communication into three dedicated sub-specifications:

```plaintext
                        ┌────────────────────────┐
                        │      API-SPEC.md       │
                        │ (Master Architecture)  │
                        └───────────┬────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│ control-plane.md │       │telemetry-plane.md│       │  data-plane.md   │
│   (REST APIs)    │       │   (SSE Events)   │       │(JSON Schemas)    │
└──────────────────┘       └──────────────────┘       └──────────────────┘
```

* **control-plane.md:** Governs HTTP REST transactional commands, state controls, pagination, and debugging APIs.
* **telemetry-plane.md:** Governs real-time Server-Sent Events (SSE), heartbeat streams, event taxonomy, and connection recovery.
* **data-plane.md:** Governs universal schema envelopes, artifact payloads, ownership boundaries, and JSON Patch operations.

---

## 2. Universal API Standards & Protocols

### 2.1 Universal Header Standard
All HTTP requests and responses across the Control and Telemetry Planes MUST include the following headers:

| Header Name | Type | Requirement | Description |
| :--- | :--- | :--- | :--- |
| **X-API-Version** | String | REQUIRED | Requested/Returned API SemVer (e.g., 1.0.0). |
| **X-Correlation-ID** | String | REQUIRED | Unique request/telemetry trace ID (e.g., req_01h9x88a). |
| **Idempotency-Key** | String | OPTIONAL | Unique UUID for POST operations to prevent duplicate builds. |
| **Last-Event-ID** | String | OPTIONAL | Used by client on SSE connection reconnect for event replay. |

### 2.2 Contract Stability Policy
Every endpoint, telemetry event, and schema payload in `docs/api/` MUST explicitly declare its stability tier:

* **Stable:** Production-ready. Backward-compatible updates only. Breaking changes require a 6-month deprecation notice.
* **Experimental:** In active development. Subject to changes or removal with minor version bumps.
* **Deprecated:** Marked for removal in the next major version. Migration path MUST be provided.
* **Removed:** Fully retired from the codebase.

### 2.3 Non-Polling & UI Ownership Laws
* **Frontend Never Polls Rule:** The Product Experience Layer (Novelis Studio) MUST NOT poll REST endpoints when an active SSE stream is available. REST polling is strictly restricted to connection fallback modes.
* **UI Never Owns Canon Rule:** Novelis Studio UI acts strictly as a reactive presentation view. The UI SHALL NOT maintain, mutate, or store Canon state locally. The Runtime VM is the single source of truth for Canon.

---

## 3. Modular Specification Outlines

### 3.1 Control Plane Protocol (`docs/api/control-plane.md`)

**Endpoint Lifecycle Suite (Stable):**
* `POST /api/v1/builds` — Initiates build (supports Idempotency-Key).
* `GET /api/v1/builds` — Lists builds with cursor-based pagination (cursor, limit, next_cursor).
* `GET /api/v1/builds/{id}` — Retrieves current build state & summary.
* `POST /api/v1/builds/{id}/pause` — Requests graceful worker pause.
* `POST /api/v1/builds/{id}/resume` — Resumes build from Event Store Snapshot.
* `POST /api/v1/builds/{id}/cancel` — Triggers immediate Cancellation Token & rollback.

**Synchronization & Inspection Suite (Stable):**
* `GET /api/v1/builds/{id}/snapshot` — Fetches combined atomic state (Graph, Timeline, Inspector) upon client reconnect.
* `GET /api/v1/builds/{id}/explain` — Explainability API: Queries causal narrative rationale for character deaths, state changes, or rule violations (`?entity_id=char_vector`).
* `POST /api/v1/builds/{id}/conflicts/{conflict_id}/resolve` — Submits author choice for interactive conflicts.

### 3.2 Telemetry Plane Protocol (`docs/api/telemetry-plane.md`)

**Taxonomy Standard:** All events MUST use hierarchical namespaces: `planner.*`, `compiler.*`, `runtime.*`, `renderer.*`, `graph.*`, `system.*`, `build.*`.

**Universal Event Payload Standard:**

```json
{
  "event": "runtime.state_changed",
  "event_schema_version": "1.0.0",
  "timestamp": "2026-08-05T16:20:00Z",
  "correlation_id": "trace_99182a",
  "build_id": "bld_01h9x7a2",
  "data": {
    "current_epoch": "EPOCH_14",
    "state_delta_id": "dlta_8812b"
  }
}
```

**Heartbeat & Replay Guarantees:**
* Emits `system.heartbeat` every 15 seconds.
* Supports `Last-Event-ID` header to automatically replay missed event streams upon network drop.

### 3.3 Data Plane Protocol (`docs/api/data-plane.md`)

**Artifact Ownership Laws:**
* **Creative Layer / Compiler:** Owns Story Blueprint and Internal Story DSL.
* **Compiler:** Owns CSIR payloads.
* **Runtime VM:** Owns Story State, Canon, and Event Logs.
* **Renderer Layer:** Owns Rendered Prose / Text.

**Universal Metadata Envelope Standard:** 
All artifacts transferred via REST or stored as files MUST adopt the double-envelope pattern:

```json
{
  "metadata": {
    "schema_version": "1.0.0",
    "artifact_type": "CSIR",
    "build_id": "bld_01h9x7a2",
    "correlation_id": "req_01h9x88a",
    "created_at": "2026-08-05T16:20:00Z",
    "checksum": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "payload": {
    "scene_id": "scn_ch01_sc01",
    "story_epoch": "EPOCH_01",
    "scene_spec": {}
  }
}
```

**JSON Patch Operation Standard (`graph.delta`):** 
Incremental Visual Story Graph updates MUST use standard RFC 6902 JSON Patch arrays (add, remove, replace):

```json
{
  "event": "graph.delta",
  "event_schema_version": "1.0.0",
  "data": [
    { "op": "add", "path": "/nodes/char_vector", "value": { "label": "Vector", "status": "ALIVE" } },
    { "op": "add", "path": "/edges/0", "value": { "source": "char_vector", "target": "char_kael", "relation": "ENEMY" } }
  ]
}
```