"""Novelis EPUB Exporter Engine
Compiles generated novel chapters, scenes, and metadata into valid,
standardized EPUB3 digital book files.
"""

from pathlib import Path
import zipfile
import html
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime


class EpubExporter:
    """Exports compiled story chapters and scenes to standard EPUB format."""

    def __init__(
        self,
        title: str = "Untitled Novel",
        author: str = "Novelis Author",
        language: str = "en",
        synopsis: Optional[str] = None
    ):
        self.title = title
        self.author = author
        self.language = language
        self.synopsis = synopsis or ""
        self.chapters: List[Dict[str, Any]] = []

    def add_chapter(self, title: str, content_html_or_text: str, chapter_idx: int) -> None:
        """Adds a chapter with its formatted text or HTML content."""
        self.chapters.append({
            "idx": chapter_idx,
            "title": title,
            "content": content_html_or_text
        })

    def export_to_file(self, output_path: Path) -> Path:
        """Packages the complete novel into an EPUB file."""
        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Standard EPUB CSS typography
        css_content = """
        body {
            font-family: Georgia, "Times New Roman", serif;
            line-height: 1.6;
            margin: 5% 8%;
            color: #1a1a1a;
        }
        h1.book-title {
            text-align: center;
            font-size: 2.2em;
            margin-top: 25%;
            margin-bottom: 0.2em;
        }
        p.author {
            text-align: center;
            font-size: 1.2em;
            font-style: italic;
            color: #555;
            margin-bottom: 25%;
        }
        h2.chapter-title {
            text-align: center;
            font-size: 1.6em;
            margin-top: 10%;
            margin-bottom: 1.5em;
            page-break-before: always;
        }
        p {
            text-indent: 1.5em;
            margin-top: 0;
            margin-bottom: 0;
            text-align: justify;
        }
        p.first-p {
            text-indent: 0;
        }
        div.scene-break {
            text-align: center;
            margin: 1.5em 0;
            letter-spacing: 0.3em;
            color: #777;
        }
        """

        book_uuid = str(uuid.uuid4())
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

        # Create EPUB ZIP package
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. 'mimetype' MUST be uncompressed and the very first entry
            zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

            # 2. META-INF/container.xml
            container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
            zf.writestr("META-INF/container.xml", container_xml)

            # 3. Stylesheet
            zf.writestr("OEBPS/style.css", css_content)

            # 4. Title / Cover Page
            title_page_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="{self.language}">
<head>
  <title>{html.escape(self.title)}</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
  <h1 class="book-title">{html.escape(self.title)}</h1>
  <p class="author">by {html.escape(self.author)}</p>
  {f'<div class="synopsis"><p class="first-p">{html.escape(self.synopsis)}</p></div>' if self.synopsis else ''}
</body>
</html>"""
            zf.writestr("OEBPS/title.xhtml", title_page_html)

            # 5. Chapters
            manifest_items = [
                '<item id="style" href="style.css" media-type="text/css"/>',
                '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>',
                '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
            ]
            spine_items = ['<itemref idref="title"/>']
            nav_points = []

            for i, chap in enumerate(self.chapters, start=1):
                chap_id = f"chapter_{i}"
                filename = f"chapter_{i}.xhtml"

                # Format paragraphs
                paragraphs = chap["content"].split("\n\n")
                body_parts = []
                for p_idx, p in enumerate(paragraphs):
                    p_clean = p.strip()
                    if not p_clean:
                        continue
                    if p_clean in ["* * *", "***", "---"]:
                        body_parts.append('<div class="scene-break">* * *</div>')
                    else:
                        cls = ' class="first-p"' if p_idx == 0 else ""
                        body_parts.append(f"<p{cls}>{html.escape(p_clean)}</p>")

                chap_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="{self.language}">
<head>
  <title>{html.escape(chap["title"])}</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
  <h2 class="chapter-title">{html.escape(chap["title"])}</h2>
  {"".join(body_parts)}
</body>
</html>"""
                zf.writestr(f"OEBPS/{filename}", chap_html)
                manifest_items.append(f'<item id="{chap_id}" href="{filename}" media-type="application/xhtml+xml"/>')
                spine_items.append(f'<itemref idref="{chap_id}"/>')
                nav_points.append(f'<li><a href="{filename}">{html.escape(chap["title"])}</a></li>')

            # 6. Navigation Document (nav.xhtml)
            nav_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{self.language}">
<head>
  <title>Table of Contents</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
  <nav epub:type="toc" id="toc">
    <h2>Table of Contents</h2>
    <ol>
      <li><a href="title.xhtml">Title Page</a></li>
      {"".join(nav_points)}
    </ol>
  </nav>
</body>
</html>"""
            zf.writestr("OEBPS/nav.xhtml", nav_html)

            # 7. Package Document (content.opf)
            content_opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package version="3.0" unique-identifier="pub-id" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="pub-id">urn:uuid:{book_uuid}</dc:identifier>
    <dc:title>{html.escape(self.title)}</dc:title>
    <dc:creator>{html.escape(self.author)}</dc:creator>
    <dc:language>{self.language}</dc:language>
    <dc:date>{date_str}</dc:date>
    <meta property="dcterms:modified">{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}</meta>
  </metadata>
  <manifest>
    {"".join(manifest_items)}
  </manifest>
  <spine>
    {"".join(spine_items)}
  </spine>
</package>"""
            zf.writestr("OEBPS/content.opf", content_opf)

        return output_path
