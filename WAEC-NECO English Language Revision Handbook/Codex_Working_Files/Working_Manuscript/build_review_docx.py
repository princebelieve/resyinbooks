from __future__ import annotations

from html import escape
from pathlib import Path
import re
import zipfile


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "WAEC_NECO_English_Language_Revision_Handbook_Assembly_Draft.md"
OUTPUT = HERE.parents[1] / "For_Professor" / "WAEC_NECO_English_Language_Revision_Handbook_Editorial_Review_Draft.docx"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def run(text: str, *, bold: bool = False, italic: bool = False, size: int = 22, color: str | None = None) -> str:
    if not text:
        return ""
    props = []
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    props.append(f'<w:sz w:val="{size}"/>')
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    return f'<w:r><w:rPr>{"".join(props)}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def formatted_runs(value: str, *, size: int = 22) -> str:
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", value)
    chunks = re.split(r"(\*\*.*?\*\*|\*.*?\*)", value)
    out = []
    for chunk in chunks:
        if chunk.startswith("**") and chunk.endswith("**"):
            out.append(run(chunk[2:-2], bold=True, size=size))
        elif chunk.startswith("*") and chunk.endswith("*"):
            out.append(run(chunk[1:-1], italic=True, size=size))
        else:
            out.append(run(chunk, size=size))
    return "".join(out)


def paragraph(value: str = "", *, style: str = "Normal", page_break: bool = False) -> str:
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if page_break:
        ppr.append("<w:pageBreakBefore/>")
    if style == "Normal":
        ppr.append('<w:spacing w:after="100" w:line="300" w:lineRule="auto"/>')
    return f'<w:p><w:pPr>{"".join(ppr)}</w:pPr>{formatted_runs(value)}</w:p>'


def table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    col_count = max(len(row) for row in rows)
    widths = [int(9360 / col_count)] * col_count
    result = ['<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/><w:tblBorders>'
              '<w:top w:val="single" w:sz="4" w:color="B8C7D9"/>'
              '<w:left w:val="single" w:sz="4" w:color="B8C7D9"/>'
              '<w:bottom w:val="single" w:sz="4" w:color="B8C7D9"/>'
              '<w:right w:val="single" w:sz="4" w:color="B8C7D9"/>'
              '<w:insideH w:val="single" w:sz="4" w:color="B8C7D9"/>'
              '<w:insideV w:val="single" w:sz="4" w:color="B8C7D9"/>'
              '</w:tblBorders></w:tblPr>']
    for row_index, cells in enumerate(rows):
        cells = cells + [""] * (col_count - len(cells))
        result.append("<w:tr>")
        for index, value in enumerate(cells):
            shading = '<w:shd w:fill="DCE6F1"/>' if row_index == 0 else ""
            cell_runs = formatted_runs(value, size=20)
            if row_index == 0:
                cell_runs = formatted_runs(value, size=20)
                cell_runs = cell_runs.replace("<w:rPr>", "<w:rPr><w:b/>")
            result.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{widths[index]}" w:type="dxa"/>{shading}</w:tcPr>'
                f'<w:p><w:pPr><w:spacing w:after="50"/></w:pPr>{cell_runs}</w:p></w:tc>'
            )
        result.append("</w:tr>")
    result.append("</w:tbl>")
    return "".join(result)


def toc_field() -> str:
    return (
        '<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        f'{run("Open in Word and update the table of contents (F9).", italic=True, size=20)}'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'
    )


def make_body(text: str) -> str:
    # Skip the Markdown title banner; the DOCX title page supplies a review label.
    marker = "---\n"
    text = text[text.find(marker) + len(marker):]
    lines = text.splitlines()
    output = []
    pending_table: list[list[str]] = []
    next_chapter_title = False
    in_first_chapter = True

    def flush_table() -> None:
        nonlocal pending_table
        if pending_table:
            if len(pending_table) > 1 and all(re.fullmatch(r":?-{2,}:?", cell.replace(" ", "")) for cell in pending_table[1]):
                pending_table.pop(1)
            output.append(table(pending_table))
            pending_table = []

    for raw in lines:
        line = raw.strip()
        if line.startswith("|"):
            cells = [item.strip() for item in line.strip("|").split("|")]
            pending_table.append(cells)
            continue
        flush_table()
        if not line or line == "---":
            continue
        if line.startswith("# "):
            heading = line[2:].strip()
            output.append(paragraph(heading, style="Heading1", page_break=not in_first_chapter))
            in_first_chapter = False
            next_chapter_title = True
            continue
        if line.startswith("## "):
            heading = line[3:].strip()
            output.append(paragraph(heading, style="Heading2"))
            continue
        if line.startswith("### "):
            output.append(paragraph(line[4:].strip(), style="Heading3"))
            continue
        if re.match(r"^\d+(?:\.\d+)+\s+", line):
            output.append(paragraph(line, style="Heading3"))
            continue
        if re.match(r"^Chapter (One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen)$", line):
            output.append(paragraph(line, style="Heading1", page_break=not in_first_chapter))
            in_first_chapter = False
            next_chapter_title = True
            continue
        if next_chapter_title and not line.startswith(("**", "- ")):
            output.append(paragraph(line, style="Heading2"))
            next_chapter_title = False
            continue
        next_chapter_title = False
        if line.startswith("- ") or line.startswith("* "):
            output.append(paragraph("•  " + line[2:], style="Normal"))
        else:
            output.append(paragraph(line))
    flush_table()
    return "".join(output)


normal = '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="22"/><w:lang w:val="en-GB"/></w:rPr></w:style>'
heading1 = '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="0" w:after="240"/></w:pPr><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:b/><w:color w:val="0B2C62"/><w:sz w:val="32"/></w:rPr></w:style>'
heading2 = '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="220" w:after="120"/></w:pPr><w:rPr><w:b/><w:color w:val="0B2C62"/><w:sz w:val="27"/></w:rPr></w:style>'
heading3 = '<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="160" w:after="80"/></w:pPr><w:rPr><w:b/><w:color w:val="167340"/><w:sz w:val="23"/></w:rPr></w:style>'
contents_title = '<w:style w:type="paragraph" w:styleId="ContentsTitle"><w:name w:val="Contents Title"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:after="240"/></w:pPr><w:rPr><w:b/><w:color w:val="0B2C62"/><w:sz w:val="32"/></w:rPr></w:style>'
cover_kicker = '<w:style w:type="paragraph" w:styleId="CoverKicker"><w:name w:val="Cover Kicker"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:after="320"/></w:pPr><w:rPr><w:b/><w:color w:val="B48612"/><w:sz w:val="30"/></w:rPr></w:style>'
cover_title = '<w:style w:type="paragraph" w:styleId="CoverTitle"><w:name w:val="Cover Title"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:after="360"/></w:pPr><w:rPr><w:b/><w:color w:val="0B2C62"/><w:sz w:val="36"/></w:rPr></w:style>'
cover_author = '<w:style w:type="paragraph" w:styleId="CoverAuthor"><w:name w:val="Cover Author"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:before="600" w:after="320"/></w:pPr><w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style>'
draft_label = '<w:style w:type="paragraph" w:styleId="DraftLabel"><w:name w:val="Draft Label"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:before="520" w:after="160"/></w:pPr><w:rPr><w:b/><w:color w:val="9D2525"/><w:sz w:val="22"/></w:rPr></w:style>'
cover_note = '<w:style w:type="paragraph" w:styleId="CoverNote"><w:name w:val="Cover Note"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/></w:pPr><w:rPr><w:color w:val="555555"/><w:sz w:val="20"/></w:rPr></w:style>'
styles = f'<?xml version="1.0" encoding="UTF-8"?><w:styles xmlns:w="{W}"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="22"/><w:lang w:val="en-GB"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:widowControl/></w:pPr></w:pPrDefault></w:docDefaults>{normal}{heading1}{heading2}{heading3}{contents_title}{cover_kicker}{cover_title}{cover_author}{draft_label}{cover_note}</w:styles>'

body = [
    paragraph("THE COMPLETE WAEC/NECO", style="CoverKicker"),
    paragraph("ENGLISH LANGUAGE REVISION HANDBOOK", style="CoverTitle"),
    paragraph("Prof. Johnson Agharese Egonmwan", style="CoverAuthor"),
    paragraph("EDITORIAL REVIEW DRAFT - NOT FOR PUBLICATION", style="DraftLabel"),
    paragraph("Working text assembled for review. The title, imprint, ISBN, examination claims and final chapter structure require approval.", style="CoverNote"),
    '<w:p><w:r><w:br w:type="page"/></w:r></w:p>',
    paragraph("Contents", style="ContentsTitle"),
    toc_field(),
    '<w:p><w:r><w:br w:type="page"/></w:r></w:p>',
    make_body(SOURCE.read_text(encoding="utf-8-sig")),
]

footer = (
    f'<w:ftr xmlns:w="{W}"><w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
    '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
    '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
    '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>'
)
footer_rel = f'<Relationship Id="rId2" Type="{R}/footer" Target="footer1.xml"/>'
document_rels = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    f'<Relationship Id="rId1" Type="{R}/styles" Target="styles.xml"/>{footer_rel}'
    '</Relationships>'
)
document = (
    f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{W}">'
    f'<w:body>{"".join(body)}<w:sectPr><w:footerReference w:type="default" r:id="rId2" xmlns:r="{R}"/>'
    '<w:pgSz w:w="8391" w:h="11906"/><w:pgMar w:top="850" w:right="760" w:bottom="850" w:left="760" w:header="360" w:footer="420"/>'
    '</w:sectPr></w:body></w:document>'
)
content_types = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
    '</Types>'
)
root_rels = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    f'<Relationship Id="rId1" Type="{R}/officeDocument" Target="word/document.xml"/>'
    '</Relationships>'
)
settings = f'<?xml version="1.0" encoding="UTF-8"?><w:settings xmlns:w="{W}"><w:updateFields w:val="true"/></w:settings>'
settings_rel = f'<Relationship Id="rId3" Type="{R}/settings" Target="settings.xml"/>'
document_rels = document_rels.replace('</Relationships>', f'{settings_rel}</Relationships>')
content_types = content_types.replace('</Types>', '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/></Types>')

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as package:
    package.writestr("[Content_Types].xml", content_types)
    package.writestr("_rels/.rels", root_rels)
    package.writestr("word/document.xml", document)
    package.writestr("word/styles.xml", styles)
    package.writestr("word/footer1.xml", footer)
    package.writestr("word/settings.xml", settings)
    package.writestr("word/_rels/document.xml.rels", document_rels)

print(OUTPUT)
