"""Step 5: Fact Extractor & State Ingestion
Extracts newly revealed narrative facts, updates character knowledge,
and generates Tier 1 scene summaries per NSPEC-002 Section 5.5.
"""

from typing import Dict, Any, List, Optional
import json
from novelis.llm.base import BaseLLMClient


class FactExtractor:
    """Analyzes approved scene prose to extract state deltas and summaries."""

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client

    def extract_deltas_and_summary(
        self,
        scene_prose: str,
        scene_beat: str,
        active_characters: List[str]
    ) -> Dict[str, Any]:
        """Extracts new character knowledge, plot thread updates, and scene summary."""
        if self.llm_client:
            return self._extract_with_llm(scene_prose, scene_beat, active_characters)
        return self._extract_heuristic(scene_prose, scene_beat, active_characters)

    def _extract_with_llm(
        self,
        scene_prose: str,
        scene_beat: str,
        active_characters: List[str]
    ) -> Dict[str, Any]:
        """Extracts state deltas using LLM prompt."""
        system_instruction = (
            "You are the Novelis Fact Extraction Engine (NSPEC-002).\n"
            "Analyze the finalized scene text and extract:\n"
            "1. 'scene_summary': Concise summary (100-150 words) of key actions, discoveries, and state changes.\n"
            "2. 'new_knowledge': List of objects [{'char_id': str, 'proposition': str}] for any secret or new fact revealed to a character.\n"
            "3. 'plot_thread_updates': List of objects [{'thread_id': str, 'status': 'PROGRESSING' | 'RESOLVED'}].\n"
            "Respond in JSON format only."
        )

        prompt = (
            f"SCENE BEAT OBJECTIVE: {scene_beat}\n"
            f"ACTIVE CHARACTERS: {', '.join(active_characters)}\n\n"
            f"FINALIZED PROSE:\n{scene_prose}\n\n"
            "Output JSON only:"
        )

        try:
            raw = self.llm_client.generate(system_instruction, prompt, temperature=0.2)
            clean_json = raw.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.startswith("```"):
                clean_json = clean_json[3:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            return json.loads(clean_json.strip())
        except Exception:
            return self._extract_heuristic(scene_prose, scene_beat, active_characters)

    def _extract_heuristic(
        self,
        scene_prose: str,
        scene_beat: str,
        active_characters: List[str]
    ) -> Dict[str, Any]:
        """Fallback deterministic extractor without external LLM."""
        words = scene_prose.split()
        summary = " ".join(words[:120]) + ("..." if len(words) > 120 else "")

        return {
            "scene_summary": f"In this scene based on beat '{scene_beat}': {summary}",
            "new_knowledge": [],
            "plot_thread_updates": []
        }
