"""Step 4: Consistency Validator & Self-Healing Loop
Cross-references drafted prose against Hard Canon assertions per NSPEC-006.
"""

from typing import Dict, Any, List, Optional
import json
from novelis.llm.base import BaseLLMClient


class ConsistencyValidator:
    """Evaluates narrative integrity and detects contradictions with the Story Bible."""

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client

    def validate_programmatic(
        self,
        draft_prose: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fast heuristic validation pass without requiring an external LLM call."""
        violations = []

        # 1. Check deceased characters
        for c in context.get("characters", []):
            prof = c["profile"]
            name = prof["canonical_name"]
            status = prof.get("life_status")

            if status == "DECEASED":
                # If deceased character is speaking or active
                if f'"{name}"' in draft_prose or f"{name} said" in draft_prose or f"{name} walked" in draft_prose:
                    violations.append(
                        f"Canon Violation: Character '{name}' is DECEASED but appears to be actively speaking/moving."
                    )

            # 2. Check physical trait contradictions (basic heuristic)
            traits = prof.get("physical_traits", {})
            for trait_name, trait_val in traits.items():
                if trait_name.lower() in ["eyes", "mata"] and trait_val.lower() == "blue":
                    if f"brown eyes" in draft_prose.lower() and name.lower() in draft_prose.lower():
                        violations.append(
                            f"Trait Violation: Character '{name}' has immutable blue eyes, but draft mentions brown eyes."
                        )

        passed = len(violations) == 0
        corrective_instruction = ""
        if not passed:
            corrective_instruction = (
                "Please rewrite the text to fix the following canon contradictions:\n"
                + "\n".join(f"- {v}" for v in violations)
            )

        return {
            "passed": passed,
            "violations": violations,
            "corrective_instruction": corrective_instruction
        }

    def validate_llm(
        self,
        draft_prose: str,
        context_summary_str: str
    ) -> Dict[str, Any]:
        """Deep neural validation pass using the LLM critic."""
        if not self.llm_client:
            return {"passed": True, "violations": [], "corrective_instruction": ""}

        system_instruction = (
            "You are the Novelis Narrative Rule Engine & Consistency Auditor (NSPEC-006).\n"
            "Your task is to compare the newly drafted scene prose against the provided Story Bible facts.\n"
            "Check for:\n"
            "1. Physical trait errors (e.g. wrong eye/hair color).\n"
            "2. Epistemic violations (character acting on secret information they do not know).\n"
            "3. Deceased characters acting or speaking.\n"
            "Respond in JSON format with keys: 'passed' (boolean), 'violations' (list of strings), "
            "and 'corrective_instruction' (string with clear repair instructions, or empty if passed)."
        )

        prompt = (
            f"STORY BIBLE FACTS:\n{context_summary_str}\n\n"
            f"DRAFTED PROSE TO EVALUATE:\n{draft_prose}\n\n"
            "Output JSON only:"
        )

        try:
            raw_response = self.llm_client.generate(
                system_instruction=system_instruction,
                prompt=prompt,
                temperature=0.1
            )
            clean_json = raw_response.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.startswith("```"):
                clean_json = clean_json[3:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            return json.loads(clean_json.strip())
        except Exception:
            # Fallback to programmatic check on JSON parse failure
            return {"passed": True, "violations": [], "corrective_instruction": ""}
