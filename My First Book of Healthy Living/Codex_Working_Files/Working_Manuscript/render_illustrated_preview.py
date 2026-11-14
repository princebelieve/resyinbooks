from __future__ import annotations
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "My_First_Book_of_Healthy_Living_Final_Manuscript.md"
OUT = ROOT / "Healthy_Living_Final_Book.html"
COVER = "../Production/Healthy_Living_Front_Cover_Working_Reference.png"


def inline(text: str) -> str:
    # Minimal Markdown inline conversion for this working manuscript.
    links = []
    def save_link(match):
        links.append((match.group(1), match.group(2)))
        return f"@@LINK{len(links)-1}@@"
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", save_link, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    for i, (label, target) in enumerate(links):
        text = text.replace(f"@@LINK{i}@@", f'<a href="{html.escape(target, quote=True)}">{html.escape(label)}</a>')
    return text


def chapter_number(line: str) -> int | None:
    names = ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN"]
    m = re.match(r"# CHAPTER (.+)$", line)
    if not m:
        return None
    try:
        return names.index(m.group(1).strip()) + 1
    except ValueError:
        return None

def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def render(lines: list[str]) -> str:
    out: list[str] = []
    i = 0
    ul = ol = False
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped:
            if ul:
                out.append("</ul>"); ul = False
            if ol:
                out.append("</ol>"); ol = False
            i += 1
            continue
        if stripped == "---":
            out.append('<hr class="ornament">'); i += 1; continue
        if stripped.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells); i += 1
            if len(rows) > 1 and all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in rows[1]):
                rows.pop(1)
            out.append('<table class="worktable">')
            for ri, row in enumerate(rows):
                tag = "th" if ri == 0 else "td"
                out.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in row) + "</tr>")
            out.append("</table>")
            continue
        if stripped.startswith("# "):
            ch = chapter_number(stripped)
            cls = "chapter-title" if ch else "book-section"
            out.append(f'<h1 class="{cls}" id="chapter-{ch}">{inline(stripped[2:])}</h1>' if ch else f'<h1 class="{cls}" id="{slug(stripped[2:])}">{inline(stripped[2:])}</h1>')
            if ch:
                img = f"Selected_Illustrations/png_review/Chapter_{ch:02d}.png"
                out.append(f'<figure class="storyboard"><img src="{img}" alt="Chapter {ch} illustration"><figcaption>Chapter illustration</figcaption></figure>')
            i += 1; continue
        if stripped.startswith("## "):
            heading=stripped[3:]
            anchors={"Copyright","Dedication","Preface","A Note to Parents, Teachers and Caregivers","How to Use This Book","Contents","My Healthy Living Pledge","My Weekly Healthy Habits Reflection","Glossary","Questions for Revision","References for Adults","About the Author","Find a Topic"}
            ident=f' id="{slug(heading)}"' if heading in anchors else ""
            out.append(f"<h2{ident}>{inline(heading)}</h2>"); i += 1; continue
        if stripped.startswith("### "):
            out.append(f"<h3>{inline(stripped[4:])}</h3>"); i += 1; continue
        if re.match(r"^[-*] ", stripped):
            if ol:
                out.append("</ol>"); ol = False
            if not ul:
                out.append('<ul class="tips">'); ul = True
            out.append(f"<li>{inline(stripped[2:])}</li>"); i += 1; continue
        if re.match(r"^\d+\. ", stripped):
            if ul:
                out.append("</ul>"); ul = False
            if not ol:
                out.append('<ol class="questions">'); ol = True
            out.append(f"<li>{inline(re.sub(r'^\d+\. ', '', stripped))}</li>"); i += 1; continue
        if ul:
            out.append("</ul>"); ul = False
        if ol:
            out.append("</ol>"); ol = False
        cls = ""
        if stripped.startswith("**Remember:**"):
            cls = ' class="remember"'
        elif stripped.startswith("**My promise:**"):
            cls = ' class="promise"'
        elif stripped.startswith("**My promise**") or stripped.startswith("**My Healthy"):
            cls = ' class="promise"'
        out.append(f"<p{cls}>{inline(stripped)}</p>"); i += 1
    if ul: out.append("</ul>")
    if ol: out.append("</ol>")
    return "\n".join(out)


text = SOURCE.read_text(encoding="utf-8-sig")
lines = text.splitlines()
# The supplied front cover carries the title, subtitle and author; begin the text at the copyright page.
start = next((i + 1 for i, line in enumerate(lines) if line.strip() == "---"), 0)
body = render(lines[start:])
html_doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>My First Book of Healthy Living — illustrated book</title>
<style>
@page {{ size: A5; margin: 16mm 15mm 17mm; }}
:root {{ --green:#167340; --navy:#0b2c62; --coral:#d94d32; --gold:#e7b934; --paper:#fffdf5; --ink:#263238; }}
* {{ box-sizing:border-box; }}
body {{ margin:0 auto; max-width:760px; padding:24px; background:#e8eef1; color:var(--ink); font:15px/1.62 Georgia,"Times New Roman",serif; }}
main {{ background:var(--paper); padding:30px 38px; box-shadow:0 4px 22px #28455a26; }}
.cover {{ margin:-30px -38px 28px; text-align:center; background:#0b2c62; }}
.cover img {{ display:block; width:100%; max-height:1060px; object-fit:contain; margin:auto; }}
.notice {{ margin:18px 0 26px; padding:10px 14px; border-left:5px solid var(--gold); background:#fff4c7; color:#584b24; font:13px/1.45 Arial,sans-serif; }}
h1,h2,h3 {{ font-family:Arial,Helvetica,sans-serif; line-height:1.16; }}
h1.chapter-title {{ page-break-before:always; break-before:page; margin:0 0 6px; padding:10px 14px; color:white; background:var(--green); border-radius:9px 9px 0 0; font-size:23px; text-transform:uppercase; }}
h1.book-section {{ color:var(--navy); border-bottom:3px solid var(--gold); padding-bottom:8px; margin-top:1.2em; font-size:24px; }}
h2 {{ color:var(--navy); margin:10px 0 14px; font-size:19px; }}
h3 {{ color:var(--green); margin:24px 0 8px; font-size:16px; }}
p {{ margin:0 0 12px; }}
.storyboard {{ clear:both; width:100%; max-width:410px; margin:10px auto 22px; padding:6px; background:#fff; border:2px solid #e4d9a8; border-radius:10px; }}
.storyboard img {{ display:block; width:100%; height:auto; }}
.storyboard figcaption {{ padding:5px 3px 2px; color:#60686d; font:9px/1.2 Arial,sans-serif; text-align:center; }}
.tips,.questions {{ padding-left:23px; margin:5px 0 16px; }}
li {{ margin-bottom:5px; }}
.remember {{ clear:both; padding:11px 14px; border-left:5px solid var(--green); background:#eaf5ec; border-radius:3px 10px 10px 3px; }}
.promise {{ padding:12px 14px; color:#183e2c; background:#fff1c2; border:1px solid #e7ca6e; border-radius:12px; font-weight:bold; }}
.worktable {{ width:100%; border-collapse:collapse; margin:12px 0 20px; font:13px/1.4 Arial,sans-serif; }}
.worktable th {{ background:var(--navy); color:white; }}
.worktable td,.worktable th {{ border:1px solid #bdc9cb; padding:7px; vertical-align:top; }}
hr.ornament {{ border:0; height:2px; margin:28px auto; max-width:70%; background:linear-gradient(90deg,transparent,var(--gold),transparent); }}
a {{ color:#075c8e; }}
@media screen and (max-width:700px) {{ body {{ padding:0; font-size:16px; }} main {{ padding:22px 20px; }} .cover {{ margin:-22px -20px 24px; }} .storyboard {{ width:100%; }} }}
@media print {{ body {{ max-width:none; padding:0; background:white; font-size:14pt; }} main {{ padding:0; box-shadow:none; }} .cover {{ margin:0 0 16mm; page-break-after:always; }} .cover img {{ max-height:250mm; }} .notice {{ print-color-adjust:exact; }} .storyboard {{ width:100%; max-width:410px; }} h1.chapter-title {{ print-color-adjust:exact; }} .remember,.promise,.worktable th {{ print-color-adjust:exact; }} }}
</style></head><body><main>
<figure class="cover"><img src="{COVER}" alt="Source front cover: My First Book of Healthy Living"></figure>

{body}
</main></body></html>'''
OUT.write_text(html_doc, encoding="utf-8")
print(OUT)
