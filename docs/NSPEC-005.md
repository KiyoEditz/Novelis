# NSPEC-005: Autonomous Runtime Virtual Machine (VM) Specification

---
Document Status: Approved & Locked
Document Version: 1.0.0
NSPEC Compatibility:
  minimum: 1.0
  maximum: 1.x
API Compatibility:
  minimum: 1.0
  maximum: 1.x
Owner: Engine Architecture & Runtime VM Teams
Last Updated: 2026-10-10
Normative Standard: RFC 2119 Compliance
---

## Document Rules & Strict Hierarchy Law

This specification is normative and governs the architecture, state transition mechanics, task scheduling, memory isolation, and transactional execution model of the **Autonomous Runtime Virtual Machine (VM)** within the Novelis ecosystem.

All implementations MUST conform strictly to the definitions in `GLOSSARY.md` and the constitutional principles locked in `NSPEC-000`.

**Strict Downward-Only Document Dependency Law:**
This document depends solely upon `GLOSSARY.md`, `NSPEC-000`, `NSPEC-001`, `NSPEC-002`, `NSPEC-003`, and `NSPEC-004`. It SHALL NOT import or depend upon concepts defined in specifications positioned below it.

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
       [ NSPEC-004 ] (CSIR & Compiler Specification)
              │
              ▼
       [ NSPEC-005 ] (Autonomous Runtime VM Specification)  ◄── [Current Layer]
              │
              ▼
       [ API-SPEC Suite ] (Control, Telemetry & Data Planes)
```

---

## Abstract

This specification establishes the technical standard for the **Novelis Autonomous Runtime Virtual Machine (VM)**. The Runtime VM is the deterministic execution engine responsible for resolving Directed Acyclic Graphs (DAGs) of scene tasks, enforcing narrative preconditions, evaluating character behavior models, and applying state delta mutations ($\Delta \sigma$) to the immutable Canon. In accordance with NSPEC-000 Article II, the Runtime VM operates with zero creative freedom ($H = 0$). It does not invent plot turns or hallucinate facts; it acts as a rigid, transactional state computer executing validated CSIR payloads.

---

## 1. Virtual Machine Architecture & Formal State

The complete state of the Runtime VM at any point during a Build is defined as the 5-tuple:

$$\mathcal{VM} = \left\langle \sigma(T), \mathcal{Q}_{\text{task}}, \mathcal{E}_{\text{store}}, \mathcal{M}_{\text{mem}}, \Lambda_{\text{lock}} \right\rangle$$

Where:
* **$\sigma(T)$ (Active Story State):** The current snapshot of pure domain entities, character scopes, and active relations at Epoch $T$.
* **$\mathcal{Q}_{\text{task}}$ (Task Scheduler Queue):** The Directed Acyclic Graph (DAG) of pending, executing, and completed scene execution tasks.
* **$\mathcal{E}_{\text{store}}$ (Transactional Event Store):** The append-only, immutable transaction log recording every historic state delta.
* **$\mathcal{M}_{\text{mem}}$ (Memory System Interface):** The bridge to the SQLite Story Bible and LanceDB Hybrid Vector Store defined in `NSPEC-002`.
* **$\Lambda_{\text{lock}}$ (Concurrency Lock Table):** Mutex registry managing entity isolation across parallel scene execution workers.

---

## 2. The Task Execution Lifecycle

The execution of each CSIR payload passes through a strict 5-state lifecycle machine:

```plaintext
      ┌───────────┐
      │  QUEUED   │
      └─────┬─────┘
            │ dependencies resolved
            ▼
      ┌───────────┐
      │  RUNNING  │ ◄── Preconditions checked & locks acquired
      └─────┬─────┘
            │ draft prose generated
            ▼
      ┌───────────┐
      │ VALIDATING│ ◄── Rule Engine & Bible Consistency Pass
      └─────┬─────┘
       ┌────┴────────────────────────┐
       ▼ (Pass)                      ▼ (Violation)
 ┌───────────┐                 ┌─────────────┐
 │ COMMITTED │                 │ ROLLED_BACK │
 └───────────┘                 └──────┬──────┘
                                      │ trigger Self-Healing
                                      ▼
                                ┌───────────┐
                                │ RETRYING  │
                                └───────────┘
```

### 2.1 State Definitions
* **`QUEUED`:** Task is registered in the execution DAG; waiting for parent scene dependencies to commit.
* **`RUNNING`:** Preconditions verified; entity mutexes acquired; context assembled; dispatched to Renderer Layer.
* **`VALIDATING`:** Draft output received; consistency checks executing against the Story Bible.
* **`COMMITTED`:** State delta $\Delta \sigma$ committed to Event Store; Epoch $T$ incremented to $T+1$; locks released.
* **`ROLLED_BACK`:** Validation failed or Cancellation Token tripped; transaction aborted; uncommitted changes purged.

---

## 3. The 3-Phase State Transition Protocol (3PC-Narrative)

To guarantee ACID (Atomicity, Consistency, Isolation, Durability) guarantees across fictional state changes, the Runtime VM executes state mutations via a 3-Phase Commit protocol:

### Phase 1: Pre-Validation & Invariant Assertion
1. The VM reads the `preconditions` declared in the target CSIR payload.
2. The VM executes exact boolean queries against the active Story Bible database (`story_bible.db`).
3. If any assertion fails (e.g., character is marked `DECEASED`), the task terminates immediately with error `E_CANON_PRECONDITION_FAILED` without invoking the Renderer Layer.

### Phase 2: Generation & Verification
1. The VM dispatches the compiled CSIR payload to the Renderer Layer via the Capability Negotiation Protocol.
2. The Renderer produces candidate prose.
3. The VM invokes the Consistency Validation Loop (NSPEC-002 Section 5.4).

### Phase 3: Atomic State Commit
If and only if Phase 2 succeeds:
1. **Append Event Store:** An immutable event record containing the full JSON State Delta is written to the append-only log.
2. **Commit Story Bible:** SQLite transaction executes, updating character attributes, relation weights, and plot threads.
3. **Index Vector Memory:** The scene's dense and sparse embeddings are written to the LanceDB `scenes` table.
4. **Advance Simulation Clock:** The global Simulation Epoch increments:
   $$T \to T + 1$$
5. **Emit Telemetry Event:** Emits `runtime.state_changed` over the Telemetry Plane.

---

## 4. Concurrency & Parallel Scene Execution

When an author designs a multi-strand narrative (e.g., Chapter 4 follows Aria in the capital while Chapter 5 follows Kael in the eastern border), the VM scheduler MAY execute scenes concurrently under the following isolation rule:

### 4.1 Disjoint Entity Set Law
Two scene execution tasks $S_A$ and $S_B$ MAY execute concurrently if and only if their participating mutable entity sets are completely disjoint:

$$\text{Mut}(S_A) \cap \text{Mut}(S_B) = \emptyset$$

Where $\text{Mut}(S)$ represents the set of all entities modified by the expected state deltas of scene $S$.

### 4.2 Entity Lock Table
* If two concurrent scenes read from the same entity without mutating it, shared read locks (`S_LOCK`) are granted.
* If a scene declares intent to mutate an entity (e.g., character injury or death), an exclusive write lock (`X_LOCK`) MUST be acquired.

---

## 5. Behavior Modeling & Decision Execution

As specified in `NSPEC-001 Section 5.2`, character actions are governed by explicit behavioral model frameworks ($\mathcal{M}_{\text{beh}}$):

### 5.1 BDI-M (Belief-Desire-Intention for Narrative)
When evaluating character actions, the Runtime VM models decision-making strictly through:
* **Beliefs ($\mathcal{K}_c(T)$):** What the character knows or believes from `character_knowledge`. The character CANNOT act on facts not contained in their belief set.
* **Desires ($\mathcal{G}_c(T)$):** High-level motivations defined in `characters.core_motivation`.
* **Intentions ($I_c(T)$):** The immediate tactical action chosen to fulfill the desire given active beliefs.

### 5.2 GOAP (Goal-Oriented Action Planning)
For tactical or combative scenes, characters choose actions by formulating an acyclic sequence of preconditions and postconditions:
$$\text{Current State} \xrightarrow{\quad \text{Action}_1 \quad} \text{State}_1 \xrightarrow{\quad \text{Action}_2 \quad} \text{Goal State}$$
The Runtime VM rejects any drafted prose where a character accomplishes a goal by skipping necessary physical preconditions.

---

## 6. Crash Recovery & State Replay

To satisfy the Reproducibility objective (NSPEC-000 Section 2), the Runtime VM guarantees complete state reconstruction from raw historical logs:

### 6.1 State Reconstruction Function
The active state $\sigma(T)$ at any historical Epoch $T$ can be reconstructed deterministically:

$$\sigma(T) = \sigma_0 \oplus \sum_{k=1}^{T} \Delta \sigma_k$$

Where $\sigma_0$ is the initial Genesis State declared in the Story Blueprint, and $\Delta \sigma_k$ is the sequence of state deltas stored in the Transactional Event Store.

### 6.2 Periodic Snapshotting
* Every 10 committed scenes (or upon chapter boundaries), the Runtime VM writes an atomic snapshot archive (`snapshot_epoch_{T}.tar.gz`) containing:
  1. Complete SQLite binary dump of `story_bible.db`.
  2. LanceDB directory snapshot.
  3. Active Summary Tree JSON.
* Upon unexpected crash or system power loss, the VM recovers in $< 2$ seconds by loading the latest valid snapshot and replaying only subsequent events.

---

## 7. Verification & Compliance Standards

Implementations of the Novelis Autonomous Runtime VM MUST satisfy the following test criteria:

1. **Deterministic State Replay:** Replaying a 50-scene event log from Genesis State MUST produce a Story Bible database identical byte-for-byte to the original committed database.
2. **Zero Orphan Commits:** Terminating the VM process abruptly during Phase 2 (Generation) MUST NOT leave uncommitted partial deltas in either SQLite or LanceDB.
3. **Mutual Exclusion:** Concurrent execution of two scenes attempting to mutate the same character's status MUST deterministically serialize execution without race conditions.
