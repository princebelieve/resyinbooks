"""Create one-column, two-page chapter Contents in clean PDF baselines.

Chapter headings are taken from the validated EPUB navigation, locators from
the source PDF bookmarks. Page numbers and bookmarks after the inserted page
are advanced by one. Original baselines are left unchanged.
"""
from pathlib import Path
import sys, zipfile, re, html
sys.path.insert(0,str(Path(__file__).resolve().parent/'.python_libs'))
import pymupdf

BASE=Path(__file__).resolve().parent
PROJECT=BASE.parent
DELIVERY=PROJECT/'For_Professor'
ARCHIVE=BASE/'Source_Baselines'
OUT=ARCHIVE/'TOC_Expanded'; OUT.mkdir(exist_ok=True)
with zipfile.ZipFile(DELIVERY/'Serenity_and_Tranquillity.epub') as z:
    nav=z.read('EPUB/nav.xhtml').decode('utf-8')
labels={}
for raw in re.findall(r'<a\b[^>]*>(.*?)</a>',nav,re.S):
    value=' '.join(html.unescape(re.sub(r'<[^>]+>','',raw)).split())
    m=re.match(r'Chapter (\d+):\s*(.*)',value,re.I)
    if m: labels[int(m.group(1))]=m.group(2)
labels[24]='The Serenity-Tranquillity-Sustainability Model: A Framework for Human and National Development'
if len(labels)!=25: raise ValueError(f'Expected 25 chapter headings; got {len(labels)}')

def build(source_name):
    src=ARCHIVE/source_name; doc=pymupdf.open(src); old_len=len(doc)
    toc_index=next(i for i,p in enumerate(doc) if 'TABLE OF CONTENTS' in p.get_text().upper())
    page=doc[toc_index]; w,h=page.rect.width,page.rect.height
    starts={}; chapter_rows=[]
    for level,title,pno in doc.get_toc():
        if title.upper().startswith('CHAPTER'):
            chapter_rows.append((level,title,pno))
    if len(chapter_rows)!=25: raise ValueError(f'{source_name}: found {len(chapter_rows)} chapter bookmarks')
    starts={n:pno-1+(1 if pno-1>toc_index else 0) for n,(_,_,pno) in enumerate(chapter_rows,1)}
    # Replace the old generic list on the first page, keeping its printed heading.
    page.add_redact_annot(pymupdf.Rect(35,58,w-35,h-38),fill=(1,1,1))
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
    for link in list(page.get_links()): page.delete_link(link)
    insert_at=toc_index+1
    second=doc.new_page(pno=insert_at,width=w,height=h)
    page=doc[toc_index]
    digital='Digital' in source_name
    if digital:
        page.insert_text((57,67),'TABLE OF CONTENTS',fontname='tibo',fontsize=16,color=(0.12,0.16,0.28))
        second.insert_text((57,67),'TABLE OF CONTENTS (CONTINUED)',fontname='tibo',fontsize=16,color=(0.12,0.16,0.28))
    else:
        second.insert_text((43,43),'TABLE OF CONTENTS (CONTINUED)',fontname='tibo',fontsize=16,color=(0.12,0.16,0.28))
    # Spacious, single-column rows: thirteen on page one and twelve on page two.
    for n in range(1,26):
        target_page=toc_index if n<=13 else insert_at
        p=doc[target_page]
        slot=n-1 if n<=13 else n-14
        top=92 if digital else 68; bottom=h-43; step=(bottom-top)/13
        y=top+slot*step
        left=43 if w<500 else 57
        right=w-(43 if w<500 else 57)
        label=f'Chapter {n}: {labels[n]}'
        box=pymupdf.Rect(left,y,right-39,y+step-1)
        # Keep both editions' chapter contents comfortably readable.
        # Long titles wrap within each generous row.
        size=11
        remaining=p.insert_textbox(box,label,fontname='tiro',fontsize=size,
                                   lineheight=1.08,color=(0.12,0.16,0.28))
        if remaining<0: raise ValueError(f'Heading does not fit on Contents page: {label}')
        p.insert_text((right-30,y+size),str(starts[n]+1),fontname='tiro',fontsize=size,
                      color=(0.12,0.16,0.28))
        if digital:
            p.insert_link({'kind':pymupdf.LINK_GOTO,
                'from':pymupdf.Rect(left,y,right,y+step-1),
                'page':starts[n],'to':pymupdf.Point(0,0)})
    # Use visible folios matching the inserted physical page sequence.
    second.insert_text((w/2-7,h-25),str(insert_at+1),fontname='tiro',fontsize=9,color=(0.3,0.3,0.3))
    for i in range(insert_at+1,len(doc)):
        p=doc[i]
        p.add_redact_annot(pymupdf.Rect(0,h-38,w,h),fill=(1,1,1)); p.apply_redactions(images=0,graphics=0)
        p.insert_text((w/2-7,h-25),str(i+1),fontname='tiro',fontsize=9,color=(0.3,0.3,0.3))
    new_toc=[]; chapter_n=0
    for level,title,pno in doc.get_toc():
        if title.upper().startswith('CHAPTER'):
            chapter_n+=1; title=f'Chapter {chapter_n}: {labels[chapter_n]}'
        new_toc.append([level,title,pno])
    new_toc.append([1,'Table of Contents (continued)',insert_at+1])
    doc.set_toc(new_toc)
    if 'Print' in source_name:
        for p in doc:
            for link in list(p.get_links()):p.delete_link(link)
    target=OUT/source_name.replace('.pdf','_TOCExpanded.pdf')
    doc.set_metadata({**doc.metadata,'subject':'One-column, full-title chapter contents'})
    temp=target.with_name(target.stem+'.tmp.pdf')
    doc.save(temp,garbage=4,deflate=True); doc.close(); temp.replace(target)
    check=pymupdf.open(target)
    assert len(check)==old_len+1
    assert len(check[toc_index].get_links())==(13 if 'Digital' in source_name else 0)
    assert len(check[insert_at].get_links())==(12 if 'Digital' in source_name else 0)
    if not digital: assert check[insert_at].get_text().startswith('TABLE OF CONTENTS (CONTINUED)')
    else:
        assert 'TABLE OF CONTENTS' in check[toc_index].get_text()
        assert 'TABLE OF CONTENTS (CONTINUED)' in check[insert_at].get_text()
    print(target.name,'pages',len(check),'chapter pages',[starts[n]+1 for n in range(1,26)],
          'links',sum(len(p.get_links()) for p in check))

for name in ['Serenity_and_Tranquillity_Print_Interior_A5_11pt_HeadCorrected.pdf',
             'Serenity_and_Tranquillity_Digital_Readable_CoverCorrected.pdf']:
    build(name)
