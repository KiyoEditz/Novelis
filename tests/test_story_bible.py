"""Unit Tests for Novelis Story Bible (SQLite Hard Canon Engine)
"""

import pytest
import tempfile
from pathlib import Path
from novelis.memory.story_bible import StoryBible


@pytest.fixture
def temp_bible():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_story_bible.db"
        bible = StoryBible(db_path=db_path)
        yield bible


def test_character_upsert_and_retrieval(temp_bible):
    """Verifies that characters can be inserted and retrieved with structured traits."""
    temp_bible.upsert_character(
        char_id="char_aria",
        canonical_name="Aria Valen",
        aliases=["The Silver Crow"],
        age=19,
        physical_traits={"eyes": "blue", "hair": "silver"},
        core_motivation="Membongkar konspirasi pengasingan ayahnya",
        life_status="ALIVE",
        epoch=1
    )

    aria = temp_bible.get_character("char_aria")
    assert aria is not None
    assert aria["canonical_name"] == "Aria Valen"
    assert aria["physical_traits"]["eyes"] == "blue"
    assert aria["physical_traits"]["hair"] == "silver"
    assert aria["life_status"] == "ALIVE"
    assert "The Silver Crow" in aria["aliases"]


def test_character_knowledge_scope(temp_bible):
    """Verifies epistemic containment (recording what a character knows/believes)."""
    temp_bible.upsert_character(
        char_id="char_kael",
        canonical_name="Kaelen Vane",
        physical_traits={"eyes": "grey"},
        core_motivation="Melindungi keluarga",
        life_status="ALIVE"
    )

    temp_bible.add_knowledge(
        knowledge_id="kn_01",
        char_id="char_kael",
        proposition="Kael memiliki segel Grand Inquisitor",
        learned_epoch=1,
        source_entity_id="system"
    )

    knowledge = temp_bible.get_character_knowledge("char_kael")
    assert len(knowledge) == 1
    assert knowledge[0]["proposition"] == "Kael memiliki segel Grand Inquisitor"


def test_relations_and_plot_threads(temp_bible):
    """Verifies relational matrix edges and plot thread tracking."""
    temp_bible.upsert_character("char_a", "Alpha", {}, "Motif A")
    temp_bible.upsert_character("char_b", "Beta", {}, "Motif B")

    temp_bible.set_relation(
        source_char_id="char_a",
        target_char_id="char_b",
        relation_type="ALLY",
        sentiment_score=0.8,
        trust_score=0.9,
        epoch=1
    )

    rels = temp_bible.get_relations_for_character("char_a")
    assert len(rels) == 1
    assert rels[0]["trust_score"] == 0.9

    temp_bible.add_plot_thread(
        thread_id="thr_01",
        title="Rahasia Pedang Tua",
        description="Pedang itu harus diasah dengan air suci",
        opened_epoch=1,
        payoff_condition="Pedang diasah di kuil",
        status="OPEN"
    )

    threads = temp_bible.get_open_plot_threads()
    assert len(threads) == 1
    assert threads[0]["thread_id"] == "thr_01"

    temp_bible.update_plot_thread_status("thr_01", "RESOLVED")
    open_threads = temp_bible.get_open_plot_threads()
    assert len(open_threads) == 0
