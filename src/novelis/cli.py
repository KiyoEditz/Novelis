"""Novelis Command-Line Interface (CLI)
Provides project initialization, scene generation, inspection, and EPUB export.
"""

import sys
import argparse
from pathlib import Path
import json

from novelis.config import config
from novelis.memory.story_bible import StoryBible
from novelis.memory.hybrid_retrieval import HybridRetrievalEngine
from novelis.memory.summarizer import SummaryTreeManager
from novelis.llm.gemini_client import GeminiClient
from novelis.pipeline.orchestrator import SceneOrchestrator
from novelis.export.epub_exporter import EpubExporter


def cmd_init_bible(args):
    """Initializes SQLite Story Bible and data directories."""
    config.ensure_directories()
    bible = StoryBible()
    retrieval = HybridRetrievalEngine()
    summarizer = SummaryTreeManager()
    print("[Novelis] Successfully initialized Story Bible SQLite database & LanceDB!")
    print(f"  - Database: {config.STORY_BIBLE_PATH}")
    print(f"  - LanceDB:  {config.LANCEDB_DIR}")


def cmd_seed_sample(args):
    """Populates Story Bible with canonical sample entities (Aria & Kael)."""
    bible = StoryBible()
    config.ensure_directories()

    # 1. Characters
    bible.upsert_character(
        char_id="char_aria",
        canonical_name="Aria Valen",
        aliases=["The Silver Crow"],
        age=19,
        physical_traits={"eyes": "blue", "hair": "silver", "height": "165cm"},
        core_motivation="Uncover the conspiracy behind her father's exile without sparking a war.",
        life_status="ALIVE",
        epoch=0
    )
    bible.upsert_character(
        char_id="char_kael",
        canonical_name="Kaelen Vane",
        aliases=["Kael", "Uncle Kael"],
        age=44,
        physical_traits={"eyes": "grey", "hair": "dark grey", "scars": "burn scars across left arm"},
        core_motivation="Protect the surviving members of the Valen family at any cost.",
        life_status="ALIVE",
        epoch=0
    )

    # 2. Character Knowledge (Secrets)
    bible.add_knowledge(
        knowledge_id="kn_kael_01",
        char_id="char_kael",
        proposition="Kael holds the official imperial seal of the Grand Inquisitor.",
        learned_epoch=0,
        source_entity_id="system"
    )

    # 3. Location
    bible.upsert_location(
        loc_id="loc_sunken_temple",
        name="Sunken Temple Ruins",
        environmental_conditions={"climate": "damp cold", "hazard": "sulfur mist"},
        cultural_rules="Holy ground forbidden to imperial guards"
    )

    # 4. Relations
    bible.set_relation(
        source_char_id="char_aria",
        target_char_id="char_kael",
        relation_type="UNCLE_AND_NIECE",
        sentiment_score=0.4,
        trust_score=0.7,
        notes="Aria considers Kael her only surviving family.",
        epoch=0
    )

    # 5. Plot Thread
    bible.add_plot_thread(
        thread_id="thr_father_amulet",
        title="Mystery of Father's Amulet",
        description="Aria must decipher ancient inscriptions etched upon her father's heirloom amulet.",
        opened_epoch=0,
        payoff_condition="Aria discovers the cipher key in the imperial archives.",
        status="OPEN",
        associated_characters=["char_aria", "char_kael"]
    )

    print("[Novelis] Canonical sample data (Aria Valen & Kael) successfully seeded into Story Bible!")


def cmd_inspect_bible(args):
    """Inspects the contents of the Story Bible in terminal."""
    bible = StoryBible()
    aria = bible.get_character("char_aria")
    kael = bible.get_character("char_kael")
    threads = bible.get_open_plot_threads()

    print("=" * 60)
    print("NOVELIS STORY BIBLE INSPECTOR (HARD CANON)")
    print("=" * 60)
    if aria:
        print(f"Character: {aria['canonical_name']} ({aria['char_id']})")
        print(f"  Physical:  {aria['physical_traits']}")
        print(f"  Status:    {aria['life_status']}")
        print(f"  Motive:    {aria['core_motivation']}")
    if kael:
        print(f"\nCharacter: {kael['canonical_name']} ({kael['char_id']})")
        print(f"  Physical:  {kael['physical_traits']}")
        print(f"  Status:    {kael['life_status']}")
        kael_kn = bible.get_character_knowledge("char_kael")
        print(f"  Secrets:   {[k['proposition'] for k in kael_kn]}")

    print("\nACTIVE PLOT THREADS:")
    for t in threads:
        print(f"  - [{t['thread_id']}] {t['title']} ({t['status']}): {t['description']}")
    print("=" * 60)


def cmd_run_scene(args):
    """Executes a 5-step scene generation cycle."""
    beat = args.beat or "Aria meets Kael at the sunken temple ruins to examine the ancient amulet."
    chars = args.characters.split(",") if args.characters else ["char_aria", "char_kael"]
    loc = args.location or "loc_sunken_temple"

    # Initialize LLM Client if API key is provided
    llm = None
    if config.GEMINI_API_KEY:
        try:
            llm = GeminiClient()
            print(f"[Novelis] Using LLM: Google {config.GEMINI_MODEL}", flush=True)
        except Exception as e:
            print(f"[Warning] Failed to load Gemini: {e}. Falling back to mock simulation mode.", flush=True)
    else:
        print("[Info] GEMINI_API_KEY is not set. Running in mock simulation mode.", flush=True)

    orchestrator = SceneOrchestrator(llm_client=llm)

    print(f"\n[Novelis] Starting scene generation cycle...", flush=True)
    print(f"  Beat: {beat}", flush=True)
    print(f"  Characters: {chars}", flush=True)

    result = orchestrator.execute_scene(
        scene_id=args.scene_id or "scn_01_01",
        scene_beat=beat,
        character_ids=chars,
        location_id=loc,
        chapter_idx=args.chapter,
        scene_idx=args.scene,
        epoch_id=args.epoch
    )

    print("\n" + "=" * 60, flush=True)
    print("DRAFT PROSE OUTPUT:", flush=True)
    print("=" * 60, flush=True)
    print(result["prose"], flush=True)
    print("=" * 60, flush=True)
    print(f"Validation Status: {'PASSED' if result['passed_validation'] else 'VIOLATED'}", flush=True)
    print(f"Scene Summary (Tier 1): {result['summary']}", flush=True)


def cmd_export_epub(args):
    """Compiles scenes into an EPUB digital book."""
    output = Path(args.output or "dist/Novelis_Story.epub")
    title = args.title or "Solaris: Secret of the Hawk"
    author = args.author or "Novelis Author"

    bible = StoryBible()
    summarizer = SummaryTreeManager()

    exporter = EpubExporter(
        title=title,
        author=author,
        synopsis=summarizer.get_book_synopsis() or "A novel generated with the Novelis AI authoring system."
    )

    # Retrieve stored scenes from summary tree
    scenes = summarizer.data.get("scenes", {})
    if not scenes:
        # Fallback dummy chapter if no scenes exist yet
        exporter.add_chapter("Chapter 1: The Beginning", "Beneath a frozen sky, the journey began.\n\n* * *\n\nFootsteps echoed in the distance.", 1)
    else:
        for sid, sdata in scenes.items():
            chap_idx = sdata.get("chapter_idx", 1)
            exporter.add_chapter(f"Chapter {chap_idx}: {sid}", sdata.get("summary", ""), chap_idx)

    exported_path = exporter.export_to_file(output)
    print(f"[Novelis] Successfully exported novel to: {exported_path}")
    print(f"File size: {exported_path.stat().st_size} bytes")


def main():
    parser = argparse.ArgumentParser(description="Novelis Core CLI")
    subparsers = parser.add_subparsers(dest="command")

    # init-bible
    subparsers.add_parser("init-bible", help="Initialize Story Bible database and directories")

    # seed-sample
    subparsers.add_parser("seed-sample", help="Seed sample canonical entities (Aria & Kael)")

    # inspect-bible
    subparsers.add_parser("inspect-bible", help="Inspect Story Bible tables in console")

    # run-scene
    p_run = subparsers.add_parser("run-scene", help="Execute 5-step scene generation pipeline")
    p_run.add_argument("--beat", type=str, help="Narrative direction or beat for the scene")
    p_run.add_argument("--characters", type=str, default="char_aria,char_kael", help="Comma-separated character IDs")
    p_run.add_argument("--location", type=str, default="loc_sunken_temple", help="Location ID")
    p_run.add_argument("--chapter", type=int, default=1, help="Chapter number")
    p_run.add_argument("--scene", type=int, default=1, help="Scene index")
    p_run.add_argument("--epoch", type=int, default=1, help="Timeline epoch")
    p_run.add_argument("--scene-id", type=str, default="scn_01_01", help="Unique scene ID")

    # export-epub
    p_epub = subparsers.add_parser("export-epub", help="Export novel to EPUB format")
    p_epub.add_argument("--output", type=str, default="dist/Novel_Output.epub", help="Destination EPUB file path")
    p_epub.add_argument("--title", type=str, default="Solaris: Secret of the Hawk", help="Novel book title")
    p_epub.add_argument("--author", type=str, default="Novelis Author", help="Author name")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    commands = {
        "init-bible": cmd_init_bible,
        "seed-sample": cmd_seed_sample,
        "inspect-bible": cmd_inspect_bible,
        "run-scene": cmd_run_scene,
        "export-epub": cmd_export_epub,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
