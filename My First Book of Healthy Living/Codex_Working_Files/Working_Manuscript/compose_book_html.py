from pathlib import Path
import re, shutil
base=Path(__file__).resolve().parents[2]
w=base/'Codex_Working_Files'/'Working_Manuscript'
delivery=base/'For_Professor'
(delivery/'Illustrations').mkdir(exist_ok=True)
for n in range(1,11):
    shutil.copy2(w/'Selected_Illustrations'/'png_review'/f'Chapter_{n:02d}.png',delivery/'Illustrations'/f'Chapter_{n:02d}.png')
shutil.copy2(base/'Codex_Working_Files'/'Production'/'Healthy_Living_Front_Cover_Working_Reference.png',delivery/'Cover_Front.png')
s=(w/'Healthy_Living_Final_Book.html').read_text(encoding='utf-8')
# Keep only book content, omitting the prototype cover panel and every internal production notice.
start=s.index('<body><main>')+len('<body><main>')
end=s.index('</main></body>',start)
body=s[start:end]
body=re.sub(r'^\s*<figure class="cover">.*?</figure>','',body,flags=re.S)
body=re.sub(r'<div class="notice">.*?</div>','',body,flags=re.S)
toc_number=[0]
def link_toc_item(match):
    toc_number[0]+=1
    return f'<li><a href="#chapter-{toc_number[0]}">{match.group(1)}</a></li>'
body=re.sub(r'<li>(.*?)</li>',link_toc_item,body,count=10,flags=re.S)
def slug(term):
    return re.sub(r'[^a-z0-9]+','-',term.lower()).strip('-')
for heading in ['Copyright','Dedication','Preface','A Note to Parents, Teachers and Caregivers','How to Use This Book','Contents','My Healthy Living Pledge','My Weekly Healthy Habits Reflection','Glossary','Questions for Revision','References for Adults','About the Author','Find a Topic']:
    body=body.replace(f'<h2 id="{slug(heading)}">{heading}</h2>',f'<h1 class="front-section" id="{slug(heading)}">{heading}</h1>')
body=body.replace('<figcaption>Chapter illustration</figcaption>','').replace('Selected_Illustrations/png_review/','Illustrations/')
for n in range(1,11):
    # The chapter heading is hidden in print; put its link destination on the visible opener artwork.
    body=body.replace(f'<h1 class="chapter-title" id="chapter-{n}">', '<h1 class="chapter-title">')
    body=body.replace(f'<figure class="storyboard"><img src="Illustrations/Chapter_{n:02d}.png"',f'<figure class="storyboard" id="chapter-{n}"><img src="Illustrations/Chapter_{n:02d}.png"')
body=re.sub(r'(<h1 class="chapter-title"[^>]*>.*?</h1>)\s*(<figure class="storyboard">.*?</figure>)\s*(<h2>.*?</h2>)',r'\1\3\2',body,flags=re.S)
body=re.sub(r'(<h1 class="chapter-title"[^>]*>.*?</h1>\s*<h2>.*?</h2>\s*<figure class="storyboard">.*?</figure>)',r'<section class="chapter-start">\1</section>',body,flags=re.S)
body=re.sub(r'<section class="chapter-start">(.*?)</section>',r'\1',body,flags=re.S)
body=body.replace('<h1 class="front-section" id="copyright">Copyright</h1>','<h1 class="front-section first-front" id="copyright">Copyright</h1>')
body=body.replace('Selected chapter illustration','Chapter illustration')
# Turn each chapter's vocabulary list into links to child-friendly glossary definitions.
body=re.sub(r'<p><strong>New words:</strong>\s*(.*?)</p>',lambda m:'<p><strong>New words:</strong> '+', '.join(f'<a href="#glossary-{slug(x.strip())}">{x.strip()}</a>' for x in m.group(1).split(','))+'</p>',body)
body=re.sub(r'(<p><strong>New words:</strong>.*?</p>)',r'\1<p class="navigation"><a href="#contents">Contents</a> | <a href="#find-a-topic">Find a Topic</a></p>',body)
g=body.find('<h1 class="front-section" id="glossary">Glossary</h1>')
if g>=0:
    body=body[:g]+re.sub(r'<p><strong>([^<]+):</strong>',lambda m:f'<p id="glossary-{slug(m.group(1))}"><strong>{m.group(1)}:</strong>',body[g:])
# Stable, widely supported text punctuation avoids font-map damage in PDF readers.
body=body.replace(chr(8220),chr(34)).replace(chr(8221),chr(34)).replace(chr(8217),chr(39)).replace(chr(8212),chr(45)).replace(chr(8211),chr(45)).replace(chr(169),'&#169;')
title='''<section class="titlepage"><div><h1>MY FIRST BOOK OF HEALTHY LIVING</h1><p class="subtitle">A Children's Guide to Personal Well-Being, Healthy Habits and Responsible Living</p><p class="byline">By Prof. Johnson Agharese Egonmwan</p><p>Resyin (NG) Consults</p></div></section>'''
css='''<style>
@page { size: A5; margin: 15mm 14mm 17mm; @bottom-center { content: counter(page); font: 10pt Arial; color: #52615c; } }
:root { --green:#167340; --navy:#0b2c62; --gold:#d7aa26; --paper:#fffdf5; --ink:#263238; }
*{box-sizing:border-box} body{margin:0;color:var(--ink);font:14pt/1.5 Georgia,"Times New Roman",serif} main{padding:0;background:var(--paper)}
.titlepage{page-break-after:auto;height:auto;min-height:0;display:block;text-align:center;padding:45mm 0 20mm;color:var(--navy)}
.cover{page-break-after:always;text-align:center;margin:0}.cover img{max-width:100%;max-height:245mm;object-fit:contain}.titlepage h1{font: bold 26pt/1.15 Arial,sans-serif;color:var(--green);margin:0 0 12mm}.subtitle{font:16pt/1.35 Georgia,serif}.byline{font:15pt Georgia,serif;margin-top:14mm}
h1,h2,h3{font-family:Arial,Helvetica,sans-serif;line-height:1.16;break-after:avoid-page}h1.front-section{page-break-before:always;color:var(--navy);font-size:23pt;border-bottom:3px solid var(--gold);padding-bottom:6pt}h1.front-section.first-front{page-break-before:always}h1.chapter-title,h2{display:none}.storyboard{page-break-before:always;page-break-after:always;break-inside:avoid-page}h1.chapter-title{page-break-before:auto;margin:0 0 6pt;padding:10pt 14pt;color:white;background:var(--green);font-size:21pt}
h2{color:var(--navy);margin:13pt 0 9pt;font-size:17pt}h3{color:var(--green);margin:15pt 0 6pt;font-size:13pt}p{margin:0 0 10pt;text-align:left;orphans:2;widows:2}
.storyboard{clear:both;width:88%;max-width:88%;margin:0 auto;padding:0;background:white;border:0;border-radius:0;break-inside:avoid}.storyboard img{display:block;width:100%;height:auto;max-height:225mm;object-fit:contain}.tips,.questions{padding-left:24pt;margin:5pt 0 12pt}li{margin-bottom:4pt}.remember{clear:both;padding:9pt 12pt;border-left:4pt solid var(--green);background:#eaf5ec}.promise{padding:9pt 12pt;color:#183e2c;background:#fff1c2;border:1pt solid #e7ca6e;font-weight:bold}.worktable{width:100%;border-collapse:collapse;margin:10pt 0 16pt;font:10.5pt/1.3 Arial,sans-serif}.worktable th{background:var(--navy);color:white}.worktable td,.worktable th{border:1px solid #bdc9cb;padding:5pt;vertical-align:top}hr.ornament{border:0;height:2px;margin:18pt auto;max-width:70%;background:var(--gold)}
@media print { body{font-size:14pt} h1.chapter-title{print-color-adjust:exact} .remember,.promise,.worktable th{print-color-adjust:exact} }
a{color:#0b5d42;text-decoration:underline}.navigation{font:12pt Arial,sans-serif;margin:12pt 0}
</style>'''
head='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>My First Book of Healthy Living</title>'+css+'</head><body><main>'
# Print interior: no outer cover page. Digital screen copy receives the standalone cover as its opening page.
print_html=head+title+body+'</main></body></html>'
(w/'Healthy_Living_Interior_A5.html').write_text(print_html,encoding='utf-8')
(base/'For_Professor'/'My_First_Book_of_Healthy_Living_Print_Interior_A5.html').write_text(print_html,encoding='utf-8')
cover='<figure class="cover"><img src="Cover_Front.png" alt="My First Book of Healthy Living cover" /></figure>'
a4css=css.replace('size: A5','size: A4').replace('15mm 14mm 17mm','19mm 20mm 20mm')
a4=head.replace(css,a4css).replace('<main>','<main>'+cover+title)+body+'</main></body></html>'
(w/'Healthy_Living_Digital_A4.html').write_text(a4,encoding='utf-8')
(base/'For_Professor'/'My_First_Book_of_Healthy_Living_Digital_Readable_A4.html').write_text(a4,encoding='utf-8')
