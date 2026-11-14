from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from html import escape
import re
import textwrap
import zipfile

ROOT = Path(r"C:\Users\ASUS\Resyin Books\Book_Production")
ATT = Path(r"C:\Users\ASUS\.codex\attachments")
FRONT_ID = "5eeca7d5-b4d1-416b-a513-7126dd7f382e"
BACK_ID = "cebc3be1-ebac-4fb2-9abb-792b826ee160"
CHAPTER_IDS = [
    "5c86c100-191a-4c02-93c3-5fddbf744a45", "cf9922a4-9eda-4b44-bb27-13ea3e8cbec3",
    "706c830c-5ef4-40b1-9649-afc170c4f8dd", "13db2e00-588d-486a-b86f-7513d49a70ae",
    "d5af19b0-ad92-4ae5-8118-a060a79daae3", "3e821591-41fa-4c5e-be89-e06419ca4add",
    "788e36c2-3a73-4867-90f5-5ba6dc636db2", "f92bd4ec-44ea-4282-8b63-5405bf007fe0",
    "51efdcca-44ea-4124-ac96-1f407a0e6515", "fbd98972-ef6e-4600-9889-1ad73bfefd85",
    "91e2c407-6518-40ee-aea6-6b462714b391", "944a17f5-aa86-4d01-a445-e0da19237afb",
    "a1648bc2-60cf-4954-a796-a303f04f994d", "2cb6f00a-6004-4f2d-bc4c-1433230bd3b8",
    "4c1e8038-6dc1-46a5-be39-85092aa3cf40", "d4b3ef72-caa6-48f9-989a-bd45860726c5",
    "10d33a54-c684-4dbb-9c30-23ee37a58835", "bef6513d-2b21-4276-8c74-11806fee363e",
    "a7b13fa8-2e19-4b0a-9396-7dc33d5baac0", "cac25b7c-f304-46dc-8642-bf9561e20db8",
    "c6180df9-6665-4964-a20b-dffe5c4a52fc", "a0e8720f-1ac5-4ef7-9deb-477033996038",
    "3fc7a465-4321-4bd4-a4a3-60bad3347ef8", "449294f9-00e5-4ec2-85b5-776cd4efc71f",
    "2259515c-8dd7-4e4b-aefc-4f354804c043",
]
TITLE = "SERENITY AND TRANQUILLITY"
SUBTITLE = "In Personal Life, Community Life, National Development and the Future of Humanity"
TAGLINE = "A Philosophy for Sustainable Development, Peaceful Coexistence and a Better Future"
AUTHOR = "Prof. Johnson Agharese Egonmwan"
PARTS = {
    1: "PART I  |  PERSONAL FOUNDATIONS",
    6: "PART II  |  FAMILIES AND COMMUNITIES",
    9: "PART III  |  NATIONAL DEVELOPMENT",
    20: "PART IV  |  GLOBAL PEACE AND THE FUTURE",
}
FRONT_HEADINGS = {
    "COPYRIGHT PAGE", "DEDICATION", "EPIGRAPH", "FOREWORD", "PREFACE", "ACKNOWLEDGEMENTS",
    "INTRODUCTION", "LIST OF ABBREVIATIONS", "REFERENCES AND BIBLIOGRAPHY", "ABOUT THE AUTHOR",
    "FINAL AUTHOR'S REFLECTION", "EPILOGUE",
}


def read_doc(uid: str) -> str:
    return (ATT / uid / "Pasted text.txt").read_text(encoding="utf-8-sig")


def paragraphs(raw: str) -> list[str]:
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    raw = re.sub(r"(?m)^\s*-{3,}\s*$", "\n", raw)
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", raw) if p.strip() and p.strip() != "---"]


def chapter_title(raw: str) -> str:
    return paragraphs(raw)[0]


def edited_chapter_paragraphs(raw: str, chapter_no: int) -> list[str]:
    """Retain prose but consolidate the source's over-fragmented numbered headings."""
    items = paragraphs(raw)
    heading_indices = [i for i, p in enumerate(items) if re.match(rf"^{chapter_no}\.\d+\s+", p)]
    if len(heading_indices) <= 10:
        keep = set(heading_indices)
    else:
        interior = heading_indices[1:-1]
        slots = 8
        chosen = {round(k * (len(interior)-1) / (slots-1)) for k in range(slots)} if interior else set()
        keep = {heading_indices[0], heading_indices[-1]}
        keep.update(interior[i] for i in chosen)
    result = []
    section_number = 0
    for i, item in enumerate(items):
        if i in heading_indices:
            if i not in keep:
                continue
            section_number += 1
            title = re.sub(rf"^{chapter_no}\.\d+\s+", "", item)
            item = f"{chapter_no}.{section_number} {title}"
        result.append(item)
    return result


@dataclass
class Para:
    text: str
    style: str = "body"
    break_before: bool = False
    target: str = ""


def manuscript() -> tuple[list[Para], list[tuple[str, str]]]:
    front_raw = read_doc(FRONT_ID)
    raw_lines = front_raw.replace("\r\n", "\n").split("\n")
    prelim: list[Para] = []
    after_copyright = False
    suppress_toc = False
    suppress_lists = False
    for raw_line in raw_lines:
        line = raw_line.strip()
        if line == "COPYRIGHT PAGE":
            after_copyright = True
        if not after_copyright:
            continue
        if line == "TABLE OF CONTENTS":
            prelim.append(Para("TABLE OF CONTENTS", "fronthead", True, "toc"))
            prelim.append(Para("", "tocfield"))
            suppress_toc = True
            continue
        if suppress_toc:
            if line == "LIST OF FIGURES":
                suppress_toc = False
                suppress_lists = True
            continue
        if line == "LIST OF FIGURES":
            suppress_lists = True
            continue
        if line == "LIST OF ABBREVIATIONS":
            suppress_lists = False
        if suppress_lists:
            continue
        if line == "First Edition, 2026":
            prelim.append(Para(line))
            prelim.append(Para("ISBN 978-978-965-123-4"))
            continue
        if re.match(r"^CHAPTER ONE\b", line):
            break
        if not line or re.fullmatch(r"-{3,}", line):
            continue
        if line == "LIST OF TABLES":
            continue
        if line in FRONT_HEADINGS:
            prelim.append(Para(line, "fronthead", True, line))
        elif re.match(r"^\d+(?:\.\d+)+\s+", line):
            prelim.append(Para(line, "h2", False, line))
        else:
            prelim.append(Para(line))

    chapters = [read_doc(uid) for uid in CHAPTER_IDS]
    toc = [(f"Chapter {i}: {chapter_title(raw)}", f"chapter-{i}") for i, raw in enumerate(chapters, 1)]
    content: list[Para] = [
        Para(TITLE, "title"), Para(SUBTITLE, "subtitle"), Para(TAGLINE, "tagline"),
        Para(AUTHOR, "author"), Para("", "pagebreak"),
    ]
    content.extend(prelim)
    for index, raw in enumerate(chapters, 1):
        if index in PARTS:
            content.append(Para(PARTS[index], "part", True, f"part-{index}"))
        for pidx, paragraph in enumerate(edited_chapter_paragraphs(raw, index)):
            if pidx == 0:
                content.append(Para(paragraph, "chapter", True, f"chapter-{index}"))
            elif re.match(r"^\d+(?:\.\d+)+\s+", paragraph):
                content.append(Para(paragraph, "h2", False, paragraph))
            else:
                content.append(Para(paragraph))
    for paragraph in paragraphs(read_doc(BACK_ID)):
        if paragraph in FRONT_HEADINGS or paragraph in {"REFERENCES AND BIBLIOGRAPHY", "ABOUT THE AUTHOR", "FINAL AUTHOR'S REFLECTION", "EPILOGUE"}:
            content.append(Para(paragraph, "fronthead", True, paragraph))
        elif re.match(r"^\d+(?:\.\d+)+\s+", paragraph):
            content.append(Para(paragraph, "h2"))
        else:
            content.append(Para(paragraph))
    return content, toc


def char_width(ch: str, font: str, size: float) -> float:
    if ch == " ": return size * 0.25
    if ch in "ilI.,:;!'|": return size * 0.24
    if ch in "mwMW@%&": return size * 0.78
    if ch in "frt()[]{}": return size * 0.34
    if ch.isupper(): return size * 0.59
    if ch.isdigit(): return size * 0.50
    return size * (0.48 if font == "Times-Roman" else 0.52)


def wrap_text(text: str, width: float, size: float, font: str) -> list[str]:
    words = text.split()
    if not words: return [""]
    lines: list[str] = []
    line = ""
    current = 0.0
    for word in words:
        w = sum(char_width(c, font, size) for c in word)
        extra = char_width(" ", font, size) if line else 0
        if line and current + extra + w > width:
            lines.append(line); line = word; current = w
        else:
            line = (line + " " + word).strip(); current += extra + w
    if line: lines.append(line)
    return lines


@dataclass
class Page:
    width: float
    height: float
    commands: list[str] = field(default_factory=list)
    links: list[tuple[float, float, float, float, str]] = field(default_factory=list)


def pdf_escape(text: str) -> str:
    text = text.replace("→", "to").replace("↓", "v").replace("↔", "and")
    data = text.encode("cp1252", errors="replace")
    return "<" + data.hex().upper() + ">"


def render_pdf(pieces: list[Para], toc: list[tuple[str, str]], mode: str, output: Path) -> int:
    if mode == "print":
        pw, ph, margin_l, margin_r, top, bottom, body_size, leading = 432.0, 648.0, 61.0, 50.0, 54.0, 49.0, 10.5, 14.0
    else:
        pw, ph, margin_l, margin_r, top, bottom, body_size, leading = 595.28, 841.89, 57.0, 57.0, 57.0, 54.0, 11.5, 16.0
    usable = pw - margin_l - margin_r
    pages: list[Page] = []
    page = Page(pw, ph)
    pages.append(page)
    y = ph - top
    chapter_pages: dict[str, int] = {}
    toc_rows: list[tuple[str, str, float, list[str]]] = []
    toc_page_index: int | None = None
    toc_start_y: float | None = None

    def new_page():
        nonlocal page, y
        page = Page(pw, ph); pages.append(page); y = ph - top

    def draw(text: str, x: float, yy: float, size: float, font: str, color: tuple[float,float,float] = (0,0,0)):
        page.commands.append(f"{color[0]:.3f} {color[1]:.3f} {color[2]:.3f} rg BT /{font} {size:.2f} Tf 1 0 0 1 {x:.2f} {yy:.2f} Tm {pdf_escape(text)} Tj ET")

    if mode == "digital":
        # A designed, vector cover starts the screen edition; the title page follows it.
        page.commands.extend([
            f"0.98 0.96 0.90 rg 0 0 {pw:.2f} {ph:.2f} re f",
            f"0.84 0.91 0.93 rg 0 230 {pw:.2f} {ph-230:.2f} re f",
            f"0.04 0.22 0.15 rg 0 0 {pw:.2f} 95 re f",
            f"0.42 0.55 0.34 rg 0 220 {pw:.2f} 82 re f",
            f"0.67 0.79 0.78 rg 0 168 {pw:.2f} 63 re f",
        ])
        page.commands.append(f"1.0 0.82 0.48 rg 455 410 m 455 450 487 482 527 482 c 567 482 589 450 589 410 c 589 370 567 348 527 348 c 487 348 455 370 455 410 c f")
        for xx,yy0,ww,hh in [(58,270,42,120),(114,265,48,155),(176,263,55,190),(247,260,50,145),(308,266,48,130),(369,262,53,168),(433,269,44,125)]:
            page.commands.append(f"0.40 0.47 0.45 rg {xx} {yy0} {ww} {hh} re f")
        # City lights.
        for xx,yy0 in [(69,355),(87,355),(126,367),(148,367),(189,380),(213,380),(260,355),(282,355),(321,340),(342,340),(382,365),(406,365),(445,345)]:
            page.commands.append(f"0.94 0.79 0.48 rg {xx} {yy0} 6 7 re f")
        # Wind turbine and solar field.
        page.commands.append("0.91 0.93 0.88 RG 3 w 525 268 m 525 420 l S 525 420 m 570 460 l S 525 420 m 508 474 l S 525 420 m 580 414 l S")
        page.commands.append("0.08 0.19 0.29 rg 390 195 150 42 re f 0.43 0.65 0.68 RG 1 w 420 195 m 420 237 l S 450 195 m 450 237 l S 480 195 m 480 237 l S 390 216 m 540 216 l S")
        draw("SERENITY", 118, 785, 44, "Times-Bold", (0.04,0.10,0.23))
        draw("AND", 270, 750, 17, "Times-Roman", (0.80,0.54,0.15))
        draw("TRANQUILLITY", 76, 701, 36, "Times-Bold", (0.04,0.22,0.15))
        sy=648
        for ln in wrap_text("IN PERSONAL LIFE, COMMUNITY LIFE, NATIONAL DEVELOPMENT AND THE FUTURE OF HUMANITY",pw-90,12,"Times-Bold"):
            draw(ln, 48, sy, 12, "Times-Bold", (0.04,0.10,0.23)); sy-=18
        sy=594
        for ln in wrap_text(TAGLINE,pw-100,11,"Times-Italic"):
            draw(ln, 50, sy, 11, "Times-Italic", (0.04,0.22,0.15)); sy-=16
        draw("TOWARDS A MORE SERENE, TRANQUIL AND SUSTAINABLE WORLD", 47, 67, 10.5, "Times-Bold", (0.98,0.79,0.34))
        draw(AUTHOR, 110, 30, 13, "Times-Bold", (1,1,1))
        page = Page(pw, ph); pages.append(page)
        y = ph-top

    for p in pieces:
        if p.style == "pagebreak":
            new_page(); continue
        if p.break_before:
            if y != ph - top: new_page()
        if p.target.startswith("chapter-") or p.target.startswith("part-"):
            chapter_pages[p.target] = len(pages)
        if p.target == "toc":
            toc_page_index = len(pages) - 1
            toc_start_y = y - 16*1.35 - 14

        if p.style == "tocfield":
            continue
        if p.style == "title":
            draw("SERENITY AND", margin_l, y - 70, 27, "Times-Bold", (0.04,0.10,0.23)); y -= 104
            draw("TRANQUILLITY", margin_l, y, 27, "Times-Bold", (0.04,0.10,0.23)); y -= 58
            continue
        if p.style == "subtitle":
            for line in wrap_text(p.text, usable, 15, "Times-Roman"):
                draw(line, margin_l, y, 15, "Times-Roman", (0.08,0.24,0.17)); y -= 23
            y -= 14; continue
        if p.style == "tagline":
            for line in wrap_text(p.text, usable, 11.5, "Times-Italic"):
                draw(line, margin_l, y, 11.5, "Times-Italic", (0.62,0.39,0.08)); y -= 18
            y -= 15; continue
        if p.style == "author":
            draw(p.text, margin_l, y, 13, "Times-Bold", (0.04,0.10,0.23)); y -= 25; continue
        if p.style in {"fronthead", "chapter", "part"}:
            size = 19 if p.style == "chapter" else (15 if p.style == "part" else 16)
            font = "Times-Bold"
            color = (0.04,0.10,0.23) if p.style != "part" else (0.08,0.24,0.17)
            wrapped = wrap_text(p.text, usable, size, font)
            for line in wrapped:
                draw(line, margin_l, y, size, font, color); y -= size * 1.35
            if p.target == "toc":
                toc_rows = []
                for label, target in toc:
                    toc_size = 8.7 if mode == "print" else 9.5
                    toc_lead = 11.5 if mode == "print" else 13
                    row_lines = wrap_text(label, usable-38, toc_size, "Times-Roman")
                    y -= 4
                    toc_rows.append((label, target, y, row_lines))
                    for row_line in row_lines:
                        draw(row_line, margin_l, y, toc_size, "Times-Roman", (0.10,0.13,0.18))
                        y -= toc_lead
                    y -= 2
                continue
            y -= 15 if p.style == "chapter" else 10
            continue
        if p.style == "h2":
            size = body_size + 1
            lines = wrap_text(p.text, usable, size, "Times-Bold")
            if y - len(lines)*leading < bottom:
                new_page()
            for line in lines:
                draw(line, margin_l, y, size, "Times-Bold", (0.08,0.24,0.17)); y -= leading
            y -= 4
            continue

        lines = wrap_text(p.text, usable, body_size, "Times-Roman")
        for line in lines:
            if y - leading < bottom:
                new_page()
            draw(line, margin_l, y, body_size, "Times-Roman", (0.08,0.08,0.08)); y -= leading
        y -= leading * 0.35

    # Replace the provisional contents-page lines with final chapter page numbers.
    # Page-number values remain single-line, so page breaks do not move.
    if toc_page_index is not None:
        pg = pages[toc_page_index]
        # Remove provisional chapter entries; redraw each with page number and add a clickable destination.
        pg.commands = [c for c in pg.commands if not any(pdf_escape(line) in c for _, _, _, row_lines in toc_rows for line in row_lines)]
        yy = toc_start_y if toc_start_y is not None else ph-top-35
        toc_size = 8.7 if mode == "print" else 9.5
        toc_lead = 11.5 if mode == "print" else 13
        for label, target, _, row_lines in toc_rows:
            page_no = chapter_pages.get(target, 1)
            for j, row_line in enumerate(row_lines):
                pg.commands.append(f"0.10 0.13 0.18 rg BT /Times-Roman {toc_size:.2f} Tf 1 0 0 1 {margin_l:.2f} {yy:.2f} Tm {pdf_escape(row_line)} Tj ET")
                if j == len(row_lines)-1:
                    pg.commands.append(f"0.10 0.13 0.18 rg BT /Times-Roman {toc_size:.2f} Tf 1 0 0 1 {pw-margin_r-16:.2f} {yy:.2f} Tm {pdf_escape(str(page_no))} Tj ET")
                pg.links.append((margin_l, yy-2, pw-margin_r, yy+11, target))
                yy -= toc_lead
            yy -= 2

    # Add running heads and page numbers after layout.
    for i, pg in enumerate(pages):
        if i > (1 if mode == "digital" else 0):
            pg.commands.append(f"0.10 0.20 0.18 RG 0.4 w {margin_l:.2f} {ph-35:.2f} m {pw-margin_r:.2f} {ph-35:.2f} l S")
            pg.commands.append(f"0.08 0.10 0.20 rg BT /Times-Italic 8 Tf 1 0 0 1 {margin_l:.2f} {ph-28:.2f} Tm {pdf_escape('SERENITY AND TRANQUILLITY')} Tj ET")
            pg.commands.append(f"0.08 0.10 0.20 rg BT /Times-Roman 9 Tf 1 0 0 1 {pw/2-4:.2f} 26 Tm {pdf_escape(str(i+1))} Tj ET")

    objs: list[bytes | None] = []
    def reserve() -> int:
        objs.append(None); return len(objs)
    def add(data: bytes | str) -> int:
        if isinstance(data, str): data = data.encode("latin-1", errors="replace")
        objs.append(data); return len(objs)
    catalog_id = reserve(); pages_id = reserve()
    font_reg = add("<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman /Encoding /WinAnsiEncoding >>")
    font_bold = add("<< /Type /Font /Subtype /Type1 /BaseFont /Times-Bold /Encoding /WinAnsiEncoding >>")
    font_italic = add("<< /Type /Font /Subtype /Type1 /BaseFont /Times-Italic /Encoding /WinAnsiEncoding >>")
    page_ids = [reserve() for _ in pages]
    outline_root = reserve()
    outline_items: list[int] = []
    outline_data: list[tuple[str, int]] = []
    for i, p in enumerate(pieces):
        if p.style in {"chapter", "part"} and p.target in chapter_pages:
            if p.target.startswith("chapter-"):
                outline_data.append((p.text, chapter_pages[p.target]-1))
            elif p.target.startswith("part-"):
                outline_data.append((p.text, chapter_pages[p.target]-1))
    for _ in outline_data: outline_items.append(reserve())

    for idx, pg in enumerate(pages):
        stream = "\n".join(pg.commands).encode("latin-1", errors="replace")
        content_id = add(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
        annot_ids = []
        for x1,y1,x2,y2,target in pg.links:
            dest_index = chapter_pages.get(target, 1)-1
            annot_ids.append(add(f"<< /Type /Annot /Subtype /Link /Rect [{x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f}] /Border [0 0 0] /Dest [{page_ids[dest_index]} 0 R /Fit] >>"))
        annots = (" /Annots [" + " ".join(f"{a} 0 R" for a in annot_ids) + "]") if annot_ids else ""
        objs[page_ids[idx]-1] = f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {pg.width:.2f} {pg.height:.2f}] /Resources << /Font << /Times-Roman {font_reg} 0 R /Times-Bold {font_bold} 0 R /Times-Italic {font_italic} 0 R >> >> /Contents {content_id} 0 R{annots} >>".encode("ascii")

    for i, ((label, page_index), obj_id) in enumerate(zip(outline_data, outline_items)):
        prev = f" /Prev {outline_items[i-1]} 0 R" if i else ""
        nxt = f" /Next {outline_items[i+1]} 0 R" if i+1 < len(outline_items) else ""
        parent = outline_root
        objs[obj_id-1] = f"<< /Title {pdf_escape(label)} /Parent {parent} 0 R /Dest [{page_ids[page_index]} 0 R /Fit]{prev}{nxt} >>".encode("ascii")
    first = f" /First {outline_items[0]} 0 R /Last {outline_items[-1]} 0 R /Count {len(outline_items)}" if outline_items else ""
    objs[outline_root-1] = f"<< /Type /Outlines{first} >>".encode("ascii")
    kids = " ".join(f"{i} 0 R" for i in page_ids)
    objs[pages_id-1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode("ascii")
    objs[catalog_id-1] = f"<< /Type /Catalog /Pages {pages_id} 0 R /Outlines {outline_root} 0 R /PageMode /UseOutlines >>".encode("ascii")
    info_id = add(f"<< /Title {pdf_escape(TITLE)} /Author {pdf_escape(AUTHOR)} /Subject {pdf_escape(TAGLINE)} /Creator <436F646578> >>".encode("ascii"))
    out = bytearray(b"%PDF-1.7\n%\xE2\xE3\xCF\xD3\n")
    offsets = [0]
    for idx, obj in enumerate(objs, 1):
        offsets.append(len(out)); out.extend(f"{idx} 0 obj\n".encode()); out.extend(obj or b"<<>>"); out.extend(b"\nendobj\n")
    xref = len(out); out.extend(f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]: out.extend(f"{offset:010d} 00000 n \n".encode())
    out.extend(f"trailer\n<< /Size {len(objs)+1} /Root {catalog_id} 0 R /Info {info_id} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    output.write_bytes(out)
    return len(pages)


def xml_text(text: str) -> str:
    return escape(text).replace("\u00a0", " ")


def build_docx(pieces: list[Para], path: Path) -> None:
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    rels = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    doc_paras = []
    for p in pieces:
        if p.style == "pagebreak":
            doc_paras.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>'); continue
        if p.style == "tocfield":
            doc_paras.append('<w:p><w:fldSimple w:instr="TOC \\o &quot;1-1&quot; \\h \\z \\u"><w:r><w:t>Open in Word and update this field to populate the contents.</w:t></w:r></w:fldSimple></w:p>'); continue
        ppr = []
        if p.break_before: ppr.append("<w:pageBreakBefore/>")
        if p.style in {"chapter", "fronthead", "h2", "part"}:
            ppr.append('<w:keepNext/>')
        stylename = {"title":"BookTitle", "subtitle":"BookSubtitle", "tagline":"Tagline", "author":"AuthorLine", "chapter":"Heading1", "h2":"Heading2", "fronthead":"FrontHead", "part":"PartTitle"}.get(p.style, "Normal")
        ppr.insert(0, f'<w:pStyle w:val="{stylename}"/>')
        runs = f'<w:r><w:t xml:space="preserve">{xml_text(p.text)}</w:t></w:r>' if p.text else ""
        doc_paras.append(f'<w:p><w:pPr>{"".join(ppr)}</w:pPr>{runs}</w:p>')
    sect = '<w:sectPr><w:headerReference w:type="default" r:id="rId2"/><w:footerReference w:type="default" r:id="rId3"/><w:pgSz w:w="8640" w:h="12960"/><w:pgMar w:top="1080" w:right="900" w:bottom="1080" w:left="1080" w:header="480" w:footer="480" w:gutter="180"/></w:sectPr>'
    doc = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{W}" xmlns:r="{rels}"><w:body>{"".join(doc_paras)}{sect}</w:body></w:document>'
    styles = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="{W}">
    <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="300" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
    <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="22"/></w:rPr><w:pPr><w:spacing w:after="120" w:line="300" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr></w:style>
    <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="280" w:after="220"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:b/><w:color w:val="173F35"/><w:sz w:val="32"/></w:rPr></w:style>
    <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="220" w:after="100"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:b/><w:color w:val="173F35"/><w:sz w:val="24"/></w:rPr></w:style>
    <w:style w:type="paragraph" w:styleId="FrontHead"><w:name w:val="Front matter heading"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:jc w:val="center"/><w:spacing w:before="360" w:after="260"/></w:pPr><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:b/><w:color w:val="0B1A3A"/><w:sz w:val="32"/></w:rPr></w:style>
    <w:style w:type="paragraph" w:styleId="BookTitle"><w:name w:val="Book Title"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:before="1800" w:after="800"/></w:pPr><w:rPr><w:b/><w:sz w:val="56"/><w:color w:val="0B1A3A"/></w:rPr></w:style>
    <w:style w:type="paragraph" w:styleId="BookSubtitle"><w:name w:val="Book Subtitle"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:after="480"/></w:pPr><w:rPr><w:sz w:val="28"/><w:color w:val="173F35"/></w:rPr></w:style>
    <w:style w:type="paragraph" w:styleId="Tagline"><w:name w:val="Tagline"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:after="900"/></w:pPr><w:rPr><w:i/><w:sz w:val="22"/><w:color w:val="A46A14"/></w:rPr></w:style>
    <w:style w:type="paragraph" w:styleId="AuthorLine"><w:name w:val="Author Line"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/></w:pPr><w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style>
    <w:style w:type="paragraph" w:styleId="PartTitle"><w:name w:val="Part Title"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:before="2400" w:after="600"/></w:pPr><w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="173F35"/></w:rPr></w:style>
    </w:styles>'''
    header = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:hdr xmlns:w="{W}"><w:p><w:pPr><w:jc w:val="center"/><w:pBdr><w:bottom w:val="single" w:sz="4" w:color="A46A14"/></w:pBdr></w:pPr><w:r><w:rPr><w:i/><w:sz w:val="18"/></w:rPr><w:t>{TITLE}</w:t></w:r></w:p></w:hdr>'
    footer = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:ftr xmlns:w="{W}"><w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>'
    settings = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings xmlns:w="{W}"><w:updateFields w:val="true"/></w:settings>'
    relroot = "http://schemas.openxmlformats.org/package/2006/relationships"
    pkgrels = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{relroot}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/><Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/></Relationships>'
    content_types = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/><Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/><Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/></Types>'
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{relroot}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr("word/document.xml", doc)
        z.writestr("word/styles.xml", styles)
        z.writestr("word/header1.xml", header)
        z.writestr("word/footer1.xml", footer)
        z.writestr("word/settings.xml", settings)
        z.writestr("word/_rels/document.xml.rels", pkgrels)


def build_cover(page_count: int) -> None:
    # KDP-style 6 x 9 paperback wrap, black ink on cream stock, no interior bleed.
    bleed = 0.125 * 72
    trim_w, trim_h = 6 * 72, 9 * 72
    spine = page_count * 0.0025 * 72
    total_w = bleed * 2 + trim_w * 2 + spine
    total_h = bleed * 2 + trim_h
    back_x = bleed
    spine_x = back_x + trim_w
    front_x = spine_x + spine
    # PDF vector art, all coordinates are points with a bottom-left origin.
    c = []
    def rect(x,y,w,h,color): c.append(f"{color[0]} {color[1]} {color[2]} rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f")
    def line(x1,y1,x2,y2,color=(0.78,0.52,0.14),width=1): c.append(f"{color[0]} {color[1]} {color[2]} RG {width} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")
    def circle(x,y,r,color):
        k=r*0.55228475
        c.append(f"{color[0]} {color[1]} {color[2]} rg {x-r:.2f} {y:.2f} m {x-r:.2f} {y+k:.2f} {x-k:.2f} {y+r:.2f} {x:.2f} {y+r:.2f} c {x+k:.2f} {y+r:.2f} {x+r:.2f} {y+k:.2f} {x+r:.2f} {y:.2f} c {x+r:.2f} {y-k:.2f} {x+k:.2f} {y-r:.2f} {x:.2f} {y-r:.2f} c {x-k:.2f} {y-r:.2f} {x-r:.2f} {y-k:.2f} {x-r:.2f} {y:.2f} c f")
    def txt(text,x,y,size,font="Times-Roman",color=(0.05,0.09,0.20),rotate=False):
        c.append(f"{color[0]} {color[1]} {color[2]} rg BT /{font} {size:.2f} Tf {('0 1 -1 0' if rotate else '1 0 0 1')} {x:.2f} {y:.2f} Tm {pdf_escape(text)} Tj ET")

    cream=(0.98,0.96,0.90); navy=(0.03,0.09,0.22); green=(0.04,0.22,0.15); gold=(0.80,0.54,0.15)
    # Full-wrap background and panel grounds.
    rect(0,0,total_w,total_h,cream)
    rect(0,0,bleed,total_h,navy); rect(total_w-bleed,0,bleed,total_h,navy)
    rect(back_x,bleed,trim_w,trim_h,cream)
    rect(spine_x,bleed,spine,trim_h,navy)
    rect(front_x,bleed,trim_w,trim_h,(0.86,0.92,0.92))
    # Back panel.
    bx=back_x+29
    txt("FROM SERENITY WITHIN TO PEACE FOR HUMANITY",bx,total_h-51,11,"Times-Bold",navy)
    txt("A ROADMAP FOR A BETTER FUTURE",bx,total_h-68,10,"Times-Bold",navy)
    line(bx,total_h-82,back_x+trim_w-28,total_h-82,gold,1.1)
    blurb=("This book presents a comprehensive philosophy of human development rooted in serenity, tranquillity and sustainability. It explores how personal values, strong institutions, inclusive communities, responsible governance and international cooperation can create a world that is peaceful, prosperous and just.")
    yy=total_h-106
    for ln in wrap_text(blurb,trim_w-58,8.9,"Times-Roman"):
        txt(ln,bx,yy,8.9,"Times-Roman",(0.08,0.08,0.10)); yy-=12
    yy-=7
    txt("WRITTEN FOR INDIVIDUALS, FAMILIES, LEADERS, PRACTITIONERS,",bx,yy,8.2,"Times-Bold",green); yy-=12
    txt("SCHOLARS AND POLICY-MAKERS, THIS BOOK PROVIDES:",bx,yy,8.2,"Times-Bold",green); yy-=18
    bullets=[
        "Practical insights for personal wellbeing and responsible living",
        "Guidance for building harmonious families and resilient communities",
        "Principles for good governance, institutional integrity and national development",
        "Strategies for sustainable economies, environmental stewardship and human development",
        "Perspectives on peace, international cooperation and global sustainability",
        "A future agenda for humanity that promotes dignity, justice and hope",
    ]
    for b in bullets:
        circle(bx+4,yy+2,2.1,gold)
        for ln in wrap_text(b,trim_w-75,8.2,"Times-Roman"):
            txt(ln,bx+13,yy,8.2,"Times-Roman",navy); yy-=11
        yy-=5
    yy-=4
    txt("ABOUT THE AUTHOR",bx,yy,9,"Times-Bold",navy); yy-=14
    bio=("Prof. Johnson Agharese Egonmwan is a Nigerian scholar, public administrator, development-policy specialist and international consultant. An alumnus of the International Institute of Social Studies, The Hague, he has served in senior public-sector positions and consulted on governance and public financial management reform. His writing advocates human dignity, institutional integrity, responsible leadership and sustainable development.")
    for ln in wrap_text(bio,trim_w-58,7.8,"Times-Roman"):
        if yy < bleed+90: break
        txt(ln,bx,yy,7.8,"Times-Roman",(0.08,0.08,0.10)); yy-=10.2
    # Publisher/barcode reserve; the print platform can place the validated barcode here.
    rect(back_x+trim_w-126,bleed+22,105,52,(1,1,1))
    line(back_x+trim_w-126,bleed+22,back_x+trim_w-21,bleed+22,(0.7,0.7,0.7),0.5)
    txt("ISBN 978-978-965-123-4",bx,bleed+42,7.2,"Times-Roman",navy)
    # Spine.
    txt("SERENITY AND TRANQUILLITY",spine_x+spine/2-7,bleed+137,10,"Times-Bold",(0.95,0.75,0.30),True)
    txt("PROF. JOHNSON AGHARESE EGONMWAN",spine_x+spine/2+11,bleed+137,7.2,"Times-Roman",(1,1,1),True)
    # Front: sky, sun, hills, river, skyline, wind turbine, solar panels, family silhouettes.
    fx=front_x; fy=bleed
    rect(fx,fy,trim_w,trim_h,(0.84,0.91,0.93))
    circle(fx+trim_w*0.77,fy+trim_h*0.45,46,(1.0,0.82,0.48))
    # Golden horizon and layered green landscape.
    rect(fx,fy+trim_h*.18,trim_w,trim_h*.15,(0.94,0.77,0.47))
    rect(fx,fy+trim_h*.13,trim_w,trim_h*.10,(0.42,0.55,0.34))
    rect(fx,fy+trim_h*.05,trim_w,trim_h*.12,green)
    # City skyline.
    buildings=[(0.08,.25,.10,.28),(0.20,.24,.10,.34),(0.32,.23,.12,.42),(0.47,.23,.10,.36),(0.59,.24,.11,.30),(0.73,.24,.12,.33),(0.86,.24,.08,.26)]
    for xx,yy0,ww,hh in buildings:
        rect(fx+trim_w*xx,fy+trim_h*yy0,trim_w*ww,trim_h*hh,(0.40,0.47,0.45))
        for wy in range(3):
            for wx in range(2): rect(fx+trim_w*(xx+.02+wx*.035),fy+trim_h*(yy0+.03+wy*.07),5,5,(0.94,0.79,0.48))
    # River and shoreline highlights.
    c.append(f"0.67 0.79 0.78 rg {fx:.2f} {fy+trim_h*.12:.2f} m {fx+trim_w*.28:.2f} {fy+trim_h*.20:.2f} {fx+trim_w*.68:.2f} {fy+trim_h*.10:.2f} {fx+trim_w:.2f} {fy+trim_h*.18:.2f} l {fx+trim_w:.2f} {fy+trim_h*.08:.2f} l {fx:.2f} {fy+trim_h*.08:.2f} l f")
    # Windmill.
    wx=fx+trim_w*.91; wy=fy+trim_h*.37
    line(wx,wy-5,wx,wy+125,(0.91,0.93,0.88),2)
    circle(wx,wy+125,4,(0.91,0.93,0.88))
    for ang in [0,120,240]:
        import math
        a=math.radians(ang); line(wx,wy+125,wx+65*math.cos(a),wy+125+65*math.sin(a),(0.91,0.93,0.88),2)
    # Solar panels.
    rect(fx+trim_w*.68,fy+trim_h*.16,trim_w*.26,trim_h*.075,(0.08,0.19,0.29))
    for k in range(1,5): line(fx+trim_w*(.68+.26*k/5),fy+trim_h*.16,fx+trim_w*(.68+.26*k/5),fy+trim_h*.235,(0.43,0.65,0.68),0.6)
    line(fx+trim_w*.68,fy+trim_h*.197,fx+trim_w*.94,fy+trim_h*.197,(0.43,0.65,0.68),0.6)
    # Family silhouettes on a path.
    family=[(.35,0,15,43),(.43,0,15,47),(.30,0,11,29),(.49,0,10,30),(.56,0,9,25)]
    for px,_,head,body in family:
        cx=fx+trim_w*px; base=fy+trim_h*.16
        circle(cx,base+body+head*.36,head*.36,navy)
        line(cx,base,cx,base+body,navy,head*.52)
        line(cx,base+body*.55,cx-head*.55,base+body*.20,navy,head*.27)
        line(cx,base+body*.55,cx+head*.55,base+body*.18,navy,head*.27)
        line(cx,base,cx-head*.32,base-15,navy,head*.24)
        line(cx,base,cx+head*.30,base-15,navy,head*.24)
    # Clear title zone and bottom title band.
    rect(fx+22,fy+trim_h*.62,trim_w-44,trim_h*.35,(0.91,0.95,0.94))
    txt("SERENITY",fx+47,fy+trim_h*.90,31,"Times-Bold",navy)
    txt("AND",fx+172,fy+trim_h*.855,13,"Times-Roman",gold)
    txt("TRANQUILLITY",fx+31,fy+trim_h*.80,29,"Times-Bold",green)
    subtitle_lines=wrap_text("IN PERSONAL LIFE, COMMUNITY LIFE, NATIONAL DEVELOPMENT AND THE FUTURE OF HUMANITY",trim_w-50,9.3,"Times-Bold")
    sy=fy+trim_h*.735
    for ln in subtitle_lines:
        txt(ln,fx+25,sy,9.3,"Times-Bold",navy); sy-=13
    tagline_lines=wrap_text(TAGLINE,trim_w-52,9,"Times-Italic")
    sy=fy+trim_h*.635
    for ln in tagline_lines:
        txt(ln,fx+25,sy,9,"Times-Italic",green); sy-=12
    rect(fx,fy,trim_w,trim_h*.13,navy)
    txt("TOWARDS A MORE SERENE, TRANQUIL AND SUSTAINABLE WORLD",fx+20,fy+trim_h*.095,8.5,"Times-Bold",(0.98,0.79,0.34))
    txt(AUTHOR.upper(),fx+62,fy+trim_h*.050,8.2,"Times-Bold",(1,1,1))
    # Gutter fold guides are subtle and remain outside the visible trim.
    stream="\n".join(c).encode("latin-1",errors="replace")
    pdf=bytearray(b"%PDF-1.7\n")
    objects=[]
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {total_w:.2f} {total_h:.2f}] /Resources << /Font << /Times-Roman 4 0 R /Times-Bold 5 0 R /Times-Italic 6 0 R >> >> /Contents 7 0 R >>".encode("ascii"))
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman /Encoding /WinAnsiEncoding >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Bold /Encoding /WinAnsiEncoding >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Italic /Encoding /WinAnsiEncoding >>")
    objects.append(b"<< /Length "+str(len(stream)).encode()+b" >>\nstream\n"+stream+b"\nendstream")
    data=bytearray(b"%PDF-1.7\n%\xE2\xE3\xCF\xD3\n"); offs=[0]
    for n,obj in enumerate(objects,1): offs.append(len(data)); data.extend(f"{n} 0 obj\n".encode()); data.extend(obj); data.extend(b"\nendobj\n")
    xref=len(data); data.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for off in offs[1:]: data.extend(f"{off:010d} 00000 n \n".encode())
    data.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    (ROOT/"Serenity_and_Tranquillity_Print_Cover_KDP_6x9_cream.pdf").write_bytes(data)

    # Editable vector front cover at exact 6 x 9 trim size.
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="6in" height="9in" viewBox="0 0 432 648">
    <defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="#d6e7ed"/><stop offset="1" stop-color="#fff0cf"/></linearGradient></defs>
    <rect width="432" height="648" fill="url(#sky)"/><circle cx="330" cy="355" r="46" fill="#ffd987"/>
    <rect y="495" width="432" height="153" fill="#123b2b"/><path d="M0 485 Q110 438 205 477 T432 470 V535 H0Z" fill="#64834e"/>
    <path d="M0 513 Q120 476 260 516 T432 495 V560 H0Z" fill="#82a2a1"/>
    <g fill="#667874"><path d="M45 485V355h36v130zm48 0V330h42v155zm52 0V300h48v185zm58 0V337h41v148zm52 0V360h40v125zm50 0V328h36v157z"/></g>
    <g fill="#f2d493"><path d="M53 370h5v8h-5zm17 0h5v8h-5zM101 345h6v9h-6zm20 0h6v9h-6zM158 316h6v9h-6zm23 0h6v9h-6zM215 351h6v9h-6zm19 0h6v9h-6z"/></g>
    <g stroke="#f2f1e8" stroke-width="3"><path d="M377 340v125M377 340l44-38m-44 38-12-54m12 54 50 8"/></g>
    <g fill="#102544"><circle cx="150" cy="485" r="8"/><path d="M145 493h10l7 34h-24zm-4 19-12 16m25-16 11 16m-20-18-13-11m18 0 12 8"/><circle cx="190" cy="480" r="8"/><path d="M184 488h12l8 39h-28zm-5 19-12 16m24-16 12 16m-20-20-10-11m18 0 12 9"/><circle cx="125" cy="498" r="6"/><path d="M121 504h8l5 23h-18zm-3 12-7 12m15-12 8 12"/></g>
    <rect x="16" y="35" width="400" height="263" rx="6" fill="#f6f5ef" fill-opacity=".92"/>
    <text x="216" y="104" text-anchor="middle" fill="#0b1a3a" font-family="Georgia,serif" font-size="44" font-weight="bold">SERENITY</text>
    <text x="216" y="139" text-anchor="middle" fill="#a46a14" font-family="Georgia,serif" font-size="18">AND</text>
    <text x="216" y="192" text-anchor="middle" fill="#173f35" font-family="Georgia,serif" font-size="37" font-weight="bold">TRANQUILLITY</text>
    <text x="216" y="224" text-anchor="middle" fill="#0b1a3a" font-family="Arial,sans-serif" font-size="10" font-weight="bold"><tspan x="216">IN PERSONAL LIFE, COMMUNITY LIFE,</tspan><tspan x="216" dy="16">NATIONAL DEVELOPMENT AND THE FUTURE</tspan><tspan x="216" dy="16">OF HUMANITY</tspan></text>
    <text x="216" y="276" text-anchor="middle" fill="#173f35" font-family="Georgia,serif" font-size="9" font-style="italic"><tspan x="216">A Philosophy for Sustainable Development, Peaceful</tspan><tspan x="216" dy="13">Coexistence and a Better Future</tspan></text>
    <rect y="555" width="432" height="93" fill="#061633"/><text x="216" y="584" text-anchor="middle" fill="#f6c756" font-family="Georgia,serif" font-size="9" font-weight="bold">TOWARDS A MORE SERENE, TRANQUIL</text><text x="216" y="598" text-anchor="middle" fill="#f6c756" font-family="Georgia,serif" font-size="9" font-weight="bold">AND SUSTAINABLE WORLD</text><text x="216" y="625" text-anchor="middle" fill="#fff" font-family="Georgia,serif" font-size="13">PROF. JOHNSON AGHARESE EGONMWAN</text></svg>'''
    (ROOT/"Serenity_and_Tranquillity_Cover_Front.svg").write_text(svg,encoding="utf-8")


if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    content, toc = manuscript()
    docx = ROOT / "Serenity_and_Tranquillity_Interior_Edit.docx"
    build_docx(content, docx)
    print_pdf = ROOT / "Serenity_and_Tranquillity_Print_Interior.pdf"
    print_pages = render_pdf(content, toc, "print", print_pdf)
    digital_pdf = ROOT / "Serenity_and_Tranquillity_Digital_Readable.pdf"
    digital_pages = render_pdf(content, toc, "digital", digital_pdf)
    build_cover(print_pages)
    notes = f'''# Production notes

## Interior editions

- Print interior: 6 x 9 in, {print_pages} pages, black text, no bleed.
- Screen PDF: A4, {digital_pages} pages, with a vector cover page, clickable table of contents, and PDF chapter bookmarks.
- Editable source: 6 x 9 in DOCX. Its table of contents is a Word field and can be refreshed after edits.

The supplied front matter had a contents page for an earlier 18-chapter version, while the manuscript contains 25 chapters. The rebuilt contents follows the supplied chapters. The unsupported lists of figures and tables were removed because no corresponding figures or tables were present. The source chapters had very many small numbered sections; headings were consolidated and renumbered while their body text was retained.

## Cover assumptions

The one-page wrap PDF is sized for a 6 x 9 in KDP paperback on cream paper, using the final {print_pages}-page interior. The calculated spine is {print_pages*0.0025:.4f} in; the wrap is {(0.25+12+print_pages*0.0025):.4f} x 9.25 in including bleed. Other printers may use different paper calipers or templates; use their cover template before upload.

The ISBN text is retained exactly as supplied: 978-978-965-123-4. The barcode panel is intentionally blank; KDP can add a barcode when a cover is uploaded without one. The ISBN's final digit does not pass the ISBN-13 checksum, so this number may need publisher or retailer verification before listing.
'''
    (ROOT/"Production_Notes.md").write_text(notes, encoding="utf-8")
    print(f"DOCX: {docx.name}")
    print(f"Print interior: {print_pdf.name} ({print_pages} pages, 6 x 9 in)")
    print(f"Digital PDF: {digital_pdf.name} ({digital_pages} pages, A4)")
    print("Print cover: Serenity_and_Tranquillity_Print_Cover_KDP_6x9_cream.pdf (6 x 9 trim; cream-paper spine basis)")
