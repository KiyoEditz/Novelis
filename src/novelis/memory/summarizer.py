"""Novelis Hierarchical Summarization Tree Manager
Maintains multi-resolution story awareness (Scene -> Chapter -> Arc -> Book)
per NSPEC-002 Section 4.
"""

from pathlib import Path
import json
from typing import Dict, Any, Optional
from novelis.config import config


class SummaryTreeManager:
    """Manages the 4-tier hierarchical summary tree, preventing context window
    saturation across long novels (50,000–100,000+ words).
    """

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or (config.DATA_DIR / "summary_tree.json")
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.data: Dict[str, Any] = {
            "book_synopsis": "",
            "arcs": {},
            "chapters": {},
            "scenes": {},
            "ordered_scenes": []  # List of scene_ids in temporal order
        }
        self.load()

    def load(self) -> None:
        """Loads summary tree from JSON disk storage."""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                pass

    def save(self) -> None:
        """Persists summary tree to JSON disk storage."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    # -------------------------------------------------------------------------
    # Tier 1: Scene Summaries
    # -------------------------------------------------------------------------

    def add_scene_summary(
        self,
        scene_id: str,
        chapter_idx: int,
        scene_idx: int,
        summary_text: str,
        epoch_id: int
    ) -> None:
        """Records a completed scene summary (Tier 1: ~100–150 words)."""
        self.data["scenes"][scene_id] = {
            "chapter_idx": chapter_idx,
            "scene_idx": scene_idx,
            "summary": summary_text,
            "epoch_id": epoch_id
        }
        if scene_id not in self.data["ordered_scenes"]:
            self.data["ordered_scenes"].append(scene_id)
        self.save()

    def get_scene_summary(self, scene_id: str) -> Optional[str]:
        """Returns the summary text of a specific scene."""
        scene = self.data["scenes"].get(scene_id)
        return scene["summary"] if scene else None

    def get_last_scene_summary(self) -> Optional[str]:
        """Returns the summary text of the immediately preceding scene."""
        if not self.data["ordered_scenes"]:
            return None
        last_id = self.data["ordered_scenes"][-1]
        return self.get_scene_summary(last_id)

    # -------------------------------------------------------------------------
    # Tier 2: Chapter Summaries
    # -------------------------------------------------------------------------

    def set_chapter_summary(self, chapter_idx: int, summary_text: str) -> None:
        """Sets or rolls up a chapter summary (Tier 2: ~250–400 words)."""
        self.data["chapters"][str(chapter_idx)] = summary_text
        self.save()

    def get_chapter_summary(self, chapter_idx: int) -> Optional[str]:
        """Returns the summary of a specific chapter."""
        return self.data["chapters"].get(str(chapter_idx))

    # -------------------------------------------------------------------------
    # Tier 3 & Tier 4: Arc & Book Summaries
    # -------------------------------------------------------------------------

    def set_arc_summary(self, arc_id: str, summary_text: str) -> None:
        """Sets an arc-level summary (Tier 3: ~500–800 words)."""
        self.data["arcs"][arc_id] = summary_text
        self.save()

    def get_arc_summary(self, arc_id: str) -> Optional[str]:
        return self.data["arcs"].get(arc_id)

    def set_book_synopsis(self, synopsis: str) -> None:
        """Sets the global book synopsis (Tier 4: ~800–1200 words)."""
        self.data["book_synopsis"] = synopsis
        self.save()

    def get_book_synopsis(self) -> str:
        return self.data.get("book_synopsis", "")
