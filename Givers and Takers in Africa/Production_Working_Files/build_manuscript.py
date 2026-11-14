from __future__ import annotations

from html import escape
from pathlib import Path
import re
import zipfile


BASE = Path(__file__).resolve().parent
SOURCES = BASE / "Source_Materials"
WORK = BASE / "Working_Manuscript"
WORK.mkdir(exist_ok=True)

TITLE = "Givers and Takers in Africa"
SUBTITLE = (
    "The Politics of Self-Interest, Generosity, Leadership and Sustainable "
    "Development: With Special Focus on Nigeria"
)
AUTHOR = "Prof. Johnson Agharese Egonmwan"
PUBLISHER = "Resyin Publications (NG) Inc."
PRINT_ISBN = "978-978-59760-5-2"

WORDS = (
    "ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN ELEVEN TWELVE "
    "THIRTEEN FOURTEEN FIFTEEN"
).split()
CHAPTER_RE = re.compile(r"(?m)^CHAPTER (" + "|".join(WORDS) + r")\s*$")
SECTION_RE = re.compile(r"^\d+\.\d+\s+")
TOP_BACK_RE = re.compile(r"^\d+\.\s+[A-Z][A-Z'’ &:-]{4,}$")


def lines(text: str) -> list[str]:
    return [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n") if line.strip()]


def chapter_chunks(path: Path) -> list[tuple[int, str, str, list[str]]]:
    text = path.read_text(encoding="utf-8-sig")
    matches = list(CHAPTER_RE.finditer(text))
    result = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        chunk = text[match.start():end]
        for marker in ("\nNEXT INSTALMENT", "\nEND OF MAIN MANUSCRIPT"):
            pos = chunk.find(marker)
            if pos >= 0:
                chunk = chunk[:pos]
        chunk_lines = lines(chunk)
        chapter_word = match.group(1)
        number = WORDS.index(chapter_word) + 1
        if len(chunk_lines) < 2:
            raise ValueError(f"Incomplete chapter in {path.name}: {chapter_word}")
        result.append((number, chunk_lines[0], chunk_lines[1], chunk_lines[2:]))
    return result


def collect_chapters() -> list[tuple[int, str, str, list[str]]]:
    first = (SOURCES / "Author_Brief_and_Chapters_1-3.txt").read_text(encoding="utf-8-sig")
    start_match = re.search(r"(?m)^CHAPTER ONE\s*$", first)
    stop_match = re.search(r"(?m)^3\. DIRECTION FOR THE REMAINING CHAPTERS\s*$", first)
    if not start_match or not stop_match or start_match.start() >= stop_match.start():
        raise ValueError("Could not locate the manuscript-only boundary in the first source file")
    first_work = first[start_match.start():stop_match.start()]
    # Repair one damaged citation in the working copy. The unmodified source remains in Source_Materials.
    first_work, count = re.subn(
        r"\s*\ufffd\s*afrobarometer\.org\b",
        " (Afrobarometer, 6 May 2025).",
        first_work,
        count=1,
        flags=re.IGNORECASE,
    )
    if count != 1:
        raise ValueError("Expected the damaged Afrobarometer citation exactly once")
    first_path = WORK / "Chapters_1-3_Source_Extract.txt"
    first_path.write_text(first_work.rstrip() + "\n", encoding="utf-8", newline="")
    chapters = chapter_chunks(first_path)
    for name in ("Chapters_4-8.txt", "Chapters_9-13.txt", "Chapters_14-15.txt"):
        chapters.extend(chapter_chunks(SOURCES / name))
    chapters.sort(key=lambda item: item[0])
    expected = list(range(1, 16))
    actual = [item[0] for item in chapters]
    if actual != expected:
        raise ValueError(f"Expected chapters 1-15 in order; found {actual}")
    return chapters


def collect_backmatter() -> list[str]:
    text = (SOURCES / "Back_Matter.txt").read_text(encoding="utf-8-sig")
    start = re.search(r"(?m)^BACK MATTER\s*$", text)
    end = re.search(r"(?m)^END OF BACK MATTER\s*$", text)
    if not start or not end or start.start() >= end.start():
        raise ValueError("Could not locate the back-matter boundaries")
    body = lines(text[start.end():end.start()])
    # This sentence is an editorial instruction embedded in the supplied source, not book prose.
    body = [line for line in body if not line.startswith("The following works provide theoretical and empirical foundations")]
    # Remove repeated identical entries from the editable copy; originals remain untouched.
    seen_references: set[str] = set()
    deduplicated = []
    for line in body:
        if line in {
            "Sen, A. (1999). Development as Freedom. Oxford University Press.",
            "North, D. C. (1990). Institutions, Institutional Change and Economic Performance. Cambridge University Press.",
        }:
            if line in seen_references:
                continue
            seen_references.add(line)
        deduplicated.append(line)
    body = deduplicated
    # Add the complete source for the statistic retained in Chapter One.
    anchor = "D. Africa and Nigerian Development"
    if anchor not in body:
        raise ValueError("Could not locate the bibliography insertion point")
    insert = body.index(anchor) + 1
    body.insert(
        insert,
        "Afrobarometer. (2025, May 6). Nigerians say corruption is worsening, and citizens risk retaliation if they speak up: Afrobarometer survey finds. https://www.afrobarometer.org/articles/nigerians-say-corruption-is-worsening-and-citizens-risk-retaliation-if-they-speak-up-afrobarometer-survey-finds/",
    )
    return body


def xml(value: str) -> str:
    value = "".join(ch for ch in value if ch in "\t\n\r" or ord(ch) >= 32)
    return escape(value, quote=False).replace("\u00a0", " ")


def paragraph(text: str, style: str = "Normal", *, page_break: bool = False) -> str:
    ppr = [f'<w:pStyle w:val="{style}"/>']
    if page_break:
        ppr.append("<w:pageBreakBefore/>")
    run = f'<w:r><w:t xml:space="preserve">{xml(text)}</w:t></w:r>' if text else ""
    return f'<w:p><w:pPr>{"".join(ppr)}</w:pPr>{run}</w:p>'


def recommendations_table(rows: list[list[str]]) -> str:
    widths = [420, 1250, 2680, 1881]
    borders = (
        '<w:tblBorders><w:top w:val="single" w:sz="6" w:color="A9B8B2"/>'
        '<w:left w:val="single" w:sz="4" w:color="D6DDD9"/>'
        '<w:bottom w:val="single" w:sz="6" w:color="A9B8B2"/>'
        '<w:right w:val="single" w:sz="4" w:color="D6DDD9"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="D6DDD9"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="D6DDD9"/></w:tblBorders>'
    )
    table = (
        '<w:tbl><w:tblPr><w:tblW w:w="6231" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
        + borders
        + '</w:tblPr><w:tblGrid>'
        + ''.join(f'<w:gridCol w:w="{width}"/>' for width in widths)
        + '</w:tblGrid>'
    )
    for row_index, row in enumerate(rows):
        table += '<w:tr><w:trPr><w:cantSplit/>'
        if row_index == 0:
            table += '<w:tblHeader/>'
        table += '</w:trPr>'
        for cell_index, value in enumerate(row):
            shade = '<w:shd w:fill="EAF0ED"/>' if row_index == 0 else ''
            bold = '<w:b/>' if row_index == 0 else ''
            table += (
                f'<w:tc><w:tcPr><w:tcW w:w="{widths[cell_index]}" w:type="dxa"/>{shade}</w:tcPr>'
                f'<w:p><w:pPr><w:spacing w:after="60" w:line="240" w:lineRule="auto"/></w:pPr>'
                f'<w:r><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="18"/>{bold}</w:rPr>'
                f'<w:t xml:space="preserve">{xml(value)}</w:t></w:r></w:p></w:tc>'
            )
        table += '</w:tr>'
    return table + '</w:tbl>'


def field_paragraph(instruction: str, fallback: str) -> str:
    return (
        '<w:p><w:pPr><w:pStyle w:val="Normal"/></w:pPr>'
        f'<w:fldSimple w:instr="{escape(instruction, quote=True)}"><w:r><w:t>{xml(fallback)}</w:t></w:r></w:fldSimple></w:p>'
    )


def page_number_footer() -> str:
    return (
        '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>'
    )


def build_docx(chapters: list[tuple[int, str, str, list[str]]], backmatter: list[str], output: Path) -> None:
    doc_paras = [
        paragraph(TITLE.upper(), "BookTitle"),
        paragraph(SUBTITLE, "BookSubtitle"),
        paragraph(AUTHOR, "AuthorLine"),
        paragraph(PUBLISHER, "PublisherLine"),
        paragraph("COPYRIGHT PAGE", "FrontHead", page_break=True),
        paragraph(f"© 2026 {AUTHOR}"),
        paragraph("All rights reserved."),
        paragraph("No part of this publication may be reproduced, stored in a retrieval system, transmitted or distributed in any form or by any means, electronic, mechanical, photocopying, recording or otherwise, without the prior written permission of the author, except for brief quotations used for purposes of review, scholarship or criticism."),
        paragraph("First Edition, 2026"),
        paragraph(f"ISBN {PRINT_ISBN}"),
        paragraph("Published by:"),
        paragraph(PUBLISHER),
        paragraph("Nigeria"),
        paragraph("TABLE OF CONTENTS", "FrontHead", page_break=True),
        field_paragraph('TOC \\o "1-1" \\t "FrontHead,1" \\h \\z \\u', "Open in Word and update this field to populate the contents."),
    ]
    for number, chapter_label, title, body in chapters:
        doc_paras.append(paragraph(chapter_label, "ChapterLabel", page_break=True))
        doc_paras.append(paragraph(title, "Heading1"))
        for text in body:
            style = "Heading2" if SECTION_RE.match(text) else "Normal"
            if text.startswith(("Central Lesson:", "Final Moral Lesson:")):
                style = "Lesson"
            doc_paras.append(paragraph(text, style))
    doc_paras.append(paragraph("BACK MATTER", "FrontHead", page_break=True))
    index = 0
    while index < len(backmatter):
        text = backmatter[index]
        if text == "No.":
            table_lines = backmatter[index:index + 64]
            if len(table_lines) != 64 or table_lines[:4] != ["No.", "Policy Area", "Recommended Action", "Expected Outcome"]:
                raise ValueError("Policy recommendation table does not contain the expected 15 complete rows")
            cells = [table_lines[:4]]
            cells.extend([table_lines[pos:pos + 4] for pos in range(4, 64, 4)])
            doc_paras.append(recommendations_table(cells))
            index += 64
            continue
        if TOP_BACK_RE.match(text):
            style = "FrontHead"
        elif SECTION_RE.match(text) or re.match(r"^(?:[A-H]\.\s|Article \d+:|Preamble$|The Charter's Guiding Principle:)", text):
            style = "Heading2"
        elif re.match(r"^[A-Z][A-Za-z'’ -]+:\s", text):
            style = "Glossary"
        else:
            style = "Normal"
        doc_paras.append(paragraph(text, style))
        index += 1

    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    body_xml = "".join(doc_paras)
    sect = (
        '<w:sectPr><w:headerReference w:type="default" r:id="rId2"/>'
        '<w:footerReference w:type="default" r:id="rId3"/>'
        '<w:pgSz w:w="8640" w:h="12960"/>'
        '<w:pgMar w:top="1080" w:right="900" w:bottom="1080" w:left="1080" w:header="480" w:footer="480" w:gutter="180"/>'
        '</w:sectPr>'
    )
    document = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W}" xmlns:r="{R}"><w:body>{body_xml}{sect}</w:body></w:document>'
    )
    styles = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <w:styles xmlns:w="{W}">
      <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia" w:eastAsia="Georgia"/><w:lang w:val="en-GB"/><w:sz w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="300" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
      <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="22"/></w:rPr><w:pPr><w:jc w:val="both"/><w:widowControl/></w:pPr></w:style>
      <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="420" w:after="220"/><w:outlineLvl w:val="0"/><w:jc w:val="center"/></w:pPr><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:b/><w:color w:val="173F35"/><w:sz w:val="32"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="220" w:after="100"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:b/><w:color w:val="173F35"/><w:sz w:val="24"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="BookTitle"><w:name w:val="Book Title"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:before="2100" w:after="500"/></w:pPr><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:b/><w:sz w:val="56"/><w:color w:val="0B1A3A"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="BookSubtitle"><w:name w:val="Book Subtitle"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:after="600"/></w:pPr><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="24"/><w:color w:val="173F35"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="AuthorLine"><w:name w:val="Author Line"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:before="400"/></w:pPr><w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="PublisherLine"><w:name w:val="Publisher Line"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:before="180"/></w:pPr><w:rPr><w:sz w:val="22"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="ChapterLabel"><w:name w:val="Chapter Label"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:jc w:val="center"/><w:spacing w:before="1400" w:after="160"/></w:pPr><w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="A46A14"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="FrontHead"><w:name w:val="Front Matter Heading"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:jc w:val="center"/><w:spacing w:before="360" w:after="260"/></w:pPr><w:rPr><w:b/><w:color w:val="0B1A3A"/><w:sz w:val="32"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="Lesson"><w:name w:val="Central Lesson"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="180" w:after="220"/></w:pPr><w:rPr><w:i/><w:color w:val="173F35"/></w:rPr></w:style>
      <w:style w:type="paragraph" w:styleId="Glossary"><w:name w:val="Glossary Entry"/><w:basedOn w:val="Normal"/><w:pPr><w:keepLines/></w:pPr><w:rPr><w:sz w:val="21"/></w:rPr></w:style>
    </w:styles>'''
    header = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:hdr xmlns:w="{W}"><w:p><w:pPr><w:jc w:val="center"/><w:pBdr><w:bottom w:val="single" w:sz="4" w:color="A46A14"/></w:pBdr></w:pPr>'
        f'<w:r><w:rPr><w:i/><w:sz w:val="18"/></w:rPr><w:t>{xml(TITLE.upper())}</w:t></w:r></w:p></w:hdr>'
    )
    footer = page_number_footer()
    settings = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings xmlns:w="{W}"><w:updateFields w:val="true"/></w:settings>'
    relroot = "http://schemas.openxmlformats.org/package/2006/relationships"
    package_rels = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{relroot}">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>'
    )
    doc_rels = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{relroot}">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
        '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
        '</Relationships>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
        '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
        '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
        '</Types>'
    )
    core = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        f'<dc:title>{xml(TITLE)}</dc:title><dc:subject>{xml(SUBTITLE)}</dc:subject>'
        f'<dc:creator>{xml(AUTHOR)}</dc:creator><dc:language>en-GB</dc:language></cp:coreProperties>'
    )
    app = '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Microsoft Word</Application></Properties>'
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", package_rels)
        archive.writestr("docProps/core.xml", core)
        archive.writestr("docProps/app.xml", app)
        archive.writestr("word/document.xml", document)
        archive.writestr("word/styles.xml", styles)
        archive.writestr("word/header1.xml", header)
        archive.writestr("word/footer1.xml", footer)
        archive.writestr("word/settings.xml", settings)
        archive.writestr("word/_rels/document.xml.rels", doc_rels)


def main() -> None:
    chapters = collect_chapters()
    backmatter = collect_backmatter()
    text_lines = [TITLE.upper(), SUBTITLE, AUTHOR, PUBLISHER, "", "TABLE OF CONTENTS", ""]
    text_lines.extend(f"Chapter {WORDS[n - 1].title()}: {title}" for n, _, title, _ in chapters)
    for number, label, title, body in chapters:
        text_lines.extend(["", label, title, *body])
    text_lines.extend(["", "BACK MATTER", *backmatter, ""])
    (WORK / "Manuscript_Assembly.txt").write_text("\n".join(text_lines), encoding="utf-8", newline="")
    output = WORK / "Givers_and_Takers_in_Africa_Manuscript_Edit.docx"
    build_docx(chapters, backmatter, output)
    words = sum(len(re.findall(r"\b[\w’'-]+\b", line)) for line in text_lines)
    sections = sum(sum(bool(SECTION_RE.match(line)) for line in body) for _, _, _, body in chapters)
    print(f"DOCX: {output}")
    print(f"Chapters: {len(chapters)}; numbered sections: {sections}; approximate words: {words:,}")


if __name__ == "__main__":
    main()
