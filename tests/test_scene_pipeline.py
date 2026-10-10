"""Integration Tests for the 5-Step Scene Orchestration Pipeline
"""

import pytest
import tempfile
from pathlib import Path
from novelis.memory.story_bible import StoryBible
from novelis.memory.hybrid_retrieval import HybridRetrievalEngine
from novelis.memory.summarizer import SummaryTreeManager
from novelis.pipeline.validator import ConsistencyValidator
from novelis.pipeline.orchestrator import SceneOrchestrator


@pytest.fixture
def pipeline_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        db_path = tmp_path / "test_bible.db"
        lance_dir = tmp_path / "test_lancedb"
        tree_file = tmp_path / "test_summary.json"

        bible = StoryBible(db_path=db_path)
        retrieval = HybridRetrievalEngine(db_dir=lance_dir)
        summarizer = SummaryTreeManager(file_path=tree_file)

        # Seed initial characters
        bible.upsert_character(
            char_id="char_aria",
            canonical_name="Aria Valen",
            physical_traits={"eyes": "blue", "hair": "silver"},
            core_motivation="Uncover the truth",
            life_status="ALIVE"
        )
        bible.upsert_character(
            char_id="char_ghost",
            canonical_name="Lord Cassian",
            physical_traits={},
            core_motivation="Guardian of the tomb",
            life_status="DECEASED"
        )

        yield {
            "bible": bible,
            "retrieval": retrieval,
            "summarizer": summarizer
        }


def test_validator_detects_deceased_character(pipeline_env):
    """Verifies that the validator flags deceased characters attempting active dialogue."""
    validator = ConsistencyValidator()
    context = {
        "characters": [
            {"profile": pipeline_env["bible"].get_character("char_ghost")}
        ]
    }

    flawed_prose = 'Lord Cassian walked toward the altar and said, "You are late."'
    result = validator.validate_programmatic(flawed_prose, context)
    assert result["passed"] is False
    assert any("DECEASED" in v for v in result["violations"])


def test_orchestrator_5_step_execution(pipeline_env):
    """Verifies end-to-end 5-step scene generation lifecycle with mock execution."""
    orchestrator = SceneOrchestrator(
        bible=pipeline_env["bible"],
        retrieval=pipeline_env["retrieval"],
        summarizer=pipeline_env["summarizer"],
        llm_client=None  # Runs deterministic mock fallback
    )

    result = orchestrator.execute_scene(
        scene_id="scn_test_01",
        scene_beat="Aria inspects the stone engravings at the ancient temple.",
        character_ids=["char_aria"],
        chapter_idx=1,
        scene_idx=1,
        epoch_id=1
    )

    assert result["scene_id"] == "scn_test_01"
    assert result["passed_validation"] is True
    assert "Aria" in result["prose"]
    assert result["summary"] != ""

    # Verify Story Bible recorded the event
    assert pipeline_env["summarizer"].get_scene_summary("scn_test_01") is not None
