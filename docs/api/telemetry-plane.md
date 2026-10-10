# API-SPEC: Telemetry Plane Protocol Specification

---
Document Status: Approved & Locked
Document Version: 1.0.0
NSPEC Compatibility: 1.x
API Compatibility: 1.0.0
Owner: Infrastructure & Realtime Telemetry Engineering Team
Last Updated: 2026-10-10
Normative Standard: RFC 2119 Compliance
---

## Document Rules

This specification is normative and governs the Server-Sent Events (SSE) streaming protocol, hierarchical event taxonomy, heartbeat standards, and connection recovery protocols for the Novelis Telemetry Plane.

In accordance with `NSPEC-000 Article IV`, the client UI (Novelis Studio) MUST act as a purely reactive consumer of these events. Novelis Studio SHALL NOT poll REST endpoints when an active SSE stream is available.

---

## 1. Connection Protocol Standard (SSE)

### 1.1 Endpoint Definition
* **URL:** `GET /api/v1/builds/{id}/telemetry`
* **Transport:** HTTP/1.1 or HTTP/2 Server-Sent Events (`text/event-stream`).
* **Headers:**
  * Request: `Accept: text/event-stream`, `Last-Event-ID: <event_id>` (upon reconnect).
  * Response: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`.

### 1.2 Universal SSE Frame Format
Every event frame transmitted across the wire MUST adhere to the following standard:

```http
id: evt_01h9x88a_00142
event: runtime.state_changed
retry: 3000
data: {"event_schema_version":"1.0.0","timestamp":"2026-10-10T12:06:00Z","correlation_id":"req_01h9x88a","build_id":"bld_01h9x7a2","data":{"current_epoch":15,"state_delta_id":"dlta_8812b","affected_entities":["char_aria","char_kael"]}}

```

---

## 2. Event Taxonomy Standard

All events transmitted over the Telemetry Plane MUST use dot-notated hierarchical namespaces:

```plaintext
┌────────────────────────────────────────────────────────────────────────┐
│                      Telemetry Event Taxonomy                          │
├───────────────┬────────────────────────────────────────────────────────┤
│ Namespace     │ Description & Events                                   │
├───────────────┼────────────────────────────────────────────────────────┤
│ `system.*`    │ Connection lifecycle, health heartbeats, errors.       │
│               │ • system.heartbeat                                     │
│               │ • system.error                                         │
├───────────────┼────────────────────────────────────────────────────────┤
│ `build.*`     │ High-level build lifecycle transitions.                │
│               │ • build.started, build.paused, build.resumed           │
│               │ • build.finished, build.failed, build.cancelled        │
├───────────────┼────────────────────────────────────────────────────────┤
│ `compiler.*`  │ AST parsing and CSIR compilation feedback.             │
│               │ • compiler.compiling, compiler.csir_emitted            │
│               │ • compiler.diagnostic_emitted                          │
├───────────────┼────────────────────────────────────────────────────────┤
│ `runtime.*`   │ VM state transitions, task lifecycles, and epochs.     │
│               │ • runtime.task_started, runtime.task_committed         │
│               │ • runtime.state_changed                                │
├───────────────┼────────────────────────────────────────────────────────┤
│ `renderer.*`  │ Real-time prose generation and token streams.          │
│               │ • renderer.token_stream                                │
│               │ • renderer.scene_completed                             │
├───────────────┼────────────────────────────────────────────────────────┤
│ `rule.*`      │ Rule validation and self-healing telemetry.             │
│               │ • rule.violation_detected                              │
│               │ • rule.healing_attempted                               │
├───────────────┼────────────────────────────────────────────────────────┤
│ `graph.*`     │ Visual story graph updates (RFC 6902 JSON Patches).    │
│               │ • graph.delta                                          │
└───────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Core Event Payload Schemas

### 3.1 Heartbeat Stream (`system.heartbeat`)
Transmitted every 15 seconds to prevent network timeouts and report worker health:
```json
{
  "event": "system.heartbeat",
  "timestamp": "2026-10-10T12:06:15Z",
  "data": {
    "worker_id": "wrk_node_04",
    "worker_status": "HEALTHY",
    "cpu_usage_pct": 24.2,
    "memory_mb_used": 420
  }
}
```

### 3.2 Real-time Prose Token Stream (`renderer.token_stream`)
Enables live typewriter rendering in the author canvas:
```json
{
  "event": "renderer.token_stream",
  "build_id": "bld_01h9x7a2",
  "data": {
    "scene_id": "scn_c01_s01",
    "chunk_index": 48,
    "text": " frost crept along the iron trim of the archway.",
    "words_so_far": 842,
    "target_words": 1800
  }
}
```

### 3.3 Visual Graph Delta (`graph.delta`)
Transmits RFC 6902 JSON Patch arrays to dynamically update the interactive node graph:
```json
{
  "event": "graph.delta",
  "build_id": "bld_01h9x7a2",
  "data": [
    {
      "op": "replace",
      "path": "/nodes/char_kael/trust_score",
      "value": 0.2
    },
    {
      "op": "add",
      "path": "/edges/0",
      "value": {
        "id": "rel_aria_kael",
        "source": "char_aria",
        "target": "char_kael",
        "label": "SUSPICIOUS_ALLY"
      }
    }
  ]
}
```

---

## 4. Connection Resilience & Replay Guarantees

### 4.1 Last-Event-ID Replay Protocol
1. When a client network connection drops, the browser or client automatically reconnects with the HTTP header:
   `Last-Event-ID: evt_01h9x88a_00142`
2. The Telemetry Server maintains an in-memory ring buffer (minimum 1,000 historical events).
3. Upon receiving `Last-Event-ID`, the server immediately replays all missed events in sequence before resuming the live stream.

### 4.2 Fallback Re-synchronization
If the client was disconnected for longer than the buffer window, the server emits a `system.sync_required` event with HTTP status 410 (Gone). The client MUST then call `GET /api/v1/builds/{id}/snapshot` on the Control Plane to re-synchronize full project state before opening a fresh SSE connection.
