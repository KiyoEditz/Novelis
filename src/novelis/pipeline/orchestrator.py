"""Novelis 5-Step Scene Orchestration Engine
Implements the end-to-end execution lifecycle per NSPEC-002 Section 5:
Step 1: Outline -> Step 2: Retrieve -> Step 3: Draft -> Step 4: Validate -> Step 5: Ingest.
"""

from typing import Dict, Any, List, Optional
from novelis.memory.story_bible import StoryBible
from novelis.memory.hybrid_retrieval import HybridRetrievalEngine
from novelis.memory.summarizer import SummaryTreeManager
from novelis.llm.base import BaseLLMClient
from novelis.pipeline.context_builder import ContextBuilder
from novelis.pipeline.validator import ConsistencyValidator
from novelis.pipeline.extractor import FactExtractor


class SceneOrchestrator:
    """Coordinates deterministic scene generation and consistency safeguarding."""

    def __init__(
        self,
        bible: Optional[StoryBible] = None,
        retrieval: Optional[HybridRetrievalEngine] = None,
        summarizer: Optional[SummaryTreeManager] = None,
        llm_client: Optional[BaseLLMClient] = None
    ):
        self.bible = bible or StoryBible()
        self.retrieval = retrieval or HybridRetrievalEngine()
        self.summarizer = summarizer or SummaryTreeManager()
        self.llm_client = llm_client

        self.context_builder = ContextBuilder(self.bible, self.retrieval, self.summarizer)
        self.validator = ConsistencyValidator(self.llm_client)
        self.extractor = FactExtractor(self.llm_client)

    def execute_scene(
        self,
        scene_id: str,
        scene_beat: str,
        character_ids: List[str],
        location_id: Optional[str] = None,
        chapter_idx: int = 1,
        scene_idx: int = 1,
        epoch_id: int = 1,
        max_repair_attempts: int = 3
    ) -> Dict[str, Any]:
        """Executes the complete 5-step scene lifecycle."""

        # -------------------------------------------------------------
        # STEP 1: Outline Formulation (Received via parameters)
        # -------------------------------------------------------------

        # -------------------------------------------------------------
        # STEP 2: Context Assembly (Hard Canon + Past Chunks + Tree)
        # -------------------------------------------------------------
        context = self.context_builder.build_scene_context(
            scene_beat=scene_beat,
            character_ids=character_ids,
            location_id=location_id,
            chapter_idx=chapter_idx,
            scene_idx=scene_idx
        )
        context_prompt_text = self.context_builder.format_context_for_prompt(context)

        # -------------------------------------------------------------
        # STEP 3 & STEP 4: Drafting & Consistency Validation Loop
        # -------------------------------------------------------------
        system_instruction = (
            "You are the Prose Synthesis Engine for Novelis FOS.\n"
            "Render the requested scene into vivid, immersive, high-caliber literary prose.\n"
            "Rules:\n"
            "1. Adhere strictly to the Hard Canon character traits and knowledge bounds provided.\n"
            "2. Do NOT introduce unscripted major characters.\n"
            "3. Ground sensory details in the setting.\n"
            "4. Do NOT include markdown code blocks around your novel prose."
        )

        repair_instructions = ""
        final_prose = ""
        passed = False
        attempt = 0

        while attempt < max_repair_attempts and not passed:
            attempt += 1

            # Build prompt (including repair guidance if self-healing)
            user_prompt = (
                f"SCENE BEAT GOAL:\n{scene_beat}\n\n"
                f"{context_prompt_text}\n\n"
            )
            if repair_instructions:
                user_prompt += f"CORRECTIVE INSTRUCTIONS FROM PREVIOUS REVISION:\n{repair_instructions}\n\n"

            user_prompt += "Write the complete scene prose now:"

            # Execute generation (or fallback mock if no LLM configured)
            if self.llm_client:
                draft_prose = self.llm_client.generate(system_instruction, user_prompt, temperature=0.7)
            else:
                draft_prose = (
                    f"The air was thick with tension in the chamber. Aria glanced at the frozen doorway, "
                    f"her blue eyes scanning the shadows. Based on the directive: '{scene_beat}', the task began."
                )

            # Step 4: Consistency Check
            # Fast heuristic check first, followed by neural check if LLM is active
            heuristic_eval = self.validator.validate_programmatic(draft_prose, context)
            if not heuristic_eval["passed"]:
                repair_instructions = heuristic_eval["corrective_instruction"]
                continue

            if self.llm_client:
                llm_eval = self.validator.validate_llm(draft_prose, context_prompt_text)
                if not llm_eval.get("passed", True):
                    repair_instructions = llm_eval.get("corrective_instruction", "")
                    continue

            passed = True
            final_prose = draft_prose

        if not passed:
            # Fallback if healing exhausted: preserve last generated draft but record warning
            final_prose = draft_prose

        # -------------------------------------------------------------
        # STEP 5: Fact Ingestion & Memory Update
        # -------------------------------------------------------------
        deltas = self.extractor.extract_deltas_and_summary(final_prose, scene_beat, character_ids)
        scene_summary = deltas.get("scene_summary", scene_beat)

        # Update SQLite Story Bible
        for idx, kn in enumerate(deltas.get("new_knowledge", [])):
            cid = kn.get("char_id")
            prop = kn.get("proposition")
            if cid and prop:
                self.bible.add_knowledge(
                    knowledge_id=f"kn_{scene_id}_{idx}",
                    char_id=cid,
                    proposition=prop,
                    learned_epoch=epoch_id,
                    source_entity_id=scene_id
                )

        for pt in deltas.get("plot_thread_updates", []):
            tid = pt.get("thread_id")
            st = pt.get("status")
            if tid and st:
                self.bible.update_plot_thread_status(tid, st)

        # Record timeline event in Story Bible
        self.bible.record_timeline_event(
            event_id=f"evt_{scene_id}",
            epoch_id=epoch_id,
            chapter_idx=chapter_idx,
            scene_idx=scene_idx,
            summary=scene_summary,
            state_delta=deltas
        )

        # Update LanceDB vector index
        self.retrieval.index_scene(
            scene_id=scene_id,
            chapter_idx=chapter_idx,
            scene_idx=scene_idx,
            epoch_id=epoch_id,
            characters_present=character_ids,
            summary_text=scene_summary,
            full_text=final_prose
        )

        # Update Hierarchical Summary Tree
        self.summarizer.add_scene_summary(
            scene_id=scene_id,
            chapter_idx=chapter_idx,
            scene_idx=scene_idx,
            summary_text=scene_summary,
            epoch_id=epoch_id
        )

        return {
            "scene_id": scene_id,
            "chapter_idx": chapter_idx,
            "scene_idx": scene_idx,
            "epoch_id": epoch_id,
            "prose": final_prose,
            "summary": scene_summary,
            "attempts": attempt,
            "passed_validation": passed,
            "extracted_deltas": deltas
        }
