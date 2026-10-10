# NSPEC-007: Renderer Layer, Prose Generation & Plugin Architecture

---
Document Status: Approved & Locked
Document Version: 1.0.0
NSPEC Compatibility:
  minimum: 1.0
  maximum: 1.x
API Compatibility:
  minimum: 1.0
  maximum: 1.x
Owner: Presentation Layer & Rendering Architecture Teams
Last Updated: 2026-10-10
Normative Standard: RFC 2119 Compliance
---

## Document Rules & Strict Hierarchy Law

This specification is normative and governs the architecture, plugin interfaces, prompt engineering strategies, capability negotiation protocols, and literary prose synthesis mechanisms of the **Renderer Layer** within the Novelis ecosystem.

All implementations MUST conform strictly to the definitions in `GLOSSARY.md` and the constitutional principles locked in `NSPEC-000`.

**Strict Downward-Only Document Dependency Law:**
This document depends solely upon `GLOSSARY.md`, `NSPEC-000`, `NSPEC-001`, `NSPEC-002`, `NSPEC-003`, `NSPEC-004`, `NSPEC-005`, and `NSPEC-006`. It SHALL NOT import or depend upon concepts defined in specifications positioned below it.

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
       [ NSPEC-005 ] (Autonomous Runtime VM Specification)
              │
              ▼
       [ NSPEC-006 ] (Rule Engine & Invariant Verification)
              │
              ▼
       [ NSPEC-007 ] (Renderer Layer & Prose Generation)  ◄── [Current Layer]
              │
              ▼
       [ API-SPEC Suite ] (Control, Telemetry & Data Planes)
```

---

## Abstract

This specification establishes the technical standard for the **Novelis Renderer Layer**. The Renderer Layer transforms validated, deterministic CSIR payloads into nuanced, high-caliber literary prose. While the earlier layers in the Narrative Computing Stack drive entropy to zero ($H = 0$) to eliminate factual ambiguity, the Renderer Layer re-introduces controlled linguistic, stylistic, and rhythmic variation without ever altering Canon facts. Through a modular plugin architecture and formal **Capability Negotiation**, the Renderer Layer abstracts LLM vendor differences (Gemini, Claude, OpenAI, and Local Open-Weights), ensuring complete vendor independence.

---

## 1. Constitutional Renderer Invariants

In accordance with `NSPEC-000 Article II` and `Article V`:

### Invariant I: The Non-Mutation Law
The Renderer Layer SHALL NOT mutate, forge, or re-interpret Canon facts, character attributes, or world state variables. It acts purely as a linguistic translator from structured CSIR specifications to natural language text.

### Invariant II: Vendor Decoupling
The core Runtime VM SHALL NOT contain vendor-specific prompt templates, tokenizers, or API drivers. All vendor interactions MUST be contained inside self-contained **Renderer Plugins**.

### Invariant III: Zero Unbounded Hallucination
The Renderer Layer MUST adhere strictly to the entities, locations, sensory cues, and dramatic contracts declared in the CSIR payload. It SHALL NOT introduce unscripted major characters or alter established plot turns.

---

## 2. Pluggable Architecture & Interface Definition

All Renderer Plugins MUST implement the universal Python/TypeScript `IRendererPlugin` interface:

```typescript
export interface IRendererPlugin {
  readonly pluginId: string;
  readonly vendorName: string;
  readonly supportedModelVersions: string[];

  // Capability Declaration
  getCapabilities(): CapabilityManifest;

  // Prompt Assembly & Execution
  renderScene(
    csir: CSIRPayload,
    context: AssembledMemoryContext,
    options: RenderOptions,
    onToken?: (token: string) => void
  ): Promise<RenderedProseOutput>;

  // Token & Cost Estimation
  estimateTokens(csir: CSIRPayload, context: AssembledMemoryContext): TokenEstimate;
}
```

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any

class BaseRendererPlugin(ABC):
    plugin_id: str
    vendor_name: str
    supported_models: list[str]

    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        """Returns the machine-readable capability manifest."""
        pass

    @abstractmethod
    async def render_scene_stream(
        self,
        csir: dict[str, Any],
        context: dict[str, Any],
        options: dict[str, Any]
    ) -> AsyncIterator[str]:
        """Streams generated prose tokens to the runtime caller."""
        pass
```

---

## 3. Capability Negotiation Protocol

Before dispatching a CSIR payload, the Runtime VM and the designated Renderer Plugin perform a **Capability Handshake**:

```plaintext
[ Runtime VM ]                                 [ Renderer Plugin ]
       │                                                │
       │─────── 1. Query Capabilities ─────────────────►│
       │                                                │
       │◄────── 2. Return Capability Manifest ──────────│
       │                                                │
       │─────── 3. Select Rendering Strategy ──────────►│
       │                                                │
       │─────── 4. Dispatch Render Request ────────────►│
```

### 3.1 Capability Manifest Schema
```json
{
  "plugin_id": "novelis-renderer-gemini",
  "vendor": "Google",
  "model": "gemini-3.8-flash",
  "context_window_tokens": 1048576,
  "supports_system_instructions": true,
  "supports_streaming": true,
  "supports_json_schema_mode": true,
  "preferred_context_envelope": "MARKDOWN_SECTIONS",
  "max_output_tokens": 8192
}
```

---

## 4. Vendor-Specific Rendering Strategies

Each Renderer Plugin encapsulates formatting optimizations tailored to specific LLM model families:

### 4.1 Gemini API Strategy (`MARKDOWN_SECTIONS`)
* Employs explicit Markdown headers with strict system instructions anchoring POV, voice, and sensory immersion.
* Leverages massive context windows (up to 1M+ tokens) to comfortably ingest high-resolution episodic memory and deep lore.

```markdown
# SYSTEM INSTRUCTION
You are the Prose Synthesis Engine for Novelis FOS. 
Render the scene specified below into vivid, literary prose.
Preserve third-person limited POV anchored exclusively to Aria Valen.
DO NOT introduce external characters. DO NOT resolve conflicts prematurely.

# SCENE SPECIFICATION (CSIR)
- Setting: The Sunken Scriptorium (Dusk, bitter sleet)
- Active POV: Aria Valen (distrustful, exhausted)
- Dramatic Objective: Extract encrypted ledger before patrol breach.
- Sensory Anchors: sulfur odor, freezing fingertips, boot crunches.

# EPISODIC CONTEXT (STORY BIBLE & PAST SCENES)
[Context Chunks...]
```

### 4.2 Claude Strategy (`XML_TAGS`)
* Encapsulates CSIR contracts and memory inside semantic XML tags:
```xml
<scene_directive>
  <pov character="char_aria" mode="THIRD_PERSON_LIMITED" />
  <objective>Extract encrypted ledger before patrol breach.</objective>
  <sensory_requirements>
    <cue>smell of burning sulfur and damp stone</cue>
    <cue>sound of boots crunching frost overhead</cue>
  </sensory_requirements>
</scene_directive>
<canon_constraints>
  <assertion>Kael's inquisitorial seal is hidden beneath his left cuff.</assertion>
  <assertion>Aria does not know Kael is an Inquisitor.</assertion>
</canon_constraints>
```

### 4.3 OpenAI & Local ChatML Strategy
* Structured system prompts with role tags (`system`, `developer`, `user`), with optional JSON/Structured Output constraints when generating beat-by-beat drafts.

---

## 5. Streaming & Live Telemetry Delivery

To support real-time visual feedback in Novelis Studio without polling, Renderer Plugins MUST support chunked streaming:

1. **Chunk Delivery:** Emits `renderer.token_stream` events over Server-Sent Events (SSE).
2. **Buffer Window:** Tokens are buffered in 50ms windows to reduce network packet overhead.
3. **Progress Tracking:** Reports real-time word count against the CSIR target word budget.

---

## 6. Output Normalization & Post-Processing

Before candidate prose is passed to the Rule Engine, the Renderer Layer applies deterministic post-processing:

1. **Tag Stripping:** Strips any unintended meta-commentary, markdown fences (````markdown ... ````), or model self-talk.
2. **Scene Delimiter Normalization:** Formats paragraph breaks, dialogue quotes, and scene divider glyphs (`* * *`) according to project typesetting standards.
3. **Word Budget Validation:** Calculates exact token and word counts, ensuring the output falls within the CSIR `min_word_count` and `max_word_count` thresholds.
