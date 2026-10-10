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
    print("[Novelis] Inisialisasi basis data Story Bible & LanceDB berhasil!")
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
        core_motivation="Membongkar konspirasi pengasingan ayahnya tanpa memicu perang.",
        life_status="ALIVE",
        epoch=0
    )
    bible.upsert_character(
        char_id="char_kael",
        canonical_name="Kaelen Vane",
        aliases=["Kael", "Paman Kael"],
        age=44,
        physical_traits={"eyes": "grey", "hair": "dark grey", "scars": "bekas luka bakar di lengan kiri"},
        core_motivation="Melindungi sisa keluarga Valen dengan cara apa pun.",
        life_status="ALIVE",
        epoch=0
    )

    # 2. Character Knowledge (Secrets)
    bible.add_knowledge(
        knowledge_id="kn_kael_01",
        char_id="char_kael",
        proposition="Kael memegang segel resmi Grand Inquisitor Kekaisaran.",
        learned_epoch=0,
        source_entity_id="system"
    )

    # 3. Location
    bible.upsert_location(
        loc_id="loc_sunken_temple",
        name="Reruntuhan Kuil Bawah Tanah",
        environmental_conditions={"climate": "dingin lembap", "hazard": "kabut belerang"},
        cultural_rules="Tanah suci terlarang bagi pengawal kekaisaran"
    )

    # 4. Relations
    bible.set_relation(
        source_char_id="char_aria",
        target_char_id="char_kael",
        relation_type="PAMAN_DAN_KEPONAKAN",
        sentiment_score=0.4,
        trust_score=0.7,
        notes="Aria menganggap Kael sebagai satu-satunya keluarga yang tersisa.",
        epoch=0
    )

    # 5. Plot Thread
    bible.add_plot_thread(
        thread_id="thr_father_amulet",
        title="Rahasia Amulet Ayah",
        description="Aria harus membaca inskripsi kuno pada amulet peninggalan ayahnya.",
        opened_epoch=0,
        payoff_condition="Aria menemukan kunci kode di perpustakaan kekaisaran.",
        status="OPEN",
        associated_characters=["char_aria", "char_kael"]
    )

    print("[Novelis] Data contoh karakter (Aria Valen & Kael) berhasil dimasukkan ke Story Bible!")


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
        print(f"Karakter: {aria['canonical_name']} ({aria['char_id']})")
        print(f"  Fisik:  {aria['physical_traits']}")
        print(f"  Status: {aria['life_status']}")
        print(f"  Motif:  {aria['core_motivation']}")
    if kael:
        print(f"\nKarakter: {kael['canonical_name']} ({kael['char_id']})")
        print(f"  Fisik:  {kael['physical_traits']}")
        print(f"  Status: {kael['life_status']}")
        kael_kn = bible.get_character_knowledge("char_kael")
        print(f"  Rahasia: {[k['proposition'] for k in kael_kn]}")

    print("\nPLOT THREADS AKTIF:")
    for t in threads:
        print(f"  - [{t['thread_id']}] {t['title']} ({t['status']}): {t['description']}")
    print("=" * 60)


def cmd_run_scene(args):
    """Executes a 5-step scene generation cycle."""
    beat = args.beat or "Aria bertemu Kael di reruntuhan kuil untuk memeriksa amulet kuno."
    chars = args.characters.split(",") if args.characters else ["char_aria", "char_kael"]
    loc = args.location or "loc_sunken_temple"

    # Inisialisasi LLM Client jika API key tersedia
    llm = None
    if config.GEMINI_API_KEY:
        try:
            llm = GeminiClient()
            print(f"[Novelis] Menggunakan LLM: Google {config.GEMINI_MODEL}")
        except Exception as e:
            print(f"[Peringatan] Gagal memuat Gemini: {e}. Menggunakan mode simulasi mock.")
    else:
        print("[Info] GEMINI_API_KEY tidak disetel. Menjalankan dalam mode simulasi mock.")

    orchestrator = SceneOrchestrator(llm_client=llm)

    print(f"\n[Novelis] Memulai eksekusi adegan...")
    print(f"  Beat: {beat}")
    print(f"  Karakter: {chars}")

    result = orchestrator.execute_scene(
        scene_id=args.scene_id or "scn_01_01",
        scene_beat=beat,
        character_ids=chars,
        location_id=loc,
        chapter_idx=args.chapter,
        scene_idx=args.scene,
        epoch_id=args.epoch
    )

    print("\n" + "=" * 60)
    print("HASIL DRAF PROSA ADEGAN:")
    print("=" * 60)
    print(result["prose"])
    print("=" * 60)
    print(f"Status Validasi: {'LOLOS' if result['passed_validation'] else 'DILANGGAR'}")
    print(f"Ringkasan Adegan (Tier 1): {result['summary']}")


def cmd_export_epub(args):
    """Compiles scenes into an EPUB digital book."""
    output = Path(args.output or "dist/Novelis_Story.epub")
    title = args.title or "Solaris: Rahasia Sang Elang"
    author = args.author or "Novelis Author"

    bible = StoryBible()
    summarizer = SummaryTreeManager()

    exporter = EpubExporter(
        title=title,
        author=author,
        synopsis=summarizer.get_book_synopsis() or "Sebuah novel yang dihasilkan melalui sistem Novelis FOS."
    )

    # Ambil adegan yang tersimpan dari summary tree atau query
    scenes = summarizer.data.get("scenes", {})
    if not scenes:
        # Fallback dummy chapter jika belum ada adegan
        exporter.add_chapter("Bab 1: Awal Mula", "Di bawah langit yang beku, perjalanan dimulai.\n\n* * *\n\nLangkah kaki terdengar di kejauhan.", 1)
    else:
        for sid, sdata in scenes.items():
            chap_idx = sdata.get("chapter_idx", 1)
            exporter.add_chapter(f"Bab {chap_idx}: {sid}", sdata.get("summary", ""), chap_idx)

    exported_path = exporter.export_to_file(output)
    print(f"[Novelis] Berhasil mengekspor buku ke: {exported_path}")
    print(f"Ukuran file: {exported_path.stat().st_size} bytes")


def main():
    parser = argparse.ArgumentParser(description="Novelis Core CLI")
    subparsers = parser.add_subparsers(dest="command")

    # init-bible
    subparsers.add_parser("init-bible", help="Inisialisasi database Story Bible")

    # seed-sample
    subparsers.add_parser("seed-sample", help="Masukkan data contoh Aria & Kael")

    # inspect-bible
    subparsers.add_parser("inspect-bible", help="Periksa isi tabel Story Bible")

    # run-scene
    p_run = subparsers.add_parser("run-scene", help="Jalankan pembuatan adegan 5-langkah")
    p_run.add_argument("--beat", type=str, help="Arahan adegan (scene beat)")
    p_run.add_argument("--characters", type=str, default="char_aria,char_kael", help="ID karakter pemisah koma")
    p_run.add_argument("--location", type=str, default="loc_sunken_temple")
    p_run.add_argument("--chapter", type=int, default=1)
    p_run.add_argument("--scene", type=int, default=1)
    p_run.add_argument("--epoch", type=int, default=1)
    p_run.add_argument("--scene-id", type=str, default="scn_01_01")

    # export-epub
    p_epub = subparsers.add_parser("export-epub", help="Ekspor novel ke format EPUB")
    p_epub.add_argument("--output", type=str, default="dist/Novel_Output.epub")
    p_epub.add_argument("--title", type=str, default="Solaris: Rahasia Sang Elang")
    p_epub.add_argument("--author", type=str, default="Novelis Author")

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
