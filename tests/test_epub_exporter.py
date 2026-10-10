"""Unit Tests for Novelis EPUB Exporter Subsystem
"""

import pytest
import tempfile
import zipfile
from pathlib import Path
from novelis.export.epub_exporter import EpubExporter


def test_epub_generation():
    """Verifies that EpubExporter generates a valid EPUB3 container with proper chapters."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_book.epub"

        exporter = EpubExporter(
            title="Kisah di Balik Salju",
            author="Novelis AI",
            language="id",
            synopsis="Sebuah petualangan di dunia es."
        )

        exporter.add_chapter(
            title="Bab 1: Pertemuan di Gerbang",
            content_html_or_text="Aria menatap gerbang es yang membeku.\n\n* * *\n\nLangkah kaki terdengar dari balik kabut.",
            chapter_idx=1
        )
        exporter.add_chapter(
            title="Bab 2: Rahasia Terungkap",
            content_html_or_text="Segel perak itu akhirnya bersinar dalam kegelapan malam.",
            chapter_idx=2
        )

        exported_path = exporter.export_to_file(output_file)
        assert exported_path.exists()
        assert exported_path.stat().st_size > 0

        # Verify ZIP contents
        with zipfile.ZipFile(exported_path, "r") as zf:
            namelist = zf.namelist()
            # 1. mimetype must be the first file and uncompressed
            assert namelist[0] == "mimetype"
            mimetype_bytes = zf.read("mimetype").decode("utf-8")
            assert mimetype_bytes == "application/epub+zip"

            # 2. Check structure files
            assert "META-INF/container.xml" in namelist
            assert "OEBPS/content.opf" in namelist
            assert "OEBPS/nav.xhtml" in namelist
            assert "OEBPS/style.css" in namelist
            assert "OEBPS/title.xhtml" in namelist
            assert "OEBPS/chapter_1.xhtml" in namelist
            assert "OEBPS/chapter_2.xhtml" in namelist

            # 3. Check content integrity
            chap1_text = zf.read("OEBPS/chapter_1.xhtml").decode("utf-8")
            assert "Aria menatap gerbang es yang membeku." in chap1_text
            assert "* * *" in chap1_text
