"""Render linked A5 print and A4 digital interiors from the retained manuscript text."""
from pathlib import Path
from html import escape
import subprocess, tempfile, re
import build_manuscript as book

BASE=Path(__file__).resolve().parent
OUT=BASE/'Production'
EDGE=Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')

def build_html(a5: bool):
    chapters=book.collect_chapters(); back=book.collect_backmatter(); sizes='''@page{size:A5 portrait;margin:18mm 16mm 17mm 20mm;@bottom-center{content:counter(page);font:9pt Georgia;color:#173f35}}''' if a5 else '''@page{size:A4 portrait;margin:20mm 21mm 18mm 22mm;@bottom-center{content:counter(page);font:9pt Georgia;color:#173f35}}'''
    body_size='10.2pt' if a5 else '11.2pt'
    css=sizes+f'''*{{box-sizing:border-box}}body{{font-family:Georgia,serif;font-size:{body_size};line-height:1.42;color:#222;margin:0}}h1,h2{{font-family:Georgia,serif;break-after:avoid-page}}h1{{font-size:18pt;color:#173f35;text-align:center;margin:1.2em 0 .8em}}h2{{font-size:11.5pt;color:#173f35;margin:1.25em 0 .35em}}p{{text-align:justify;margin:.45em 0 .65em;orphans:2;widows:2}}.title{{page-break-after:always;text-align:center;padding-top:24%}}.title h1{{font-size:27pt;line-height:1.1}}.subtitle{{font-size:13pt}}.author{{font-size:15pt;margin-top:2.5em}}.copyright{{page-break-after:always;padding-top:55%}}.cover{{page-break-after:always;height:250mm;display:flex;align-items:center;justify-content:center}}.cover img{{max-width:100%;max-height:100%;object-fit:contain}}.contents{{page-break-after:always}}.contents li{{margin:.45em 0}}.chapter{{page-break-before:always}}.chapterlabel{{text-align:center;color:#a46a14;font-weight:bold;margin:13% 0 1em}}.chapter h1{{font-size:21pt;margin:0 0 1.5em}}.backmatter{{page-break-before:always}}.backheading{{page-break-before:always}}a{{color:#173f35;text-decoration:none}}table{{border-collapse:collapse;width:100%;font-size:8.6pt;page-break-inside:auto}}tr{{break-inside:avoid}}td,th{{border:.5pt solid #aaa;padding:4pt;vertical-align:top}}th{{background:#eaf0ed}}'''
    def esc(x): return escape(x,quote=True)
    out=['<!doctype html><html lang="en"><head><meta charset="utf-8"><title>'+esc(book.TITLE)+'</title><style>'+css+'</style></head><body>']
    if not a5:
        cover=OUT/'Cover_Front_OnlineStore.jpg'
        out.append(f'<section class="cover"><img src="{esc(cover.resolve().as_uri())}" alt="Front cover of Givers and Takers in Africa"/></section>')
    out.append(f'<section class="title"><h1>{esc(book.TITLE)}</h1><p class="subtitle">{esc(book.SUBTITLE)}</p><p class="author">{esc(book.AUTHOR)}</p><p>{esc(book.PUBLISHER)}</p></section>')
    isbn_line=f'<p>ISBN {esc(book.PRINT_ISBN)}</p>' if a5 else ''
    out.append(f'<section class="copyright"><h1>Copyright Page</h1><p>© 2026 {esc(book.AUTHOR)}</p><p>All rights reserved.</p><p>No part of this publication may be reproduced, stored in a retrieval system, transmitted or distributed in any form or by any means, electronic, mechanical, photocopying, recording or otherwise, without the prior written permission of the author, except for brief quotations used for purposes of review, scholarship or criticism.</p><p>First Edition, 2026</p>{isbn_line}<p>Published by:<br>{esc(book.PUBLISHER)}<br>Nigeria</p></section>')
    out.append('<section class="contents"><h1>Contents</h1><ol>')
    for n,_,title,_ in chapters: out.append(f'<li><a href="#chapter-{n}">Chapter {n}: {esc(title)}</a></li>')
    back_heads=[t for t in back if book.TOP_BACK_RE.match(t)]
    out.append('<li><a href="#back-matter">Back Matter</a><ol>')
    for j,t in enumerate(back_heads): out.append(f'<li><a href="#back-{j}">{esc(t.title())}</a></li>')
    out.append('</ol></li>')
    out.append('</ol></section>')
    for n,label,title,paras in chapters:
        out.append(f'<section class="chapter" id="chapter-{n}"><div class="chapterlabel">{esc(label)}</div><h1>{esc(title)}</h1>')
        for p in paras:
            if book.SECTION_RE.match(p):
                sid='s-'+re.match(r'^(\d+\.\d+)',p).group(1).replace('.','-'); out.append(f'<h2 id="{sid}">{esc(p)}</h2>')
            else: out.append(f'<p>{esc(p)}</p>')
        out.append('</section>')
    out.append('<section class="backmatter" id="back-matter"><h1>Back Matter</h1>'); backheadno=0
    i=0
    while i<len(back):
        t=back[i]
        if t=='No.' and back[i:i+4]==['No.','Policy Area','Recommended Action','Expected Outcome']:
            rows=[back[i+j:i+j+4] for j in range(0,64,4)]
            if len(rows)==16 and all(len(row)==4 for row in rows):
                out.append('<table><thead><tr>'+''.join('<th>'+esc(c)+'</th>' for c in rows[0])+'</tr></thead><tbody>')
                for row in rows[1:]: out.append('<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>')
                out.append('</tbody></table>'); i+=64; continue
        if book.TOP_BACK_RE.match(t): out.append(f'<h1 class="backheading" id="back-{backheadno}">{esc(t)}</h1>'); backheadno+=1
        else: out.append(f'<p>{esc(t)}</p>')
        i+=1
    out.append('</section></body></html>')
    return ''.join(out)

def main():
    if not EDGE.exists(): raise FileNotFoundError(f'Edge PDF renderer not found: {EDGE}')
    OUT.mkdir(exist_ok=True)
    for is_a5, stem in [(True,'Givers_and_Takers_in_Africa_Print_Interior_A5'),(False,'Givers_and_Takers_in_Africa_Digital_Readable')]:
        html=OUT/(stem+'.html'); pdf=OUT/(stem+'.pdf'); html.write_text(build_html(is_a5),encoding='utf-8')
        with tempfile.TemporaryDirectory(prefix='givers-edge-') as profile:
            command=[str(EDGE),'--headless=new','--disable-gpu','--disable-gpu-compositing','--in-process-gpu','--disable-gpu-sandbox','--no-first-run','--no-default-browser-check',f'--user-data-dir={profile}',f'--print-to-pdf={pdf}','--no-pdf-header-footer',html.resolve().as_uri()]
            result=subprocess.run(command,capture_output=True,text=True,timeout=180)
        if result.returncode or not pdf.exists() or pdf.stat().st_size<10000:
            raise RuntimeError(f'Edge failed for {stem}: {result.stdout}\n{result.stderr}')
        print(f'{pdf}: {pdf.stat().st_size:,} bytes')
if __name__=='__main__': main()
