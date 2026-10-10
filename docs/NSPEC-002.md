# NSPEC-002: Narrative Memory Architecture, Story Bible & Multi-Agent Scene Generation

---
Document Status: Approved & Locked
Document Version: 1.0.0
NSPEC Compatibility:
  minimum: 1.0
  maximum: 1.x
API Compatibility:
  minimum: 1.0
  maximum: 1.x
Owner: Narrative Memory & Engine Architecture Teams
Last Updated: 2026-10-10
Normative Standard: RFC 2119 Compliance
---

## Document Rules & Strict Hierarchy Law

This specification is normative and governs the architecture, data schemas, retrieval mechanics, and multi-agent execution pipeline of the Novelis Memory Subsystem and Story Bible.

All implementations MUST conform strictly to the definitions in `GLOSSARY.md` and the constitutional principles locked in `NSPEC-000`.

**Strict Downward-Only Document Dependency Law:**
This document depends solely upon `GLOSSARY.md`, `NSPEC-000`, and `NSPEC-001`. It SHALL NOT import or depend upon concepts defined in specifications positioned below it.

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
       [ NSPEC-002 ] (Narrative Memory Architecture & Story Bible)  ◄── [Current Layer]
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

This specification establishes the normative architecture for the Novelis Narrative Memory Subsystem. To sustain narrative consistency across extended fictional works (50,000 to 100,000+ words), the Fiction Operating System (FOS) implements a multi-tier memory architecture:
1. **Relational Story Bible ($\mathcal{B}$):** An embedded relational store (SQLite) preserving structured, non-negotiable narrative assertions (*Hard Canon*), including physical character traits, character knowledge boundaries, world laws, directed relationship vectors, and unresolved plot threads (narrative promises).
2. **Semantic Hybrid Vector Memory ($\mathcal{V}$):** An embedded vector store (LanceDB) utilizing dual dense-sparse representations (BGE-M3) and cross-encoder reranking (bge-reranker-v2-m3) for high-recall scene retrieval with exact named entity preservation.
3. **Hierarchical Summarization Tree ($\mathcal{H}$):** A multi-resolution recursive summary hierarchy (Scene $\to$ Chapter $\to$ Arc $\to$ Book) maintaining macroscopic narrative coherence without saturating large context windows.
4. **5-Step Scene Generation Pipeline:** A deterministic multi-agent execution workflow (Outline $\to$ Retrieve $\to$ Draft $\to$ Consistency Check $\to$ Fact Ingestion).
5. **Distributed Compute & Remote Inference Strategy:** Decoupled execution enabling low-resource local runtimes to offload intensive inference workloads (LLMs and heavy neural embeddings) to cloud APIs or remote notebook instances (Google Colab, Kaggle).

---

## 1. Mathematical Formulation of Dual Memory

The total active memory state of a Story $S$ at Simulation Epoch $T$ is defined as the 3-tuple:

$$\mathcal{M}(T) = \left\langle \mathcal{B}(T), \mathcal{V}(T), \mathcal{H}(T) \right\rangle$$

Where:
* **$\mathcal{B}(T)$ (Story Bible / Hard Canon):** Relational state of truth.
* **$\mathcal{V}(T)$ (Episodic Vector Memory):** Indexed collection of past scene prose chunks and embeddings.
* **$\mathcal{H}(T)$ (Hierarchical Summarization Tree):** Multi-resolution condensation of narrative progress up to Epoch $T$.

---

## 2. Component 1: Relational Story Bible ($\mathcal{B}$)

The Story Bible is the primary safeguard against narrative hallucination and contradiction. All facts in the Story Bible represent deterministic logical truth ($\text{Canon}(T)$).

### 2.1 Formal Structure
$$\mathcal{B}(T) = \left\langle \mathcal{T}_{\text{char}}, \mathcal{T}_{\text{know}}, \mathcal{T}_{\text{loc}}, \mathcal{T}_{\text{rel}}, \mathcal{T}_{\text{thread}}, \mathcal{T}_{\text{time}} \right\rangle$$

### 2.2 Normative Relational Schema (SQLite 3.x)

All Novelis story projects MUST initialize an embedded SQLite instance (`story_bible.db`) adhering to the following normative data definitions:

```sql
-- 1. Characters: Persistent physical and psychological profiles
CREATE TABLE characters (
    char_id TEXT PRIMARY KEY,               -- e.g. 'char_aria'
    canonical_name TEXT NOT NULL,           -- e.g. 'Aria Valen'
    aliases TEXT,                           -- JSON array of strings: '["The Silver Crow", "Aria"]'
    age INTEGER,
    physical_traits TEXT NOT NULL,          -- Strict immutable traits: '{"eyes": "blue", "hair": "silver", "height": "165cm"}'
    core_motivation TEXT NOT NULL,          -- Primary drive
    life_status TEXT NOT NULL CHECK(life_status IN ('ALIVE', 'DECEASED', 'MISSING', 'UNINITIALIZED')),
    created_epoch INTEGER NOT NULL,
    updated_epoch INTEGER NOT NULL
);

-- 2. Character Knowledge Scope: Mencegah kebocoran informasi antar-karakter
CREATE TABLE character_knowledge (
    knowledge_id TEXT PRIMARY KEY,
    char_id TEXT NOT NULL REFERENCES characters(char_id),
    proposition TEXT NOT NULL,              -- e.g. 'Father was an Imperial spy'
    learned_epoch INTEGER NOT NULL,         -- Simulation Epoch when learned
    source_entity_id TEXT,                  -- Who or what revealed it
    is_belief BOOLEAN NOT NULL DEFAULT 1    -- 1 if believed true, 0 if suspicion
);

-- 3. Locations: Geography, environment, and world laws
CREATE TABLE locations (
    loc_id TEXT PRIMARY KEY,                -- e.g. 'loc_sunken_temple'
    name TEXT NOT NULL,
    parent_loc_id TEXT REFERENCES locations(loc_id),
    environmental_conditions TEXT,          -- '{"climate": "subterranean humid", "hazard": "toxic spores"}'
    cultural_rules TEXT,                    -- Laws or traditions binding this location
    status TEXT NOT NULL DEFAULT 'ACCESSIBLE'
);

-- 4. Relational Matrix: Directed interpersonal edges
CREATE TABLE relations (
    source_char_id TEXT NOT NULL REFERENCES characters(char_id),
    target_char_id TEXT NOT NULL REFERENCES characters(char_id),
    relation_type TEXT NOT NULL,            -- e.g. 'MENTOR', 'RIVAL', 'SIBLING', 'ENEMY'
    sentiment_score REAL NOT NULL,          -- Continuous scale: -1.0 (pure hatred) to +1.0 (deep love)
    trust_score REAL NOT NULL,              -- Continuous scale: 0.0 (zero trust) to 1.0 (unconditional trust)
    notes TEXT,                             -- Contextual summary of dynamic
    updated_epoch INTEGER NOT NULL,
    PRIMARY KEY (source_char_id, target_char_id)
);

-- 5. Plot Threads: Tracked narrative promises and Chekhov's guns
CREATE TABLE plot_threads (
    thread_id TEXT PRIMARY KEY,             -- e.g. 'thr_father_amulet'
    title TEXT NOT NULL,
    description TEXT NOT NULL,              -- The promise made to the reader
    opened_epoch INTEGER NOT NULL,
    target_resolution_epoch INTEGER,        -- Projected payoff horizon
    status TEXT NOT NULL CHECK(status IN ('OPEN', 'PROGRESSING', 'RESOLVED', 'ABANDONED')),
    payoff_condition TEXT NOT NULL,         -- What must occur to satisfy this promise
    associated_characters TEXT              -- JSON array of char_ids
);

-- 6. Timeline Events: Monotonic simulation events
CREATE TABLE timeline_events (
    event_id TEXT PRIMARY KEY,
    epoch_id INTEGER NOT NULL UNIQUE,
    structural_chapter_idx INTEGER NOT NULL,
    structural_scene_idx INTEGER NOT NULL,
    in_universe_timestamp TEXT,             -- e.g. 'Year 342, 14th of Sunfall, Dusk'
    summary TEXT NOT NULL,
    state_delta_json TEXT NOT NULL          -- JSON serialized delta applied to Canon
);
```

### 2.3 Hard Canon Invariant Rule
The Runtime VM and Consistency Validator MUST reject any generated prose whose factual assertions contradict records in `characters`, `locations`, or `character_knowledge` without a preceding explicit State Delta transaction.

---

## 3. Component 2: Semantic Hybrid Vector Memory ($\mathcal{V}$)

While the Story Bible handles structured facts, narrative prose requires deep context regarding mood, tone, previous interactions, and specific descriptive nuances from past scenes.

### 3.1 Dual Dense-Sparse Embedding Standard (BGE-M3)
Every historical scene chunk MUST be encoded into both a dense semantic vector and a sparse lexical token weight vector:

$$\mathbf{e}(d) = \left\langle \mathbf{v}_{\text{dense}}, \mathbf{v}_{\text{sparse}} \right\rangle$$

* **Dense Dimension:** $\mathbf{v}_{\text{dense}} \in \mathbb{R}^{1024}$ (captures semantic mood, thematic resonance, and situational parallels).
* **Sparse Lexical Vector:** $\mathbf{v}_{\text{sparse}} \in \mathbb{R}^{|V|}$ (preserves exact proper nouns, character names, fantasy terminology, and weapon/item IDs).

### 3.2 Vector Storage Specification (LanceDB)
The vector store MUST be serverless and embedded directly into the workspace filesystem (storing data in columnar Lance format).

**Table Schema (`scenes`):**
* `scene_id` (String, Primary Key)
* `chapter_idx` (Integer)
* `scene_idx` (Integer)
* `epoch_id` (Integer)
* `characters_present` (List of Strings, indexed for metadata filtering)
* `summary_text` (String)
* `full_text` (String)
* `vector` (Vector[1024], Dense float32)
* `sparse_indices` (List of Integers)
* `sparse_values` (List of Float32)

### 3.3 Hybrid Scoring Formula
Given a query $q$ generated from the current scene beat:

$$S_{\text{hybrid}}(q, d) = \alpha \cdot \frac{\mathbf{q}_{\text{dense}} \cdot \mathbf{d}_{\text{dense}}}{\|\mathbf{q}_{\text{dense}}\| \|\mathbf{d}_{\text{dense}}\|} + (1 - \alpha) \cdot \sum_{t \in q \cap d} w_q(t) \cdot w_d(t)$$

Where $\alpha \in [0.0, 1.0]$ is the hybrid balance parameter (default: $\alpha = 0.6$).

### 3.4 Two-Stage Retrieval & Cross-Encoder Reranking
To eliminate irrelevant candidate noise and maximize LLM attention efficiency:

```plaintext
[ Current Scene Beat Query ]
              │
              ▼
┌──────────────────────────────┐
│ Stage 1: Hybrid Retrieval    │  (LanceDB Filter + Dense/Sparse Search)
│ Candidate Pool K = 30        │
└──────────────┬───────────────┘
              │
              ▼
┌──────────────────────────────┐
│ Stage 2: Cross-Encoder       │  (bge-reranker-v2-m3)
│ Reranking Pass               │
└──────────────┬───────────────┘
              │
              ▼
[ Top K_final = 3–5 Most Relevant Scenes ]
```

1. **Stage 1 (High Recall):** Fetch $K_{\text{cand}} = 30$ candidates via LanceDB with character metadata filters.
2. **Stage 2 (High Precision):** Pass $(q, d_i)$ pairs to `bge-reranker-v2-m3` cross-encoder.
3. **Selection:** Take top $K_{\text{final}} \in [3, 5]$ chunks (or maximum 8 chunks if token budget permits) to inject into the drafting prompt.

---

## 4. Component 3: Hierarchical Summarization Tree ($\mathcal{H}$)

To maintain awareness of the overall story arc without exceeding context window limits, the system maintains a 4-tier recursive summary tree:

```plaintext
                    ┌─────────────────────────┐
                    │    Tier 4: Book Syn.    │ (~800–1200 words)
                    └────────────▲────────────┘
                                 │ rollup
                    ┌────────────┴────────────┐
                    │    Tier 3: Arc Summ.    │ (~500–800 words / arc)
                    └────────────▲────────────┘
                                 │ rollup
                    ┌────────────┴────────────┐
                    │   Tier 2: Chap. Summ.   │ (~250–400 words / chap)
                    └────────────▲────────────┘
                                 │ rollup
                    ┌────────────┴────────────┐
                    │   Tier 1: Scene Summ.   │ (~100–150 words / scene)
                    └─────────────────────────┘
```

### 4.1 Resolution Tier Standards
* **Tier 1 (Scene Summary):** Generated immediately upon scene completion. Focuses on:
  * Entities present.
  * Concrete events and physical state deltas.
  * Emotional shifts and new secrets revealed.
* **Tier 2 (Chapter Summary):** Generated when all scenes in a chapter are finalized. Summarizes macro progression across scenes.
* **Tier 3 (Arc Summary):** Generated upon chapter boundary marking an arc climax or milestone (e.g., every 8–12 chapters).
* **Tier 4 (Book Synopsis):** High-level narrative state of the global universe and overall character arcs.

### 4.2 Injection Policy
When composing the context window for drafting Scene $N$:
* Inject **Book Synopsis** (Macro context).
* Inject **Current Arc Summary** (Meso context).
* Inject **Immediate Preceding Scene Summary ($N-1$)** (Micro continuity).
* Detailed past scenes are NOT pulled from raw text linearly; they are pulled selectively via Hybrid Retrieval (Section 3).

---

## 5. Component 4: 5-Step Scene Generation Orchestrator

The generation of each individual scene MUST strictly follow the 5-step entropy-reducing execution lifecycle:

```plaintext
[ User / AI Scene Beat ]
           │
           ▼
┌──────────────────────────────┐
│  Step 1: Outline Formulation │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Step 2: Context Assembly    │  ◄── SQLite Bible, LanceDB Hybrid, Summary Tree
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Step 3: Drafting LLM Pass   │  (Context Window: 32k–128k)
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Step 4: Consistency Check   │  ◄── Evaluator LLM vs. Hard Canon
└──────────┬───────────────────┘
           │ (Pass / Rectified)
           ▼
┌──────────────────────────────┐
│  Step 5: Fact Ingestion      │  ──► Update SQLite, LanceDB, & Summary Tree
└──────────────────────────────┘
```

### 5.1 Step 1: Outline Formulation
* The user or Creative Planner provides a high-level beat specification (e.g., *"Aria meets her uncle Kael at the sunken temple ruins to decipher the amulet, but discovers Kael is carrying an Imperial dagger"*).

### 5.2 Step 2: Context Assembly
The Context Builder deterministically queries:
1. **Story Bible Entities:** Query `characters` where `char_id IN ('char_aria', 'char_kael')`, `locations` for `loc_sunken_temple`, and `character_knowledge` for active beliefs.
2. **Open Plot Threads:** Query `plot_threads` where status is `OPEN` or `PROGRESSING` associated with Aria or the amulet.
3. **Previous Scene Micro-Summary:** Fetch Tier 1 summary of Scene $T-1$.
4. **Historical Scene Recall:** Execute Hybrid Search with Reranking to pull top 3 past scenes involving Aria and Kael.
5. **Macro Narrative State:** Fetch Tier 4 Book Synopsis + Tier 3 Arc Summary.

### 5.3 Step 3: Drafting LLM Pass
* The assembled context payload is structured with strict system prompts enforcing point of view (POV), tone, voice, and pacing.
* Model requirement: Context window of 32k to 128k tokens.
* Execution via Gemini API or OpenAI-compatible endpoint.

### 5.4 Step 4: Consistency Validation Pass
A secondary evaluator model receives:
* The drafted scene prose.
* The extracted Story Bible assertions (character eye color, living status, known secrets).
* Active plot thread constraints.

**Validation Rules:**
1. Did any character act upon knowledge they do not possess according to `character_knowledge`?
2. Are physical traits (eye color, scars, age) consistent with `characters`?
3. Did any deceased character perform active actions?
4. Did any established relationship dynamic violently invert without narrative justification?

If violations are detected, the Evaluator generates a structured patch prompt, and the Drafter performs an in-place revision before proceeding.

### 5.5 Step 5: Fact Ingestion & Memory Update
Once the scene passes consistency validation:
1. **Fact Extractor:** An extraction pass parses the finalized prose for:
   * Newly revealed facts $\to$ inserted into `character_knowledge` or updated in `characters`.
   * Location state changes $\to$ updated in `locations`.
   * Progress on plot promises $\to$ status updated in `plot_threads`.
2. **Vector Indexing:** The scene text and generated Tier 1 summary are embedded via BGE-M3 and indexed into the LanceDB `scenes` table.
3. **Tree Rollup:** The Tier 1 summary is committed to the Hierarchical Summary Tree, triggering chapter/arc rollups if boundary conditions are met.

---

## 6. Component 5: Distributed Compute & Remote Inference Strategy

To allow seamless operation on resource-constrained host machines (e.g., dual-core Celeron CPUs with 6 GB RAM), Novelis decouples orchestration from neural compute.

```plaintext
┌─────────────────────────────────┐           ┌─────────────────────────────────┐
│     Local Controller Engine     │           │   Remote Inference Service(s)   │
│  (Novelis Core on Local Host)   │           │   (Colab / Kaggle / Cloud API)  │
│                                 │           │                                 │
│  - SQLite Story Bible           │   HTTP    │  - LLM Drafting (Gemini API)    │
│  - LanceDB (File-based)         │──────────►│  - LLM Consistency (Gemini API)│
│  - FastEmbed ONNX (Lightweight) │           │  - Heavy Embedding / Reranker   │
│  - Pipeline Orchestration       │           │    (BGE-M3 & Reranker v2 on GPU)│
└─────────────────────────────────┘           └─────────────────────────────────┘
```

### 6.1 Inference Modes

#### Mode A: Full Cloud API (Pure Zero-Local-Weight)
* **LLM Engine:** Gemini 1.5 Pro / Flash or OpenAI-compatible endpoints via official REST APIs.
* **Embeddings & Reranker:** Lightweight FastEmbed ONNX for BGE-M3 locally, or remote embedding endpoints.
* **Local RAM Footprint:** $< 350\text{ MB}$.

#### Mode B: Hybrid Notebook Worker (Kaggle / Google Colab)
* An open-source model server (FastAPI + vLLM or HuggingFace Transformers) runs in a free GPU notebook environment (Kaggle / Google Colab with Cloudflare Tunnel or ngrok).
* The Local Novelis Controller transmits candidate text chunks to the Colab worker for heavy BGE-M3 dense/sparse embedding generation and Cross-Encoder reranking.
* The local machine retains full physical control of the SQLite Story Bible and project files.

### 6.2 Universal Remote Worker Protocol
Any remote worker MUST implement the standard JSON contract:

```http
POST /v1/embeddings/hybrid
Content-Type: application/json

{
  "texts": ["Scene chunk 1...", "Scene chunk 2..."],
  "model": "BAAI/bge-m3"
}
```

Response:
```json
{
  "dense_embeddings": [[0.012, -0.045, "..."]],
  "lexical_weights": [{"token_id_102": 0.42, "token_id_991": 0.81}]
}
```

---

## 7. Compliance & Verification Standards

Implementations of the Novelis Memory Subsystem MUST satisfy the following test criteria:

1. **Deterministic Bible Recall:** A query for a character's physical traits MUST return verbatim attributes from `characters.physical_traits` with 100% precision.
2. **Named Entity Hybrid Recall:** When querying a scene by a unique fantasy character name, Hybrid Search MUST score the correct scene higher than purely semantic queries that lack the character's name.
3. **Rollback Safety:** If Step 4 (Consistency Validation) aborts a scene, no records SHALL be permanently committed to `story_bible.db` or the LanceDB vector table.
