from __future__ import annotations

from html import escape
from pathlib import Path
import re
import subprocess
import sys
import tempfile


BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent
MANUSCRIPT = BASE / "Working_Manuscript" / "WAEC_NECO_English_Language_Revision_Handbook_Assembly_Draft.md"
PRODUCTION = BASE / "Production"
DELIVERY = PROJECT / "For_Professor"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PYMUPDF = PROJECT.parent / "Serenity and Tranquillity" / "Codex_Working_Files" / ".python_libs"
sys.path.insert(0, str(PYMUPDF))
import fitz  # noqa: E402

CHAPTER_RE = re.compile(r"^(?:# )?Chapter (One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen)$")


def inline(value: str) -> str:
    value = escape(value)
    value = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', value)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"\*(.+?)\*", r"<em>\1</em>", value)
    return value


def split_table_line(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def make_html(page_numbers: dict[str, dict[str, int]] | None = None) -> tuple[str, str]:
    raw = MANUSCRIPT.read_text(encoding="utf-8-sig")
    raw = raw[raw.find("---\n") + 4:]
    lines = raw.splitlines()
    chapters: list[tuple[str, str, str]] = []
    for index, line in enumerate(lines):
        match = CHAPTER_RE.match(line.strip())
        if not match:
            continue
        title = ""
        for candidate in lines[index + 1:]:
            if candidate.strip():
                title = re.sub(r"^#{1,3}\s+", "", candidate.strip())
                break
        slug = f"chapter-{match.group(1).lower()}"
        chapters.append((match.group(0).removeprefix("# "), title, slug))

    out: list[str] = []
    out.append('<section class="title-page"><div class="kicker">THE COMPLETE WAEC / NECO</div>'
               '<h1>English Language<br>Revision Handbook</h1>'
               '<p class="author">Prof. Johnson Agharese Egonmwan</p>'
               '<p class="draft">Editorial review draft<br>Not for publication</p>'
               '<p class="notice">Working manuscript. Final title, imprint, ISBN, exam claims and contents require approval.</p></section>')
    out.append('<section class="contents"><h1>Contents</h1><div class="contents-list">')
    for chapter, title, slug in chapters:
        out.append(f'<div class="contents-row" data-slug="{slug}"><a href="#{slug}"><span class="toc-label">{escape(chapter)}: {escape(title)}</span><span class="toc-leader"></span><span class="toc-page"></span></a></div>')
    out.append('</div></section>')

    paragraph_lines: list[str] = []
    list_tag: str | None = None
    table_rows: list[list[str]] = []
    chapter_pending = False

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            out.append(f'<p>{inline(" ".join(paragraph_lines))}</p>')
            paragraph_lines = []

    def close_list() -> None:
        nonlocal list_tag
        if list_tag:
            out.append(f'</{list_tag}>')
            list_tag = None

    def flush_table() -> None:
        nonlocal table_rows
        if table_rows:
            if len(table_rows) > 1 and all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in table_rows[1]):
                table_rows.pop(1)
            out.append('<table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in table_rows[0]) + '</tr></thead><tbody>')
            for row in table_rows[1:]:
                out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in row) + '</tr>')
            out.append('</tbody></table>')
            table_rows = []

    for line in lines:
        stripped = line.strip()
        chapter_match = CHAPTER_RE.match(stripped)
        if chapter_match:
            flush_paragraph(); close_list(); flush_table()
            chapter = stripped.removeprefix("# ")
            slug = f"chapter-{chapter.split()[-1].lower()}"
            out.append(f'<h1 class="chapter" id="{slug}">{escape(chapter)}</h1>')
            chapter_pending = True
            continue
        if not stripped or stripped == "---":
            flush_paragraph(); close_list(); flush_table()
            continue
        if stripped.startswith("|"):
            flush_paragraph(); close_list()
            table_rows.append(split_table_line(stripped))
            continue
        flush_table()
        if stripped.startswith("# "):
            flush_paragraph(); close_list()
            out.append(f'<h1>{inline(stripped[2:])}</h1>')
        elif stripped.startswith("## "):
            flush_paragraph(); close_list()
            heading = stripped[3:].strip()
            if chapter_pending:
                out.append(f'<h2 class="chapter-title">{inline(heading)}</h2>')
                chapter_pending = False
            else:
                out.append(f'<h2>{inline(heading)}</h2>')
        elif stripped.startswith("### "):
            flush_paragraph(); close_list()
            out.append(f'<h3>{inline(stripped[4:])}</h3>')
        elif stripped.startswith("- ") or stripped.startswith("* "):
            flush_paragraph()
            if list_tag != "ul":
                close_list(); out.append("<ul>"); list_tag = "ul"
            out.append(f'<li>{inline(stripped[2:])}</li>')
        elif re.match(r"^\d+\.\s+", stripped):
            flush_paragraph()
            if list_tag != "ol":
                close_list(); out.append("<ol>"); list_tag = "ol"
            out.append(f'<li>{inline(re.sub(r"^\d+\.\s+", "", stripped))}</li>')
        else:
            close_list()
            paragraph_lines.append(stripped)
    flush_paragraph(); close_list(); flush_table()
    body = "\n".join(out)

    def document(trim: str, font_size: str, margins: str) -> str:
        title = "The Complete WAEC/NECO English Language Revision Handbook - Editorial Review Draft"
        css = f'''<style>
@page {{ size:{trim}; margin:{margins}; @bottom-center {{ content:counter(page); font:9pt Georgia,serif; color:#173f35; }} }}
* {{ box-sizing:border-box; }}
body {{ font-family:Georgia,"Times New Roman",serif; font-size:{font_size}; line-height:1.42; color:#17202a; }}
.title-page {{ min-height:165mm; display:flex; flex-direction:column; justify-content:center; text-align:center; page-break-after:always; }}
.cover {{ height:255mm; display:flex; align-items:center; justify-content:center; page-break-after:always; }}
.cover img {{ display:block; max-width:100%; max-height:100%; object-fit:contain; }}
.kicker {{ font:700 15pt Arial,sans-serif; letter-spacing:2pt; color:#b48612; }}
.title-page h1 {{ font:700 28pt Arial,sans-serif; color:#0b2c62; line-height:1.14; margin:16pt 0; }}
.author {{ font:700 15pt Arial,sans-serif; margin-top:20pt; }}
.draft {{ font:700 12pt Arial,sans-serif; color:#9d2525; margin-top:26pt; }}
.notice {{ font:10pt Arial,sans-serif; color:#555; max-width:130mm; margin:22pt auto 0; }}
.contents {{ page-break-after:always; }}
.contents h1 {{ font:700 19pt Arial,sans-serif; color:#0b2c62; }}
.contents-list {{ margin:0; padding:0; }}
.contents-row {{ margin:0 0 5pt; break-inside:avoid; }}
.contents-row a {{ display:flex; align-items:baseline; gap:5pt; color:#0b2c62; text-decoration:none; }}
.toc-label {{ flex:0 1 auto; }}
.toc-leader {{ flex:1 1 auto; min-width:10pt; border-bottom:0.7pt dotted #53647a; }}
.toc-page {{ flex:0 0 auto; min-width:14pt; text-align:right; font-weight:700; }}
h1.chapter {{ page-break-before:always; page-break-after:avoid; font:700 20pt Arial,sans-serif; color:#fff; background:#17633c; padding:10pt 12pt; margin:0 0 7pt; }}
h2.chapter-title {{ font:700 15pt Arial,sans-serif; color:#0b2c62; margin:0 0 16pt; page-break-after:avoid; }}
h1:not(.chapter) {{ font:700 19pt Arial,sans-serif; color:#0b2c62; }}
h2 {{ font:700 15pt Arial,sans-serif; color:#0b2c62; margin:15pt 0 7pt; page-break-after:avoid; }}
h3 {{ font:700 12pt Arial,sans-serif; color:#17633c; margin:12pt 0 5pt; page-break-after:avoid; }}
p {{ margin:0 0 8pt; orphans:2; widows:2; }}
li {{ margin:0 0 3pt; }}
table {{ width:100%; border-collapse:collapse; margin:8pt 0 13pt; font-size:9.5pt; page-break-inside:avoid; }}
th,td {{ border:0.5pt solid #bbc6d1; padding:5pt; text-align:left; vertical-align:top; }}
th {{ background:#dce6f1; }}
a {{ color:#0b5d42; }}
@media print {{ h1.chapter,th {{ print-color-adjust:exact; -webkit-print-color-adjust:exact; }} }}
</style>'''
        cover = ''
        if trim == "A4":
            cover_path = DELIVERY / "WAEC_NECO_English_Language_Cover_Front_Review.jpeg"
            cover = f'<section class="cover"><img src="{escape(cover_path.resolve().as_uri())}" alt="Review front cover" /></section>'
        toc = body
        trim_pages = (page_numbers or {}).get(trim, {})
        for chapter, chapter_title, slug in chapters:
            ref = str(trim_pages.get(slug, ""))
            marker = f'<span class="toc-page"></span>'
            # Inject this trim's locator in the already-built chapter row.
            row_start = toc.find(f'<div class="contents-row" data-slug="{slug}">')
            if row_start >= 0:
                row_end = toc.find('</div>', row_start) + 6
                row = toc[row_start:row_end]
                toc = toc[:row_start] + row.replace(marker, f'<span class="toc-page">{ref}</span>') + toc[row_end:]
        return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + escape(title) + '</title>' + css + '</head><body>' + cover + toc + '</body></html>'

    return document("A5", "10.5pt", "16mm 15mm 17mm"), document("A4", "11.5pt", "18mm 19mm 19mm")


def render(html_path: Path, pdf_path: Path) -> None:
    profile = tempfile.mkdtemp(prefix="waec-review-")
    subprocess.run(
        [str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
         "--no-pdf-header-footer", f"--user-data-dir={profile}",
         f"--print-to-pdf={pdf_path.resolve()}", html_path.resolve().as_uri()],
        check=True, capture_output=True, text=True, timeout=240,
    )


def locate_chapters(pdf_path: Path) -> dict[str, int]:
    document = fitz.open(pdf_path)
    result: dict[str, int] = {}
    for chapter, _title, slug in chapters_for_lookup:
        for page_index, page in enumerate(document):
            lines = [line.strip() for line in page.get_text().splitlines()]
            if chapter in lines:
                result[slug] = page_index + 1
                break
        if slug not in result:
            raise RuntimeError(f"Could not locate the printed heading {chapter!r} in {pdf_path.name}")
    return result


PRODUCTION.mkdir(parents=True, exist_ok=True)
DELIVERY.mkdir(parents=True, exist_ok=True)
chapters_for_lookup = []
for line in MANUSCRIPT.read_text(encoding="utf-8-sig").splitlines():
    match = CHAPTER_RE.match(line.strip())
    if match:
        chapter = match.group(0).removeprefix("# ")
        chapters_for_lookup.append((chapter, "", f"chapter-{match.group(1).lower()}"))

page_numbers: dict[str, dict[str, int]] = {}
with tempfile.TemporaryDirectory(prefix="waec-toc-pages-") as temp_dir:
    temp_path = Path(temp_dir)
    # First pass uses the same layout with blank locators to establish chapter pages.
    for trim, html in zip(("A5", "A4"), make_html()):
        html_file = temp_path / f"unpaginated_{trim}.html"
        pdf_file = temp_path / f"unpaginated_{trim}.pdf"
        html_file.write_text(html, encoding="utf-8")
        render(html_file, pdf_file)
        page_numbers[trim] = locate_chapters(pdf_file)

    # Render again with locators, re-measure and repeat if TOC reflow changed pagination.
    for pass_number in range(3):
        stable = True
        for trim, html in zip(("A5", "A4"), make_html(page_numbers)):
            html_file = PRODUCTION / f"WAEC_NECO_English_Language_Review_Draft_{trim}.html"
            pdf_file = DELIVERY / f"WAEC_NECO_English_Language_Revision_Handbook_Review_Draft_{trim}.pdf"
            html_file.write_text(html, encoding="utf-8")
            render(html_file, pdf_file)
            actual = locate_chapters(pdf_file)
            if actual != page_numbers[trim]:
                page_numbers[trim] = actual
                stable = False
            print(f"{pdf_file.name}: {pdf_file.stat().st_size} bytes; {len(actual)} chapter page locators (pass {pass_number + 1})")
        if stable:
            break
    else:
        raise RuntimeError("Chapter page locators did not stabilize after three layout passes")
