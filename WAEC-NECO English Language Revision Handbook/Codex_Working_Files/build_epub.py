from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re
import uuid
import zipfile


BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent
MASTER = BASE / "Working_Manuscript" / "WAEC_NECO_English_Language_Revision_Handbook_Assembly_Draft.md"
DELIVERY = PROJECT / "For_Professor"
TITLE = "The Complete WAEC/NECO English Language Revision Handbook"
AUTHOR = "Prof. Johnson Agharese Egonmwan"
IDENTIFIER = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, TITLE + "|" + AUTHOR))
CHAPTER_NAMES = "One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen Fourteen Fifteen Sixteen".split()
CHAPTER_RE = re.compile(r"^(?:# )?Chapter (" + "|".join(CHAPTER_NAMES) + r")\s*$")
OUTPUT = DELIVERY / "The_Complete_WAEC_NECO_English_Language_Revision_Handbook.epub"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def inline(value: str) -> str:
    tokens = re.split(r"(\[[^\]]+\]\(https?://[^)]+\)|\*\*.+?\*\*|\*.+?\*)", value)
    rendered = []
    for token in tokens:
        link = re.fullmatch(r"\[([^\]]+)\]\((https?://[^)]+)\)", token)
        if link:
            rendered.append(f'<a href="{escape(link.group(2), quote=True)}">{escape(link.group(1))}</a>')
        elif token.startswith("**") and token.endswith("**"):
            rendered.append(f"<strong>{escape(token[2:-2])}</strong>")
        elif token.startswith("*") and token.endswith("*"):
            rendered.append(f"<em>{escape(token[1:-1])}</em>")
        else:
            rendered.append(escape(token))
    return "".join(rendered)


def parse_table_line(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def markdown_to_xhtml(lines: list[str], chapter_title: str, chapter_id: str) -> tuple[str, list[tuple[str, str]]]:
    body: list[str] = []
    toc: list[tuple[str, str]] = []
    paragraph_lines: list[str] = []
    list_kind: str | None = None
    table_rows: list[list[str]] = []
    heading_ids: dict[str, int] = {}

    def flush_p() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            body.append("<p>" + inline(" ".join(paragraph_lines)) + "</p>")
            paragraph_lines = []

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            body.append(f"</{list_kind}>")
            list_kind = None

    def flush_table() -> None:
        nonlocal table_rows
        if table_rows:
            if len(table_rows) > 1 and all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in table_rows[1]):
                table_rows.pop(1)
            body.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in table_rows[0]) + "</tr></thead><tbody>")
            for row in table_rows[1:]:
                body.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
            body.append("</tbody></table>")
            table_rows = []

    def heading(text: str, level: int) -> None:
        base_id = f"{chapter_id}-{slug(text)}"
        heading_ids[base_id] = heading_ids.get(base_id, 0) + 1
        ident = base_id if heading_ids[base_id] == 1 else f"{base_id}-{heading_ids[base_id]}"
        body.append(f'<h{level} id="{ident}">{inline(text)}</h{level}>')
        if level <= 3:
            toc.append((text, ident))

    for raw in lines:
        line = raw.strip()
        if not line or line == "---":
            flush_p(); close_list(); flush_table()
            continue
        if line.startswith("|"):
            flush_p(); close_list()
            table_rows.append(parse_table_line(line))
            continue
        flush_table()
        if line.startswith("### "):
            flush_p(); close_list(); heading(line[4:].strip(), 3)
        elif line.startswith("## "):
            flush_p(); close_list(); heading(line[3:].strip(), 2)
        elif line.startswith("# "):
            flush_p(); close_list(); heading(line[2:].strip(), 1)
        elif re.match(r"^\d+(?:\.\d+)+\s+", line):
            flush_p(); close_list(); heading(line, 3)
        elif line in {"Learning Objectives", "Chapter Summary", "WAEC/NECO Revision Questions", "Common Examination Mistakes", "Practical Exercise", "Theory Questions", "Mock Examination One", "Mock Examination Two", "Answer key and marking guide", "Final Self-Assessment Checklist", "Final Advice to Candidates"}:
            flush_p(); close_list(); heading(line, 3)
        elif line.startswith("- ") or line.startswith("* "):
            flush_p()
            if list_kind != "ul":
                close_list(); body.append("<ul>"); list_kind = "ul"
            body.append(f"<li>{inline(line[2:])}</li>")
        elif re.match(r"^\d+\.\s+", line):
            flush_p()
            if list_kind != "ol":
                close_list(); body.append("<ol>"); list_kind = "ol"
            body.append(f"<li>{inline(re.sub(r'^\d+\.\s+', '', line))}</li>")
        else:
            close_list(); paragraph_lines.append(line)
    flush_p(); close_list(); flush_table()
    return "\n".join(body), toc


def xhtml(title: str, content: str, *, lang: str = "en-GB") -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" '
        f'xmlns:epub="http://www.idpf.org/2007/ops" lang="{lang}" xml:lang="{lang}">'
        f"<head><title>{escape(title)}</title><link rel=\"stylesheet\" type=\"text/css\" href=\"styles.css\"/></head>"
        f"<body>{content}</body></html>"
    )


raw = MASTER.read_text(encoding="utf-8-sig")
raw = raw[raw.find("---\n") + 4:]
lines = raw.splitlines()
chapters: list[tuple[str, str, list[str]]] = []
starts = [i for i, line in enumerate(lines) if CHAPTER_RE.match(line.strip())]
for pos, start in enumerate(starts):
    match = CHAPTER_RE.match(lines[start].strip())
    assert match is not None
    end = starts[pos + 1] if pos + 1 < len(starts) else len(lines)
    chunk = lines[start + 1:end]
    title_line_index = next((i for i, line in enumerate(chunk) if line.strip()), None)
    if title_line_index is None:
        raise ValueError(f"Missing chapter title after {lines[start]}")
    chapter_title = re.sub(r"^#{1,3}\s+", "", chunk[title_line_index].strip())
    content_lines = chunk[title_line_index + 1:]
    chapter_label = match.group(1)
    chapters.append((chapter_label, chapter_title, content_lines))

if len(chapters) != 16:
    raise ValueError(f"Expected 16 chapters; found {len(chapters)}")

chapter_files: dict[str, str] = {}
all_sections: list[tuple[str, str, str]] = []
nav_chapters: list[str] = []
spine_items: list[str] = []
manifest_items: list[str] = []
for number, (label, chapter_title, content_lines) in enumerate(chapters, start=1):
    cid = f"chapter-{number:02d}"
    body, section_toc = markdown_to_xhtml(content_lines, chapter_title, cid)
    chapter_heading = f"<h1 id=\"{cid}\">Chapter {escape(label)}</h1><h2>{escape(chapter_title)}</h2>"
    chapter_files[cid + ".xhtml"] = xhtml(f"Chapter {label}: {chapter_title}", chapter_heading + body)
    nav_chapters.append(f'<li><a href="{cid}.xhtml#{cid}">Chapter {escape(label)}: {escape(chapter_title)}</a></li>')
    spine_items.append(f'<itemref idref="{cid}"/>')
    manifest_items.append(f'<item id="{cid}" href="{cid}.xhtml" media-type="application/xhtml+xml"/>')
    for heading_text, heading_id in section_toc:
        all_sections.append((f"Chapter {label}: {chapter_title}", cid + ".xhtml#" + heading_id, heading_text))

nav = xhtml("Contents", '<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>' + "".join(nav_chapters) + '<li><a href="topic-finder.xhtml">Topic Finder</a></li></ol></nav>')
topic_items = []
for chapter_name, href, heading_text in all_sections:
    topic_items.append(f'<li><a href="{escape(href)}">{escape(heading_text)}</a> <span class="context">({escape(chapter_name)})</span></li>')
topic_page = xhtml("Topic Finder", '<main><h1>Topic Finder</h1><p>Use this list to jump to chapter topics. In a reflowable ebook, page numbers depend on your device and text settings.</p><ul>' + "".join(topic_items) + '</ul></main>')

cover_name = "cover-front.jpg"
cover_file = DELIVERY / "WAEC_NECO_English_Language_Cover_Front_Review.jpeg"
cover_page = xhtml("Cover", f'<section class="cover"><img src="{cover_name}" alt="Front cover of The Complete WAEC/NECO English Language Revision Handbook"/></section>')
style = '''body{font-family:serif;line-height:1.5;margin:5%;}h1,h2,h3{font-family:sans-serif;line-height:1.2;color:#0b2c62;}h1{font-size:1.6em;margin:1.4em 0 .7em;}h2{font-size:1.3em;margin:1.3em 0 .6em;}h3{font-size:1.05em;margin:1.2em 0 .5em;}p{margin:.6em 0;text-indent:0;}ul,ol{padding-left:1.5em;}li{margin:.35em 0;}table{border-collapse:collapse;width:100%;font-size:.9em;}th,td{border:1px solid #9aa8b5;padding:.35em;vertical-align:top;}th{background:#e6edf5;}img{max-width:100%;height:auto;}.context{font-size:.85em;color:#555;}.cover{text-align:center}.cover img{max-height:95vh;width:auto;}'''
manifest_items.extend([
    '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
    '<item id="topicfinder" href="topic-finder.xhtml" media-type="application/xhtml+xml"/>',
    '<item id="coverpage" href="cover.xhtml" media-type="application/xhtml+xml"/>',
    '<item id="coverimage" href="cover-front.jpg" media-type="image/jpeg" properties="cover-image"/>',
    '<item id="style" href="styles.css" media-type="text/css"/>',
])
spine_items = ['<itemref idref="coverpage"/>'] + spine_items + ['<itemref idref="topicfinder"/>']
modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
opf = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id" xml:lang="en-GB">'
    f'<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="pub-id">{IDENTIFIER}</dc:identifier>'
    f'<dc:title>{escape(TITLE)}</dc:title><dc:creator>{escape(AUTHOR)}</dc:creator><dc:language>en-GB</dc:language>'
    f'<meta property="dcterms:modified">{modified}</meta></metadata>'
    '<manifest>' + "".join(manifest_items) + '</manifest><spine>' + "".join(spine_items) + '</spine></package>'
)
container = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
    '<rootfiles><rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(OUTPUT, "w") as epub:
    epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
    epub.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
    epub.writestr("OEBPS/package.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
    epub.writestr("OEBPS/nav.xhtml", nav, compress_type=zipfile.ZIP_DEFLATED)
    epub.writestr("OEBPS/topic-finder.xhtml", topic_page, compress_type=zipfile.ZIP_DEFLATED)
    epub.writestr("OEBPS/cover.xhtml", cover_page, compress_type=zipfile.ZIP_DEFLATED)
    epub.writestr("OEBPS/styles.css", style, compress_type=zipfile.ZIP_DEFLATED)
    for name, content in chapter_files.items():
        epub.writestr("OEBPS/" + name, content, compress_type=zipfile.ZIP_DEFLATED)
    epub.write(cover_file, "OEBPS/" + cover_name, compress_type=zipfile.ZIP_DEFLATED)

print(f"Built {OUTPUT} ({OUTPUT.stat().st_size} bytes)")
