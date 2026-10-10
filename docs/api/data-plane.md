# API-SPEC: Data Plane Protocol & Schema Contracts

---
Document Status: Approved & Locked
Document Version: 1.0.0
NSPEC Compatibility: 1.x
API Compatibility: 1.0.0
Owner: Data Architecture & Infrastructure Teams
Last Updated: 2026-10-10
Normative Standard: RFC 2119 Compliance
---

## Document Rules

This specification is normative and governs the universal metadata envelope patterns, artifact ownership boundaries, cryptographic integrity checks, and JSON Patch serialization standards for the Novelis Data Plane.

All artifacts persisted to disk or transmitted over REST and Telemetry streams MUST conform strictly to this specification.

---

## 1. Universal Double-Envelope Pattern

Every JSON artifact across the Novelis ecosystem MUST adopt the double-envelope structure, cleanly segregating administrative and provenance metadata from domain payloads:

```json
{
  "metadata": {
    "schema_version": "1.0.0",
    "artifact_type": "CSIR",
    "build_id": "bld_01h9x7a2",
    "correlation_id": "req_01h9x88a",
    "created_at": "2026-10-10T12:00:00Z",
    "checksum": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "payload": {
    "...": "Domain-specific payload body"
  }
}
```

### 1.1 Mandatory Metadata Fields
* `schema_version` (String, SemVer): Target schema specification version.
* `artifact_type` (Enum): One of `STORY_BLUEPRINT`, `CSIR`, `STATE_DELTA`, `CANON_SNAPSHOT`, `RENDERED_PROSE`, or `STORY_GRAPH`.
* `build_id` (String): Unique identifier of the execution session.
* `correlation_id` (String): End-to-end telemetry tracing ID.
* `created_at` (String, ISO 8601 UTC): Creation timestamp.
* `checksum` (String): Cryptographic SHA-256 hash computed over the canonicalized JSON string of the `payload` object.

---

## 2. Artifact Ownership & Mutation Laws

To preserve architectural isolation (NSPEC-000 Article II), write permissions across artifact types are strictly segregated:

```plaintext
┌──────────────────────────────┬─────────────────────────────┬──────────────────────────┐
│ Artifact Type                │ Authoritative Producer      │ Consumer Layers          │
├──────────────────────────────┼─────────────────────────────┼──────────────────────────┤
│ `STORY_BLUEPRINT`            │ Creative Planning Layer     │ Compiler Layer, Studio   │
│ `INTERNAL_STORY_DSL`         │ Creative Planning Layer     │ Compiler Layer, Author   │
│ `CSIR`                       │ Narrative Compiler          │ Runtime VM, Rule Engine  │
│ `STATE_DELTA`                │ Runtime VM                  │ Event Store, Story Bible │
│ `CANON_SNAPSHOT`             │ Runtime VM                  │ Studio UI, Evaluator LLM │
│ `RENDERED_PROSE`             │ Renderer Layer              │ Studio UI, Rule Engine   │
└──────────────────────────────┴─────────────────────────────┴──────────────────────────┘
```

* **Rule:** A component positioned lower in the stack SHALL NOT mutate or overwrite an artifact owned by a layer above it. For example, the Renderer Layer SHALL NOT alter a CSIR payload.

---

## 3. RFC 6902 JSON Patch Standard for State Mutations

All incremental updates to story state, character sheets, and visual graphs MUST use standard RFC 6902 JSON Patch arrays:

```json
[
  {
    "op": "replace",
    "path": "/characters/char_kael/relations/char_aria/trust",
    "value": 0.2
  },
  {
    "op": "add",
    "path": "/characters/char_aria/inventory/-",
    "value": { "item_id": "item_charred_ledger", "acquired_epoch": 1 }
  },
  {
    "op": "remove",
    "path": "/active_events/evt_scriptorium_fire"
  }
]
```

### 3.1 Supported Operations
* `add`: Inserts a new attribute, list element, or map key.
* `remove`: Removes an attribute or element.
* `replace`: Overwrites an existing attribute value.

---

## 4. Cryptographic Integrity & Checksum Algorithm

To detect data corruption and verify artifact immutability across build stages:

### 4.1 Checksum Calculation Standard
1. Extract the `payload` JSON object.
2. Canonicalize the payload via RFC 8785 (JSON Canonicalization Scheme - JCS) to eliminate whitespace and key ordering discrepancies.
3. Compute the SHA-256 hash over the UTF-8 encoded canonical bytes.
4. Format as lowercase hex string prefixed with `sha256:`.

```python
import hashlib
import json

def compute_payload_checksum(payload: dict) -> str:
    # RFC 8785 canonical JSON formatting
    canonical_bytes = json.dumps(
        payload,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False
    ).encode('utf-8')
    digest = hashlib.sha256(canonical_bytes).hexdigest()
    return f"sha256:{digest}"
```

### 4.2 Verification Gate
When any subsystem loads an artifact from disk or receives a payload via REST, it MUST verify that the calculated checksum matches `metadata.checksum`. If a mismatch is detected, the operation MUST immediately abort with error `E_DATA_CHECKSUM_MISMATCH`.
