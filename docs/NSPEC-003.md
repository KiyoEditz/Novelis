# NSPEC-003: Story Blueprint & Declarative Artifact Specification

---
Document Status: Approved & Locked
Document Version: 1.0.0
NSPEC Compatibility:
  minimum: 1.0
  maximum: 1.x
API Compatibility:
  minimum: 1.0
  maximum: 1.x
Owner: Creative Planning & Compiler Architecture Teams
Last Updated: 2026-10-10
Normative Standard: RFC 2119 Compliance
---

## Document Rules & Strict Hierarchy Law

This specification is normative and governs the schemas, syntax, validation rules, and lifecycle of the **Story Blueprint** and associated declarative narrative artifacts within the Novelis ecosystem.

All implementations MUST conform strictly to the definitions in `GLOSSARY.md` and the constitutional principles locked in `NSPEC-000`.

**Strict Downward-Only Document Dependency Law:**
This document depends solely upon `GLOSSARY.md`, `NSPEC-000`, `NSPEC-001`, and `NSPEC-002`. It SHALL NOT import or depend upon concepts defined in specifications positioned below it.

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
       [ NSPEC-003 ] (Story Blueprint & Artifact Specification)  ◄── [Current Layer]
              │
              ▼
       [ NSPEC-004 ] (CSIR & Compiler Specification)
              │
              ▼
       [ NSPEC-005 ] (Autonomous Runtime VM Specification)
              │
              ▼
       [ API-SPEC Suite ] (Control, Telemetry & Data Planes)
```

---

## Abstract

This specification establishes the technical contract for the **Story Blueprint** ($\mathcal{B}_{\text{story}}$). The Story Blueprint is the primary declarative output of the Creative Planning Layer. It synthesizes user premises, thematic objectives, character arcs, world rules, and structural plotting into a strictly typed, versioned, and machine-parseable JSON specification. The Story Blueprint defines *what the story intends to achieve* before the Compiler translates it into executable instructions for the Runtime Virtual Machine.

---

## 1. Mathematical Formulation of the Story Blueprint

A Story Blueprint $\mathcal{B}_{\text{story}}$ is mathematically formulated as the 6-tuple:

$$\mathcal{B}_{\text{story}} = \left\langle \mathcal{M}_{\text{meta}}, \Theta, \mathcal{C}_{\text{cast}}, \Phi_{\text{world}}, \mathcal{G}_{\text{plot}}, \mathbb{T}_{\text{struct}} \right\rangle$$

Where:
* **$\mathcal{M}_{\text{meta}}$ (Metadata & Generation Constraints):** Project identity, target length, linguistic registers, and Point of View (POV) declarations.
* **$\Theta$ (Thematic Matrix):** Set of central dramatic arguments, thematic tensions, and stylistic tonal bounds.
* **$\mathcal{C}_{\text{cast}}$ (Ensemble Blueprint):** Declarations of character psychological archetypes, motivation vectors, flaws, and anticipated transformation arcs.
* **$\Phi_{\text{world}}$ (World Invariants):** Hard world rules, magical/technological axioms, and spatial locations.
* **$\mathcal{G}_{\text{plot}}$ (Plot Arc Graph):** Directed graph of causal plot developments, inciting incidents, climaxes, and Chekhov's guns.
* **$\mathbb{T}_{\text{struct}}$ (Structural Blueprint):** Explicit hierarchy of Acts, Chapters, and Scene Beating specifications.

---

## 2. Double-Envelope Artifact Schema Standard

Every Story Blueprint persisted to storage or transmitted over the Control/Data Plane MUST implement the universal double-envelope pattern defined in `API-SPEC`:

```json
{
  "metadata": {
    "schema_version": "1.0.0",
    "artifact_type": "STORY_BLUEPRINT",
    "build_id": "bld_01h9x7a2",
    "correlation_id": "req_01h9x88a",
    "created_at": "2026-10-10T12:00:00Z",
    "checksum": "sha256:d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35"
  },
  "payload": {
    "project_id": "proj_solaris_chronicles",
    "story_identity": {
      "story_id": "sty_main_01",
      "universe_id": "univ_solaris",
      "canon_line_id": "canon_main",
      "story_type": "MAIN_CANON"
    },
    "narrative_constraints": {
      "target_word_count": 85000,
      "pacing": "FAST_DELIBERATE",
      "pov_mode": "THIRD_PERSON_LIMITED",
      "primary_pov_character": "char_aria",
      "tense": "PAST"
    },
    "thematic_matrix": {
      "central_argument": "Truth preserved through deception ultimately corrodes trust.",
      "motifs": ["ancient clocks", "silver feather", "subterranean frost"],
      "mood_palette": ["melancholic", "tense", "mysterious"]
    },
    "cast": [],
    "world_invariants": [],
    "structural_timeline": []
  }
}
```

---

## 3. Normative Blueprint Component Schemas

### 3.1 Cast Blueprint Specification (`payload.cast`)

Each character entry MUST provide full initial state bounds and anticipated arc trajectory:

```json
{
  "char_id": "char_aria",
  "canonical_name": "Aria Valen",
  "archetype": "RELUCTANT_INHERITOR",
  "physical_invariants": {
    "age": 19,
    "eyes": "blue",
    "hair": "silver",
    "distinguishing_marks": ["faint scar across left collarbone"]
  },
  "psychological_profile": {
    "core_desire": "To uncover the reason behind her father's exile without igniting civil war.",
    "internal_flaw": "Inability to delegate or trust collaborators.",
    "lie_believed": "Self-reliance is the only absolute shield against betrayal.",
    "truth_to_realize": "Isolation makes destruction inevitable."
  },
  "arc_trajectory": {
    "starting_state": "DISTRUSTFUL_OUTCAST",
    "midpoint_shift": "FORCED_COOPERATION",
    "climactic_state": "VULNERABLE_LEADER"
  }
}
```

### 3.2 World Invariants Specification (`payload.world_invariants`)

Defines non-negotiable physical, political, and metaphysical laws that bind all scenes:

```json
{
  "rule_id": "rule_magic_thermodynamics",
  "domain": "MAGIC_SYSTEM",
  "axiom": "Thermal energy drawn to ignite kinetic force must be drawn from the caster's core temperature.",
  "violation_consequence": "Hypothermic shock and organ failure.",
  "override_permitted": false
}
```

### 3.3 Structural Timeline & Scene Beat Specification (`payload.structural_timeline`)

The Structural Timeline decomposes the novel into a deterministic hierarchy of Acts $\to$ Chapters $\to$ Scenes:

```json
[
  {
    "act_idx": 1,
    "title": "Act I: Whispers in the Frost",
    "chapters": [
      {
        "chapter_idx": 1,
        "title": "The Sunken Scriptorium",
        "target_word_count": 3500,
        "scenes": [
          {
            "scene_idx": 1,
            "scene_id": "scn_c01_s01",
            "setting": {
              "location_id": "loc_scriptorium_ruins",
              "time_of_day": "DUSK",
              "weather": "BITTER_SLEET"
            },
            "pov_char_id": "char_aria",
            "cast_present": ["char_aria", "char_kael"],
            "scene_objective": "Aria must extract the encrypted ledger from the imperial seal before the patrol reaches the lower arch.",
            "conflict_vector": "Kael attempts to incinerate the ledger to protect his covert allegiance.",
            "expected_outcome": "Aria recovers the charred ledger but discovers Kael is carrying the seal of the Grand Inquisitor.",
            "foreshadowing_anchors": ["thr_inquisitor_secret_pact"],
            "target_word_count": 1800
          }
        ]
      }
    ]
  }
]
```

---

## 4. Internal Story DSL (Domain Specific Language)

To facilitate human inspection, authorial override, and direct multi-agent manipulation, the Story Blueprint supports an equivalent, isomorphic plaintext representation: the **Novelis Story DSL**.

### 4.1 DSL Grammar & Syntax Standard

```dsl
STORY "Solaris Chronicles" {
    UNIVERSE: "univ_solaris"
    CANON_LINE: "canon_main"
    TARGET_WORDS: 85000
    POV: THIRD_PERSON_LIMITED ("char_aria")
    TENSE: PAST
}

CHARACTER "char_aria" {
    NAME: "Aria Valen"
    AGE: 19
    PHYSICAL: { eyes: "blue", hair: "silver" }
    DESIRE: "Uncover father's exile reason"
    FLAW: "Extreme distrust"
    ARC: DISTRUSTFUL_OUTCAST -> VULNERABLE_LEADER
}

ACT 1: "Whispers in the Frost" {
    CHAPTER 1: "The Sunken Scriptorium" {
        SCENE 1 "scn_c01_s01" {
            LOCATION: "loc_scriptorium_ruins"
            CAST: ["char_aria", "char_kael"]
            POV: "char_aria"
            OBJECTIVE: "Extract encrypted ledger before imperial patrol arrives"
            CONFLICT: "Kael attempts to burn the documents"
            OUTCOME: "Aria secures charred ledger, discovers Kael's inquisitorial token"
            PROMISE: "thr_inquisitor_secret_pact"
            WORDS: 1800
        }
    }
}
```

### 4.2 Bi-directional Isomorphism Guarantee
The Compiler Layer MUST guarantee lossless bi-directional translation between the Story DSL plaintext format and the Story Blueprint JSON schema:

$$\mathcal{B}_{\text{story}} \equiv \text{DSL}(\mathcal{B}_{\text{story}})$$

---

## 5. Blueprint Validation & Invariant Laws

Before a Story Blueprint can be compiled into a Canonical Story Intermediate Representation (CSIR), the Compiler validation pass MUST enforce five invariant laws:

### Invariant I: Strict Entity Referential Integrity
Every entity reference (`char_id`, `location_id`, `rule_id`, `thread_id`) appearing within a Scene Beat MUST be explicitly defined in `payload.cast`, `payload.world_invariants`, or the project's Story Bible.

### Invariant II: Structural Monotonicity
Scene and chapter indices MUST form a strictly monotonically increasing sequence:
$$\text{idx}_{k+1} = \text{idx}_k + 1, \quad \forall k \in \mathbb{N}$$

### Invariant III: POV Existence Invariant
In any scene with a designated `pov_char_id`, that character MUST be declared as a member of `cast_present` and possess a `life_status` of `ALIVE` at the corresponding simulation epoch.

### Invariant IV: Plot Thread Lifecycle Invariant
Any plot thread declared in `foreshadowing_anchors` MUST resolve or progress in at least one subsequent structural scene. Orphaned promises remaining open at the conclusion of the final chapter SHALL trigger a compiler warning (`WARN_UNRESOLVED_CHEKHOV_GUN`).

### Invariant V: Immutability Upon Compilation
Once a Story Blueprint receives the `APPROVED` lifecycle tag and compilation into CSIR initiates, the blueprint artifact SHALL be cryptographically locked via SHA-256 checksum. Any authorial modification requires generating a new Blueprint revision.
