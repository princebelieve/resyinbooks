"""Add actual chapter-opening page numbers to both PDF Contents pages.

The existing title wording and pagination are retained. Print interiors and the
two-up hardcopy are print-only; internal links remain available in the digital PDF.
"""
from pathlib import Path
import re, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'Serenity and Tranquillity'/'Codex_Working_Files'/'.python_libs'))
import pymupdf

BASE=Path(__file__).resolve().parent
DELIVERY=BASE.parent/'For_Professor'

def repair(source_name,digital):
    path=DELIVERY/source_name
    doc=pymupdf.open(path); page_count=len(doc)
    if not digital and sum(len(p.get_links()) for p in doc)==0:
        print(path.name,'already print-only; page locators retained')
        doc.close(); return
    starts={pno-1 for _,title,pno in doc.get_toc() if re.match(r'Chapter \d+:',title)}
    if len(starts)!=15: raise ValueError(f'Expected 15 chapter bookmarks in {source_name}, found {len(starts)}')
    start_to_n={pno-1:int(re.match(r'Chapter (\d+):',title).group(1))
                for _,title,pno in doc.get_toc() if re.match(r'Chapter \d+:',title)}
    links_by_page={}
    toc_page=next(i for i,p in enumerate(doc) if 'CONTENTS' in p.get_text().upper())
    for i in range(toc_page,min(toc_page+2,len(doc))):
        p=doc[i]
        for link in p.get_links():
            if link.get('page',-1) in start_to_n:
                links_by_page.setdefault((i,link['page']),[]).append(link)
    rows=0
    for (page_no,dest),links in links_by_page.items():
        page=doc[page_no]
        # Multi-line titles produce several link rectangles; place the locator
        # beside the final line of that chapter entry.
        y=max(link['from'].y1 for link in links)
        x=page.rect.width-39
        page.insert_text((x,y-1),str(dest+1),fontname='tiro',fontsize=8.4,
                         color=(0.12,0.16,0.28),overlay=True)
        rows+=1
    if rows!=15: raise ValueError(f'Inserted {rows}/15 chapter locators in {source_name}')
    if not digital:
        for page in doc:
            for link in list(page.get_links()): page.delete_link(link)
    temp=path.with_name(path.stem+'.tocfix.tmp.pdf')
    doc.save(temp,garbage=4,deflate=True); doc.close(); temp.replace(path)
    check=pymupdf.open(path)
    assert len(check)==page_count
    if not digital: assert sum(len(p.get_links()) for p in check)==0
    print(path.name,'pages',len(check),'locators',rows,'links',sum(len(p.get_links()) for p in check))

repair('Givers_and_Takers_in_Africa_Print_Interior_A5_Indexed.pdf',False)
repair('Givers_and_Takers_in_Africa_Digital_Readable_Indexed.pdf',True)

# Re-impose the updated A5 interior for paper printing; carry no link annotations.
src=pymupdf.open(DELIVERY/'Givers_and_Takers_in_Africa_Print_Interior_A5_Indexed.pdf')
spreads=pymupdf.open()
for i in range(0,len(src),2):
    page=spreads.new_page(width=842,height=595)
    page.show_pdf_page(pymupdf.Rect(0,0,421,595),src,i,keep_proportion=True)
    if i+1<len(src): page.show_pdf_page(pymupdf.Rect(421,0,842,595),src,i+1,keep_proportion=True)
out=DELIVERY/'Givers_and_Takers_in_Africa_Hardcopy_A5_2up_Indexed.pdf'
spreads.save(out,garbage=4,deflate=True)
print(out.name,'sheets',len(spreads),'links',sum(len(p.get_links()) for p in spreads))
