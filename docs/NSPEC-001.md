# NSPEC-001: Domain Ontology & Canonical Story Model

---
Document Status: Approved & Locked
Document Version: 1.2.0
NSPEC Compatibility:
minimum: 1.0
maximum: 1.x
API Compatibility:
minimum: 1.0
maximum: 1.x
Owner: Product Experience & Engine Architecture Teams
Last Updated: 2026-08-05
Normative Standard: RFC 2119 Compliance
---

## Document Rules & Strict Hierarchy Law

This specification is normative and defines the foundational domain ontology for all fictional universe entities, states, and relations within the Novelis ecosystem.

This document specifies Domain Models only ("What exists"). It SHALL NOT specify execution algorithms, rule enforcement loops, or runtime scheduling ("How it behaves").

**Strict Downward-Only Document Dependency Law:**
A document in the specification stack SHALL NOT depend on, reference, or import concepts from documents positioned below it.

```plaintext
       [ GLOSSARY.md ] (Lexicon Single Source of Truth)
              │
              ▼
       [ NSPEC-000 ] (Core Philosophy & Constitution)
              │
              ▼
       [ NSPEC-001 ] (Domain Ontology & Canonical Model)  ◄── [Current Layer]
              │
              ▼
       [ NSPEC-002 ] (Narrative Memory Architecture & Story Bible)
              │
              ▼
       [ NSPEC-003 ] (Story Blueprint & Artifact Specification)
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

This specification defines the pure domain ontology for the Fiction Operating System (FOS). It establishes the mathematical formulation of Fictional Universes, Story Root Identities ($I_S$), Stories ($S$), Canon Lines, the clean Root Story State ($\sigma$), entity persistent/transient taxonomy, dual-timeline structures, and the formal logical distinction between Canon (Logical Truth) and Event Store (Historical Record).

---

## 1. Fictional Universe & Story Mathematical Formulation

### 1.1 Fictional Universe ($U$)
A Fictional Universe $U$ is a persistent container hosting one or more discrete stories:

$$U = \left\langle \text{Universe\_ID}, \Phi, \mathcal{S} \right\rangle$$

Where $\Phi$ represents the invariant global Rule Anchors shared across all stories in Universe $U$, and $\mathcal{S}$ is the set of stories $\{S_1, S_2, \dots, S_n\}$.

### 1.2 Story Identity ($I_S$) & Story Instance ($S$)
Every Story instance $S \in \mathcal{S}$ possesses a explicit domain identity:

$$I_S = \left\langle \text{Story\_ID}, \text{Universe\_ID}, \text{Canon\_Line\_ID}, \text{Story\_Type}, \text{Parent\_Story\_ID}, \text{Origin} \right\rangle$$

Where:
* **$\text{Canon\_Line\_ID}$:** Anchors the story to a specific canon continuity (e.g., `canon_main`, `canon_alternate_ending`, `canon_prequel`).
* **$\text{Story\_Type}$:** Indicates structural classification $\in \{\text{MAIN\_CANON}, \text{BRANCH}, \text{SPIN\_OFF}, \text{WHAT\_IF}\}$.

A Story $S$ is mathematically defined as the 4-tuple:

$$S = \left\langle I_S, \sigma, \mathbb{T}_{\text{struct}}, \mathbb{T}_{\text{sim}} \right\rangle$$

---

## 2. Dual Timeline Architecture

```plaintext
Structural Timeline (Presentation):  [ Book / Act ] ──► [ Chapter ] ──► [ Scene ]
                                                                           │
                                                                           ▼
Simulation Timeline (State Steps):   [ Epoch T₀ ] ──► [ Epoch T₁ ] ──► [ Epoch T₂ ]
```

### 2.1 Structural Timeline ($\mathbb{T}_{\text{struct}}$)
The human-facing organizational structure organizing narrative flow:

$$\mathbb{T}_{\text{struct}} = \text{Acts} \to \text{Chapters} \to \text{Scenes}$$

### 2.2 Simulation Timeline ($\mathbb{T}_{\text{sim}}$)
The discrete, monotonically increasing sequence of simulation state change steps:

$$\mathbb{T}_{\text{sim}} = \{ T_0, T_1, T_2, \dots, T_n \}, \quad T_k \in \mathbb{N}_0$$

* **Story Epoch ($T$):** The fundamental unit of simulation time. An Epoch transition $T \to T+1$ occurs if and only if an atomic transition produces a non-empty State Delta ($\Delta \sigma \neq \emptyset$).

### 2.3 Timeline Markers
Timeline Markers provide domain-level annotations across $\mathbb{T}_{\text{struct}}$ and $\mathbb{T}_{\text{sim}}$:

* **Marker Types:** BOOKMARK, CHECKPOINT, CONFLICT_POINT, FORESHADOW_ANCHOR, FLASHBACK_ORIGIN, BRANCH_NODE.

---

## 3. The Pure Story State Container ($\sigma$)

The Story State ($\sigma$) contains pure domain variables only at simulation Epoch $T$. Implementation metadata (checksums, compiler versions, build IDs) SHALL NOT reside within $\sigma$:

$$\sigma(T) = \left\langle \mathcal{W}(T), \mathcal{C}(T), \mathcal{R}(T), \mathcal{A}(T), \mathcal{Q}(T), \text{Canon}(T) \right\rangle$$

Where:
* **$\mathcal{W}(T)$ (World State):** Environmental conditions, locations, weather, global variables, and active world flags.
* **$\mathcal{C}(T)$ (Character Ensemble):** The collection of all character entity states active in the story.
* **$\mathcal{R}(T)$ (Relational Matrix):** The network of directed interpersonal, emotional, and political vectors between entities.
* **$\mathcal{A}(T)$ (Active Events):** Stateful occurrences that persist across more than one Epoch ($T_{\text{duration}} > 1$). Instantaneous state changes MUST be recorded as State Deltas ($\Delta \sigma$), not Active Events.
* **$\mathcal{Q}(T)$ (Objectives Set):** Active narrative drives categorized into:
    * **Story Objectives:** High-level global plot objectives.
    * **Character Objectives:** Individual character motivations and personal goals.
    * **Scene Objectives:** Immediate tactical goals for a specific scene.
* **$\text{Canon}(T)$ (Logical Truth):** The set of all factual assertions validated as absolute truth at Epoch $T$.

---

## 4. Canon vs. Event Store Distinction

The system enforces a formal logical separation between Truth and Historical Event History:

$$\text{Event Store (Historical Record)} \xrightarrow{\quad f_{\text{reconstruct}}\quad} \text{Canon}(T) \text{ (Logical Truth)}$$

* **Event Store (Historical Record):** An append-only, immutable transaction log recording every micro-event delta in sequence (What happened).
* **Canon (Logical Truth):** The current, compiled set of facts deduced from the Event Store up to Epoch $T$ (What is currently true).

---

## 5. Entity Taxonomy & Root Inheritance

All entities in the Novelis ecosystem MUST inherit from a common Root Entity Identity:

$$E_{\text{root}} = \left\langle \text{Canonical\_ID}, \text{Entity\_Type}, \text{Display\_Name}, \text{Lifecycle\_Status} \right\rangle$$

Where $\text{Lifecycle\_Status} \in \{\text{UNINITIALIZED}, \text{ACTIVE}, \text{DORMANT}, \text{DESTROYED}, \text{ARCHIVED}\}$.

### 5.1 Persistent vs. Transient Entity Domain Classification

Entities are categorized by their lifecycle behavior within the story domain:

**Persistent Entities:** Entities that retain identity and continuity across the entire story lifespan.
* `ENT_CHAR` (Character)
* `ENT_LOC` (Location)
* `ENT_ITEM` (Item)
* `ENT_FACT` (Faction / Organization)
* `ENT_CREAT` (Creature)
* `ENT_VEH` (Vehicle)

**Transient Entities:** Temporal entities created during execution that expire or resolve upon task completion.
* `ENT_DLG` (Dialogue Act)
* `ENT_CND` (Status Condition)
* `ENT_QST` (Objective / Quest)
* `ENT_EVT` (Active Event)
* `ENT_MRK` (Timeline Marker)

### 5.2 Abstract Character Entity Model

A Character Entity $c \in \mathcal{E}$ is defined by its domain attributes:

$$\mathcal{C}_c(T) = \left\langle E_{\text{root}}, \text{Identity}_c, \mathcal{K}_c(T), \mathcal{G}_c(T), P_c(T), I_c(T), \mathcal{M}_{\text{beh}} \right\rangle$$

* **$\mathcal{K}_c(T)$ (Knowledge Scope):** The set of propositions character $c$ believes or knows at Epoch $T$. Knowledge Scope carries no assumption of objective truth ($\mathcal{K}_c(T) \neq \text{Canon}(T)$).
* **$\mathcal{M}_{\text{beh}}$ (Behavior Model Specification):** Declares the abstract behavior framework type (e.g., BDI-M, GOAP, HTN). Execution algorithms ARE DEFERRED to NSPEC-005.