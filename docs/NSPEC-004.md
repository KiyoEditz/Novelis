# NSPEC-004: CSIR & Compiler Toolchain Specification

---
Document Status: Approved & Locked
Document Version: 1.0.0
NSPEC Compatibility:
  minimum: 1.0
  maximum: 1.x
API Compatibility:
  minimum: 1.0
  maximum: 1.x
Owner: Compiler Architecture & Runtime VM Teams
Last Updated: 2026-10-10
Normative Standard: RFC 2119 Compliance
---

## Document Rules & Strict Hierarchy Law

This specification is normative and governs the compilation pipeline, Abstract Syntax Tree (AST) representations, semantic validation rules, and schema definitions for the **Canonical Story Intermediate Representation (CSIR)** within the Novelis ecosystem.

All implementations MUST conform strictly to the definitions in `GLOSSARY.md` and the constitutional principles locked in `NSPEC-000`.

**Strict Downward-Only Document Dependency Law:**
This document depends solely upon `GLOSSARY.md`, `NSPEC-000`, `NSPEC-001`, `NSPEC-002`, and `NSPEC-003`. It SHALL NOT import or depend upon concepts defined in specifications positioned below it.

```plaintext
       [ GLOSSARY.md ] (Lexicon Single Source of Truth)
              │
              ▼
       [ NSPEC-000 ] (Core Philosophy & Constitution)
              │
              ▼
       [ NSPEC-001 ] (Domain Ontology & Canonical Model)
              │
              ▼
       [ NSPEC-002 ] (Narrative Memory Architecture & Story Bible)
              │
              ▼
       [ NSPEC-003 ] (Story Blueprint & Artifact Specification)
              │
              ▼
       [ NSPEC-004 ] (CSIR & Compiler Specification)  ◄── [Current Layer]
              │
              ▼
       [ NSPEC-005 ] (Autonomous Runtime VM Specification)
              │
              ▼
       [ API-SPEC Suite ] (Control, Telemetry & Data Planes)
```

---

## Abstract

This specification establishes the technical standard for the **Novelis Narrative Compiler** and the **Canonical Story Intermediate Representation (CSIR)**. The Compiler transforms declarative Story Blueprints and Story DSL scripts into rigid, unambiguous, and machine-executable CSIR instruction packages. CSIR serves as the strict boundary between creative planning (*Thinking*) and deterministic VM execution (*Executing*). By reducing narrative ambiguity to near-zero ($H \to 0$), CSIR guarantees that the Autonomous Runtime VM executes scenes with zero narrative drift and full mathematical determinism.

---

## 1. The Compilation Toolchain Pipeline

The Narrative Compiler operates across four discrete, deterministic phases:

```plaintext
[ Story DSL / Blueprint ]
           │
           ▼
┌──────────────────────────────┐
│ Phase 1: Lexer & Parser      │  ──► Abstract Syntax Tree (AST)
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Phase 2: Semantic Analyzer   │  ──► Validated AST + Symbol Table
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Phase 3: DAG Scheduler       │  ──► Execution Task Graph
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Phase 4: CSIR Code Generator │  ──► Canonical CSIR Payload (.csir.json)
└──────────────────────────────┘
```

### 1.1 Mathematical Formulation of Compilation
Compilation is a total deterministic function $f_{\text{compile}}$:

$$f_{\text{compile}}: \left( \mathcal{B}_{\text{story}}, \sigma(T) \right) \to \left\{ \text{CSIR}_1, \text{CSIR}_2, \dots, \text{CSIR}_n \right\}$$

Where $\sigma(T)$ represents the current Canon State at Epoch $T$, and each $\text{CSIR}_k$ represents an atomic, executable scene instruction package.

---

## 2. Canonical Story Intermediate Representation (CSIR) Standard

CSIR is an immutable, strictly typed JSON artifact. A CSIR payload represents the complete specification required by the Runtime VM to execute a single scene.

### 2.1 Double-Envelope CSIR Schema

```json
{
  "metadata": {
    "schema_version": "1.0.0",
    "artifact_type": "CSIR",
    "build_id": "bld_01h9x7a2",
    "correlation_id": "req_01h9x88a",
    "created_at": "2026-10-10T12:05:00Z",
    "checksum": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "payload": {
    "csir_id": "csir_bld01_c01_s01",
    "scene_id": "scn_c01_s01",
    "chapter_idx": 1,
    "scene_idx": 1,
    "target_epoch": 1,
    "preconditions": {
      "canon_invariants": [
        { "entity_id": "char_aria", "field": "life_status", "expected": "ALIVE" },
        { "entity_id": "char_kael", "field": "life_status", "expected": "ALIVE" },
        { "entity_id": "loc_scriptorium_ruins", "field": "status", "expected": "ACCESSIBLE" }
      ],
      "epistemic_bounds": [
        { "char_id": "char_aria", "forbidden_knowledge": ["prop_kael_is_inquisitor"] }
      ]
    },
    "participating_entities": {
      "pov_character": "char_aria",
      "actors": ["char_aria", "char_kael"],
      "primary_location": "loc_scriptorium_ruins",
      "key_props": ["item_inquisitorial_seal", "item_charred_ledger"]
    },
    "dramatic_contracts": {
      "macro_objective": "Aria recovers the imperial ledger before patrol breach.",
      "conflict_vector": "Kael attempts concealment through arson.",
      "pacing_curve": "CRESCENDO",
      "sensory_anchors": [
        "smell of burning sulfur and damp stone",
        "sound of boots crunching frost overhead",
        "cold numbness in Aria's fingertips"
      ],
      "inflection_point": "Aria catches Kael's sleeve, revealing the hidden seal."
    },
    "expected_state_deltas": {
      "character_updates": [
        { "char_id": "char_aria", "attribute": "item_inventory", "op": "ADD", "value": "item_charred_ledger" }
      ],
      "knowledge_deltas": [
        { "char_id": "char_aria", "learned_proposition": "Kael carries the Grand Inquisitor seal", "source": "OBSERVATION" }
      ],
      "relational_deltas": [
        { "source_id": "char_aria", "target_id": "char_kael", "trust_delta": -0.4, "sentiment_delta": -0.2 }
      ],
      "plot_threads_affected": [
        { "thread_id": "thr_inquisitor_secret_pact", "transition": "PROGRESSING" }
      ]
    },
    "execution_budget": {
      "target_word_count": 1800,
      "min_word_count": 1500,
      "max_word_count": 2200,
      "max_retries": 3,
      "timeout_seconds": 120
    }
  }
}
```

---

## 3. Abstract Syntax Tree (AST) & Intermediate Grammar

When compiling from Story DSL, the compiler constructs a typed AST representation:

```plaintext
                    ┌─────────────────────────┐
                    │      StoryRootNode      │
                    └────────────┬────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
┌─────────────────────┐┌─────────────────────┐┌─────────────────────┐
│    MetaDeclNode     ││   CastRegistryNode  ││    ActBlockNode     │
└─────────────────────┘└─────────────────────┘└──────────┬──────────┘
                                                         │
                                               ┌─────────┴─────────┐
                                               ▼                   ▼
                                     ┌───────────────────┐┌───────────────────┐
                                     │ ChapterBlockNode  ││ ChapterBlockNode  │
                                     └─────────┬─────────┘└───────────────────┘
                                               │
                                     ┌─────────┴─────────┐
                                     ▼                   ▼
                             ┌───────────────┐   ┌───────────────┐
                             │ SceneDeclNode │   │ SceneDeclNode │
                             └───────────────┘   └───────────────┘
```

### 3.1 Node Types Standard
* `StoryRootNode`: Root container storing project identifiers and global options.
* `CastDeclNode`: Strongly typed character declaration containing attribute map.
* `WorldRuleNode`: World axiom node storing domain category and enforcement logic.
* `SceneDeclNode`: Atomic narrative leaf node containing setting, actors, POV, dramatic contracts, and state change assertions.

---

## 4. Semantic Validation Laws

During Phase 2 of compilation, the Semantic Analyzer enforces six mandatory validation passes:

### Pass 1: Symbol Table Resolution
Every symbol (`char_id`, `loc_id`, `item_id`, `thread_id`) referenced within a scene block MUST resolve to an explicit definition declared in either the Story Blueprint or the active Story Bible database (`story_bible.db`). Unresolved symbols SHALL emit error `E_SYM_UNDEFINED`.

### Pass 2: Epistemic Feasibility Check
A character SHALL NOT be assigned an objective requiring knowledge they do not possess according to `character_knowledge`. Violations SHALL emit error `E_EPISTEMIC_VIOLATION`.

### Pass 3: Precondition Consistency Check
The compiler queries the active Story Bible at the target epoch $T$. If any precondition assertion fails (e.g., character is deceased or location is destroyed), the compiler SHALL halt with error `E_CANON_PRECONDITION_FAILED`.

### Pass 4: Timeline DAG Acyclicity
Scene execution dependencies MUST form a strict Directed Acyclic Graph (DAG). Any circular causal loop (Scene A depends on Scene B, which depends on Scene A) SHALL emit error `E_DAG_CYCLE_DETECTED`.

### Pass 5: Word Budget Feasibility
The sum of scene word budgets across a chapter MUST equal the declared chapter target word count within a $\pm 15\%$ tolerance band. Violations SHALL emit warning `W_BUDGET_DISCREPANCY`.

---

## 5. Compiler Diagnostic Standard

Every error or warning emitted by the compiler MUST format diagnostics adhering to the universal Diagnostic Payload Standard:

```json
{
  "severity": "ERROR",
  "code": "E_EPISTEMIC_VIOLATION",
  "message": "Character 'char_aria' cannot act upon proposition 'prop_kael_is_inquisitor' in scene 'scn_c01_s01'.",
  "source_location": {
    "file": "story_blueprint.dsl",
    "line": 42,
    "column": 12
  },
  "context": {
    "char_id": "char_aria",
    "missing_knowledge_id": "prop_kael_is_inquisitor",
    "current_epoch": 1
  },
  "suggested_fix": "Add an explicit discovery beat prior to line 42 or remove inquisitorial references from Aria's scene objective."
}
```

---

## 6. Verification & Test Criteria

Implementations of the Novelis Narrative Compiler MUST satisfy the following test criteria:

1. **Deterministic Output:** Compiling the identical Story Blueprint or DSL file against the identical Story Bible snapshot MUST produce an identical CSIR JSON payload with matching SHA-256 checksums.
2. **Zero Ingestion of Undefined Entities:** The compiler MUST reject any DSL input containing an undefined entity reference before generating CSIR code.
3. **Double-Envelope Integrity:** Every emitted `.csir.json` artifact MUST be verified against its internal SHA-256 payload checksum upon creation.
