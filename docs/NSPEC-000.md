# NSPEC-000: Core Philosophy & Architectural Constitution

---
Document Status: Approved & Locked
Document Version: 1.1.0
NSPEC Compatibility:
minimum: 1.0
maximum: 1.x
API Compatibility:
minimum: 1.0
Owner: Product Experience & Engine Architecture Teams
Last Updated: 2026-08-05
Normative Standard: RFC 2119 Compliance
---

## Document Rules

This document is normative and defines the constitutional laws of the Novelis ecosystem.

Definitions in this document SHALL take precedence over all general documentation, second only to GLOSSARY.md.

Normative keywords MUST follow RFC 2119 (MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY, OPTIONAL).

All cross-references SHALL point to stable document identifiers (NSPEC, ADR, API-SPEC, GLOSSARY).

Any modification to this constitutional spec REQUIRES an approved RFC, compatibility impact analysis, and unanimous sign-off from both Engine and Product Experience Architects.

---

## Abstract

This document specifies the core philosophy, constitutional laws, immutable principles, and foundational constraints governing the Novelis Fiction Operating System (FOS). It establishes the primacy of story integrity, enforces the total separation between creative planning (Thinking) and VM execution (Executing), defines the 5-Layer Narrative Computing Stack, and locks the deterministic entropy reduction pipeline across all story build processes.

---

## 1. Core Definitions

To ensure strict alignment with GLOSSARY.md, the following core architectural layers and constructs are normatively anchored:

### Creative Layer
The isolated multi-agent subsystem responsible for synthesizing narrative goals, character arcs, and world building into structured blueprints.

### Compiler Layer
The deterministic subsystem responsible for parsing, validating, and translating narrative blueprints into canonical intermediate representations.

### Runtime Layer
The deterministic Virtual Machine responsible for executing scene graphs, managing state transitions, enforcing canon, and logging immutable events.

### Renderer Layer
The pluggable presentation subsystem responsible for transforming structured state representations into natural language literary prose.

### Canon
The single, immutable source of narrative truth representing all accepted facts, states, and history of the fictional world at a given Story Epoch.

---

## 2. Architectural Objectives

The Novelis ecosystem architecture exists to guarantee eight fundamental operational goals:

### Determinism
Identical inputs, blueprints, and seed states MUST yield identical structural state transitions.

### Explainability
Every narrative state transition MUST be traceable back to an explicit scene objective or event delta.

### Inspectability
Every intermediate artifact (Blueprint, DSL, CSIR, State Delta) MUST remain human-readable and machine-parseable.

### Reproducibility
Any historical state of a build MUST be exactingly replayed from the Transactional Event Store.

### Vendor Independence
Core engine execution MUST remain completely decoupled from underlying LLM vendors and model providers.

### Long Narrative Stability
State integrity MUST NOT degrade over long-form narrative spans (e.g., 100,000+ words).

### Human Override
Authors SHALL retain ultimate authority to inspect, pause, alter, or override any artifact or state decision.

### Future Compatibility
Evolution of specs and tools MUST preserve backward compatibility for historical build artifacts.

---

## 3. Constitutional Articles

### Article I: The Story-First Principle
The Story is the product. The Engine exists to preserve the Story. The Runtime VM exists to preserve the Engine. The Renderer exists to express the Story. No technical implementation detail, optimization, or vendor constraint SHALL take precedence over preserving narrative integrity and authorial intent.

### Article II: The Four-Layer Isolation Rule
The Novelis system architecture MUST enforce strict boundary isolation across four primary technical layers. Cross-layer domain leakage is strictly prohibited:

* **Creative Layer:** Responsible solely for formulating intent, themes, and goals. It MUST NOT emit execution VM instructions, database queries, or target word counts.
* **Compiler Layer:** Responsible solely for syntax validation, AST parsing, and CSIR generation. It MUST NOT alter narrative intent, emotional choices, or prose stylistic choices.
* **Runtime Layer:** Responsible solely for deterministic task-graph (DAG) execution, rule enforcement, and state delta commits. The Runtime Layer MUST NOT think creatively, revise character decisions, or make unguided narrative assumptions.
* **Renderer Layer:** Responsible solely for translating validated CSIR payloads into natural language prose. It MUST NOT alter Canon facts, revive dead characters, or manipulate world state variables.

### Article III: The Entropy Reduction Pipeline
The system SHALL treat novel generation as a monotonic entropy reduction process. Narrative ambiguity MUST strictly decrease as data moves down the stack:

$$H(\text{User Premise}) \gg H(\text{Story Blueprint}) > H(\text{CSIR}) > H(\text{Runtime State}) = 0$$

* **User Layer ($H \gg 0$):** High ambiguity raw prompts and emotional goals.
* **Creative Layer ($H > 0$):** Resolves creative trajectories into a validated, declarative Story Blueprint.
* **Compiler Layer ($H \to 0$):** Converts Story Blueprint into rigid, unambiguous CSIR payloads.
* **Runtime Layer ($H = 0$):** Executes state transitions with zero logical ambiguity.
* **Renderer Layer:** Re-introduces stylistic linguistic variance, but ZERO factual ambiguity regarding Canon.

### Article IV: The "Observe, Don't Infer" Interface Rule
The Product Experience Layer (Novelis Studio) MUST act as a purely reactive consumer of backend telemetry events. The UI SHALL NOT infer, guess, or synthesize execution states. All UI progress bars, node graphs, and conflict prompts MUST be directly driven by explicit telemetry events emitted over the Dual-Plane API.

### Article V: Vendor-Agnostic Engine Standard
The Core Runtime Engine MUST remain 100% agnostic to underlying LLM vendors (OpenAI, Anthropic, Local Open-Weights). Model-specific prompt formats, tags, and API conventions MUST be isolated inside pluggable Renderer Plugins via Capability Negotiation.

### Article VI: Evolution Without Fragmentation
System evolution MUST NOT fragment the ecosystem. All schema changes, spec upgrades, and pipeline modifications MUST preserve compatibility through explicit version anchoring, migration adapters, capability negotiation, and formal RFC approval processes.

### Article VII: The One Concept, One Name Governance
Every technical concept within the Novelis platform, specifications, and codebase MUST have exactly one official name and one normative definition registered in GLOSSARY.md. Alternative aliases or informal terms SHALL NOT be used in normative documentation.

---

## 4. Immutable Principles (What Must Never Change)

The following principles represent the untouchable foundation of Novelis. Altering any of these principles SHALL require creating a new major system architecture version (e.g., FOS 2.0):

### Canon Primacy
Canon is the single source of truth; no component may bypass or overwrite Canon without an explicit Event Store transaction.

### Runtime Determinism
The Runtime VM MUST execute deterministically without creative hallucination.

### Renderer Non-Mutation
The Renderer Layer MUST NOT mutate Canon facts, world variables, or character states.

### Creative Isolation
The Creative Layer MUST NOT execute Runtime VM logic or manipulate database state directly.

### Universal Inspectability
All Story States, CSIR payloads, and Event Logs MUST remain fully inspectable by humans and tools.

### Append-Only History
The Transactional Event Store MUST remain strictly append-only; historical events SHALL NOT be mutated or deleted.

---

## 5. Extension & Failure Philosophies

### 5.1 Extension Philosophy
* Plugins and extensions MAY add new pipeline capabilities, UI views, or rendering adapters.
* Plugins and extensions SHALL NOT weaken system guarantees or bypass the Rule Engine.
* Plugins and extensions SHALL NOT mutate core Runtime contracts or alter Canon without going through the formal API.

### 5.2 Failure Philosophy
The FOS ecosystem enforces a deterministic error handling philosophy across all components:

* **Fail Fast:** Detect and reject invalid inputs (syntax, rule violations, schema mismatches) at the earliest possible layer.
* **Fail Explicitly:** Every failure MUST produce an explicit, typed error payload containing context, step ID, and causal details.
* **Fail Recoverably:** System failures MUST allow safe rollback to the last valid Event Store Snapshot without corrupting project data.
* **Never Fail Silently:** Unexpected state transitions or unhandled exceptions MUST NEVER be swallowed or hidden from telemetry streams.

---

## 6. System Operating Modes Overview

To accommodate diverse authoring workflows, the Novelis ecosystem architecture supports multiple operating modes:

### Autonomous Mode (One-Click)
Executes the full build pipeline end-to-end autonomously, utilizing automated validation passes and self-healing loops.

### Interactive Mode (Co-Pilot)
Allows step-by-step author inspection, approval, conflict resolution, and manual artifact modification at defined breakpoints.

Detailed specifications for operating mode state transitions are defined in NSPEC-001 and API-SPEC.

---

## 7. Constitution Amendment Process

Any proposed amendment to this document MUST undergo formal governance review:

### RFC Submission
A formal RFC document MUST be submitted detailing the proposed constitutional change and rationale.

### Impact Analysis
An automated and manual compatibility analysis MUST verify the impact on existing specifications (NSPEC, API-SPEC).

### Consensus Requirement
Ratification REQUIRES unanimous approval from both Engine Architecture and Product Experience Architecture leads.

### Version Bump
Approved amendments SHALL trigger a Semantic Version bump of NSPEC-000.

---

## 8. Non-Goals

### Monolithic Prompting
Novelis is NOT a wrapper around single-prompt long-context window LLM calls.

### Interactive Chatbot
FOS is NOT a conversational chat system; it is a deterministic software compiler for fiction.

### Runtime Creativity
The Runtime VM SHALL NOT be granted creative freedom to alter the plot trajectory during execution.