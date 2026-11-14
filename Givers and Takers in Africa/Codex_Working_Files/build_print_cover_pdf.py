"""Wrap the generated A5 cover JPEG as a dimensioned PDF proof and write its audit."""
from pathlib import Path
import json, sys

BASE=Path(__file__).resolve().parent
PROD=BASE/'Production'
DELIVERY=BASE.parent/'For_Professor'
sys.path.insert(0,str(BASE.parent.parent/'Serenity and Tranquillity'/'Codex_Working_Files'/'.python_libs'))
import pymupdf as fitz

PAGE_COUNT=167
TRIM_WIDTH_IN=420.0/72.0
TRIM_HEIGHT_IN=594.96/72.0
SPINE_WIDTH_IN=PAGE_COUNT*0.0025 # cream paper, matching the prior cover workflow
BLEED_IN=0.125
SPREAD_WIDTH_IN=2*TRIM_WIDTH_IN+SPINE_WIDTH_IN+2*BLEED_IN
SPREAD_HEIGHT_IN=TRIM_HEIGHT_IN+2*BLEED_IN
JPG=DELIVERY/'Cover_Spread_A5_167p_Cream_Assumption.jpg'
PDF=DELIVERY/'Cover_Spread_A5_167p_Cream_Assumption.pdf'

doc=fitz.open()
page=doc.new_page(width=SPREAD_WIDTH_IN*72,height=SPREAD_HEIGHT_IN*72)
page.insert_image(page.rect,filename=str(JPG))
doc.set_metadata({'title':'Givers and Takers in Africa — A5 print cover proof','author':'Resyin Publications (NG) Inc.','subject':'A5 167-page wrap proof; cream-paper spine assumption'})
doc.save(PDF,garbage=4,deflate=True)
report={
    'source_cover':'Professor_Supplied/Givers and Takers Book Cover.jpeg',
    'page_count':PAGE_COUNT,
    'trim_inches':[TRIM_WIDTH_IN,TRIM_HEIGHT_IN],
    'spine_formula':'page_count x 0.0025 inches (cream-paper assumption from reference cover workflow)',
    'spine_inches':SPINE_WIDTH_IN,
    'outer_bleed_inches_each_edge':BLEED_IN,
    'cover_spread_inches':[SPREAD_WIDTH_IN,SPREAD_HEIGHT_IN],
    'cover_art_pixels_at_300dpi':[3701,2555],
    'cover_pdf_points':[SPREAD_WIDTH_IN*72,SPREAD_HEIGHT_IN*72],
    'proof_status':'Working proof only. Confirm paper type, binding and printer template before submission.',
    'isbn':'978-978-59760-5-2',
    'isbn_source':'Retained from supplied back-cover art and added as plain text to the printed interior copyright page. No separate ebook ISBN was supplied.'
}
(PROD/'Print_Cover_Audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(f'{PDF}: {page.rect.width:.2f} x {page.rect.height:.2f} pt; spine {SPINE_WIDTH_IN:.3f} in; {PAGE_COUNT} pages.')
