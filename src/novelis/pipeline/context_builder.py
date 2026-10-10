"""Step 2: Context Builder & Assembler
Assembles Hard Canon facts, past scenes, summaries, and open plot threads
per NSPEC-002 Section 5.2.
"""

from typing import List, Dict, Any, Optional
from novelis.memory.story_bible import StoryBible
from novelis.memory.hybrid_retrieval import HybridRetrievalEngine
from novelis.memory.summarizer import SummaryTreeManager


class ContextBuilder:
    """Deterministically compiles multi-tier context for the Drafting LLM."""

    def __init__(
        self,
        bible: StoryBible,
        retrieval: HybridRetrievalEngine,
        summarizer: SummaryTreeManager
    ):
        self.bible = bible
        self.retrieval = retrieval
        self.summarizer = summarizer

    def build_scene_context(
        self,
        scene_beat: str,
        character_ids: List[str],
        location_id: Optional[str] = None,
        chapter_idx: int = 1,
        scene_idx: int = 1
    ) -> Dict[str, Any]:
        """Assembles a comprehensive context dictionary ready for prompt synthesis."""

        # 1. Hard Canon: Characters profiles & knowledge scopes
        characters_data = []
        for cid in character_ids:
            char_prof = self.bible.get_character(cid)
            if char_prof:
                knowledge = self.bible.get_character_knowledge(cid)
                relations = self.bible.get_relations_for_character(cid)
                characters_data.append({
                    "profile": char_prof,
                    "known_facts": [k["proposition"] for k in knowledge],
                    "relations": relations
                })

        # 2. Hard Canon: Location details
        location_data = self.bible.get_location(location_id) if location_id else None

        # 3. Open Plot Threads (Chekhov's Guns)
        open_threads = self.bible.get_open_plot_threads(limit=5)

        # 4. Micro Continuity: Previous Scene Summary
        prev_scene_summary = self.summarizer.get_last_scene_summary() or "This is the opening scene."

        # 5. Macro Context: Book synopsis & Chapter summary
        book_synopsis = self.summarizer.get_book_synopsis()
        chapter_summary = self.summarizer.get_chapter_summary(chapter_idx)

        # 6. Episodic Soft Memory: Top 3 relevant historical scenes from LanceDB
        historical_scenes = self.retrieval.search_scenes(
            query=scene_beat,
            filter_characters=character_ids,
            top_k=3
        )

        return {
            "scene_beat": scene_beat,
            "chapter_idx": chapter_idx,
            "scene_idx": scene_idx,
            "characters": characters_data,
            "location": location_data,
            "open_plot_threads": open_threads,
            "previous_scene_summary": prev_scene_summary,
            "chapter_summary": chapter_summary,
            "book_synopsis": book_synopsis,
            "relevant_past_scenes": historical_scenes
        }

    def format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Formats assembled context into structured Markdown sections for Gemini 3.8."""
        sections = []

        # Macro Context
        if context.get("book_synopsis"):
            sections.append(f"### BOOK OVERVIEW\n{context['book_synopsis']}\n")

        # Continuity
        sections.append(
            f"### IMMEDIATE PRECEDING CONTEXT (SCENE CONTINUITY)\n"
            f"{context.get('previous_scene_summary')}\n"
        )

        # Active Characters (Hard Canon)
        char_texts = []
        for c in context.get("characters", []):
            prof = c["profile"]
            traits = prof.get("physical_traits", {})
            traits_str = ", ".join(f"{k}: {v}" for k, v in traits.items())
            known = "; ".join(c.get("known_facts", [])) or "No unique secret knowledge recorded."

            char_texts.append(
                f"- **{prof['canonical_name']} ({prof['char_id']})**:\n"
                f"  * Physical Traits (IMMUTABLE): {traits_str}\n"
                f"  * Core Motivation: {prof['core_motivation']}\n"
                f"  * Life Status: {prof['life_status']}\n"
                f"  * Known Facts (CANNOT ACT ON FACTS OUTSIDE THIS): {known}"
            )
        sections.append("### ACTIVE CHARACTERS (HARD CANON)\n" + "\n".join(char_texts) + "\n")

        # Setting
        loc = context.get("location")
        if loc:
            sections.append(
                f"### SETTING & LOCATION\n"
                f"- **{loc['name']}**\n"
                f"  * Environmental Conditions: {loc.get('environmental_conditions')}\n"
                f"  * Rules/Hazards: {loc.get('cultural_rules', 'None')}\n"
            )

        # Open Plot Threads
        threads = context.get("open_plot_threads", [])
        if threads:
            thread_lines = [f"- [{t['thread_id']}] {t['title']}: {t['description']}" for t in threads]
            sections.append("### ACTIVE PLOT THREADS (PROMISES TO MAINTAIN)\n" + "\n".join(thread_lines) + "\n")

        # Relevant Past Scenes
        past_scenes = context.get("relevant_past_scenes", [])
        if past_scenes:
            past_texts = []
            for ps in past_scenes:
                past_texts.append(
                    f"#### Excerpt from Chapter {ps.get('chapter_idx')}, Scene {ps.get('scene_idx')}:\n"
                    f"{ps.get('summary_text', '')}\n"
                )
            sections.append("### RELEVANT PAST SCENE EXCERPTS (MEMORY RETRIEVAL)\n" + "\n".join(past_texts))

        return "\n".join(sections)
