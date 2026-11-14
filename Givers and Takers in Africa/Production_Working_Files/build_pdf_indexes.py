"""Add section-based indexes, PDF navigation, previews and a two-up printer file."""
from pathlib import Path
import sys, re, json
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'Serenity and Tranquillity'/'.python_libs'))
import pymupdf as fitz
import build_manuscript as book

BASE=Path(__file__).resolve().parent; PROD=BASE/'Production'; PRE=PROD/'Previews'; PRE.mkdir(exist_ok=True)
SUBJECTS={
'Accountability: democratic responsibility':'13.8,14.4,14.13',
'Accountability: financial management':'6.8,7.7,7.8',
'African development: institutions and leadership':'1.7,4.4,15.2',
'African philosophy: communal living':'2.2,2.3,2.4,2.6',
'Agriculture and food security':'12.3',
'Altruism and empathy':'1.2,1.5,3.3',
'Business ethics: consumers and workers':'8.4,8.5,8.6',
'Citizenship: democratic responsibility':'13.8',
'Civil society: development role':'9.7,14.10,13.9',
'Community development: local government':'7.6,9.8,12.7,15.7',
'Corruption: institutions and public sector':'6.2,6.6,6.7,6.9',
'Democracy: public interest and participation':'13.2,13.4,13.8',
'Development: national transformation':'1.7,7.10,14.5,15.12',
'Education: human capital':'11.3,12.5,15.8',
'Elections: patronage and accountability':'5.6,13.3',
'Entrepreneurship: self-reliance':'8.3,11.5,12.4',
'Ethics: public service':'4.7,7.4,14.3',
'ELEVATE Development Philosophy':'15.11',
'Family: mutual giving':'2.3,12.9',
'Federalism: resource distribution':'13.6',
'Generosity: reciprocity and philanthropy':'1.2,2.5,2.6,10.10',
'Governance: institutional accountability':'3.8,6.9,7.1,13.10',
'Human dignity and social responsibility':'1.5,4.6,14.5',
'Inequality: wealth and opportunity':'10.4,10.8',
'Institutions: traditional and religious':'2.3,3.8,9.5,9.8',
'Leadership: common good and stewardship':'4.4,4.6,4.7,9.6,14.7',
'Nigeria: development and prosperity':'1.6,10.5,15.3,15.12',
'Nepotism and political patronage':'5.2,5.5,5.6',
'Poverty: reduction and social protection':'10.2,10.3,10.7,10.9',
'Political participation: youth and women':'11.8,12.6,13.7',
'Public administration: development agent':'7.2,7.6,7.10,15.5',
'Public finance: resource management':'6.8,7.8,14.4',
'Public procurement: accountability':'7.8,14.4',
'Public service: ethics and responsibility':'4.1,7.4,7.5',
'Religion: moral development and giving':'2.5,9.2,9.3,9.4',
'Resource curse and resource diversion':'6.4,6.5,15.3',
'Self-interest: motivation and culture':'1.4,3.2,3.7',
'Social exchange and reciprocity':'2.6,3.6,14.11',
'Social protection: poverty reduction':'10.7',
'Stomach infrastructure':'5.3,5.4',
'Sustainable development: prosperity':'1.7,14.5,15.8,15.10',
'Technology: accountable administration':'7.9,11.6,15.9',
'Traditional institutions: communal responsibility':'2.4,9.5,9.8',
'Transparency: public accountability':'6.8,7.8,13.8',
'Unemployment: youth and dependency':'11.2,11.4,11.5',
'Ubuntu: personhood and solidarity':'2.2,2.4',
'Wealth: creation and extraction':'8.2,10.4,15.6',
'Women: economic and community contribution':'12.2,12.3,12.4,12.7',
'Youth: entrepreneurship and participation':'11.2,11.5,11.8,11.9',
}
CROSS={'Giving':'Generosity: reciprocity and philanthropy','Takers':'Self-interest: motivation and culture','Stomach politics':'Stomach infrastructure','Public accountability':'Accountability: democratic responsibility'}
RELATED={'corruption':'6.2','good governance':'7.1','Ubuntu':'2.2','reciprocity':'2.6','political patronage':'5.2','stomach infrastructure':'5.3','public financial management':'6.8','public service':'7.4','corporate social responsibility':'8.6','religious leadership':'9.6','social protection':'10.7','youth entrepreneurship':'11.5','women in agriculture':'12.3','democracy':'13.2','accountability':'14.4','common good':'14.5','leadership by example':'14.7','ELEVATE':'15.11','sustainable prosperity':'15.8','resource curse':'6.4'}

def text(p): return p.get_text('text').strip()
def wrap(s,font,size,width):
    out=[]; cur=''
    for word in s.split():
        t=(cur+' '+word).strip()
        if cur and fitz.get_text_length(t,fontname=font,fontsize=size)>width: out.append(cur); cur=word
        else: cur=t
    if cur: out.append(cur)
    return out
def ranges(nums):
    nums=sorted(set(nums)); out=[]; i=0
    while i<len(nums):
        j=i
        while j+1<len(nums) and nums[j+1]==nums[j]+1: j+=1
        out.append(str(nums[i]+1) if i==j else f'{nums[i]+1}-{nums[j]+1}'); i=j+1
    return ', '.join(out)

def section_pages(doc, chapters):
    starts={}; section_order=[]; chapter_pages={}
    for n,_,title,body in chapters:
        marker=f'CHAPTER {book.WORDS[n-1]}'
        cp=next((i for i,p in enumerate(doc) if marker in text(p)),None)
        if cp is None: raise ValueError(f'Chapter start missing from PDF: {n}')
        chapter_pages[n]=cp
        for heading in body:
            if not book.SECTION_RE.match(heading): continue
            found=None
            for i in range(cp,len(doc)):
                hits=doc[i].search_for(heading)
                if hits: found=(i,hits[0]); break
            if found is None: raise ValueError(f'Section heading not found in PDF {n}: {heading}')
            sid=re.match(r'^(\d+\.\d+)',heading).group(1)
            starts[sid]=found; section_order.append((sid,n,heading))
    back=next(i for i,p in enumerate(doc) if p.search_for('Back Matter'))
    spans={}
    for ix,(sid,n,heading) in enumerate(section_order):
        first=starts[sid][0]
        if ix+1<len(section_order): last=max(first,starts[section_order[ix+1][0]][0])
        else: last=max(first,back-1)
        spans[sid]=list(range(first,last+1))
    return starts,spans,chapter_pages,back

def make_rows(chapters,spans):
    section_text={};
    for n,_,title,body in chapters:
        active=None; buf=[]
        for para in body:
            if book.SECTION_RE.match(para):
                if active: section_text[active]=' '.join(buf)
                active=re.match(r'^(\d+\.\d+)',para).group(1); buf=[para]
            elif active: buf.append(para)
        if active: section_text[active]=' '.join(buf)
    rows=[]; evidence=[]
    for label,ids in SUBJECTS.items():
        pages=set(); used=[]
        for sid in ids.split(','):
            if sid not in spans: raise ValueError(f'Index points to missing section {sid}: {label}')
            pages.update(spans[sid]); used.append(sid)
        evidence.append({'entry':label,'sections':used,'pages':sorted(p+1 for p in pages)})
        main,_,sub=label.partition(': ')
        rows.append((main,sub,sorted(pages),label))
    for term,target in CROSS.items():
        if target not in SUBJECTS: raise ValueError(f'Invalid cross-reference target: {target}')
        main=term; rows.append((main,'See '+target,[],main))
    return sorted(rows,key=lambda x:(x[0].casefold(),x[1].casefold())),evidence,section_text

def build_index(rows,w,h,index_page_num):
    size=9.4 if w<450 else 10.2; lead=size+2.3; margin=43 if w<450 else 55; gap=20; cw=(w-2*margin-gap)/2
    out=fitz.open(); links=[]; entry_anchor={}; page=None; col=0; y=0; letter=''
    def new_page():
        nonlocal page,y,col
        page=out.new_page(width=w,height=h); col=0; y=78
        page.insert_text((margin,48),'Subject Index' if len(out)==1 else 'Subject Index (continued)',fontname='tibo',fontsize=16,color=(.09,.25,.20))
        page.insert_text((w/2-7,h-23),str(index_page_num+len(out)-1),fontname='tiro',fontsize=8)
    def advance():
        nonlocal col,y
        if col==0: col=1; y=78
        else: new_page()
    new_page()
    for main,sub,pages,label in rows:
        first=main[0].upper()
        is_cross=not pages
        name_text=(main+'. See '+sub[4:] if is_cross else main+(', '+sub if sub else ''))
        page_labels=ranges(pages) if pages else ''
        full=(name_text + (', '+page_labels if page_labels else ''))
        font='tibo' if not sub or is_cross else 'tiro'; indent=0 if not sub or is_cross else 12
        wrapped=wrap(full,font,size,cw-indent)
        need=len(wrapped)*lead+(9 if first!=letter else 2)
        if y+need>h-43: advance()
        if first!=letter:
            y+=5; page.insert_text((margin+col*(cw+gap),y),first,fontname='tibo',fontsize=size+1,color=(.67,.43,.08)); y+=lead; letter=first
        x=margin+col*(cw+gap)+indent
        if not sub or is_cross: entry_anchor.setdefault(main,(len(out)-1,fitz.Point(x,y-size)))
        offset=0
        for line in wrapped:
            page.insert_text((x,y),line,fontname=font,fontsize=size)
            if pages:
                for m in re.finditer(r'(?<!\w)(\d+)(?:-(\d+))?(?=,|$)',line):
                    for g in (1,2):
                        if not m[g]: continue
                        a=x+fitz.get_text_length(line[:m.start(g)],fontname=font,fontsize=size); b=a+fitz.get_text_length(m[g],fontname=font,fontsize=size)
                        links.append((len(out)-1,fitz.Rect(a,y-size,b,y+2),int(m[g])-1))
            offset+=len(line)+1; y+=lead
        y+=2
    # Make See references point to the corresponding main entry.
    for main,sub,pages,label in rows:
        if pages or not sub.startswith('See '): continue
        target=sub[4:]
        if target in entry_anchor:
            dest,point=entry_anchor[target]
            # Find the printed cross-reference phrase and link only its target words.
            for i,p in enumerate(out):
                for r in p.search_for(target):
                    p.insert_link({'kind':fitz.LINK_GOTO,'from':r,'page':dest,'to':point})
    return out,links,entry_anchor

def process(filename,digital=False):
    src=PROD/filename; doc=fitz.open(src); chapters=book.collect_chapters(); starts,spans,chapter_pages,back=section_pages(doc,chapters); rows,evidence,section_text=make_rows(chapters,spans)
    index,loc_links,anchors=build_index(rows,doc[0].rect.width,doc[0].rect.height,len(doc)+1)
    # A subject index belongs after all supplied back matter, at the end of the book.
    count=len(index); out=fitz.open(); out.insert_pdf(doc); index_start=len(out); out.insert_pdf(index); tail=index_start+count
    for local,rect,dest in loc_links:
        out[index_start+local].insert_link({'kind':fitz.LINK_GOTO,'from':rect,'page':dest,'to':fitz.Point(0,0)})
    # Restore all original internal links after the page insertion and keep destinations exact.
    for old_i,page in enumerate(doc):
        new_i=old_i
        for link in page.get_links():
            if link.get('kind') not in (fitz.LINK_GOTO,fitz.LINK_NAMED) or link.get('page',-1)<0: continue
            dest=link['page']
            out[new_i].insert_link({'kind':fitz.LINK_GOTO,'from':link['from'],'page':dest,'to':link.get('to',fitz.Point(0,0))})
    index_dest=index_start
    # Digital reading controls and selective in-text links to substantively relevant sections.
    related_count=0; return_count=0
    if digital:
        # Targets point to the start of the chosen section in the final edition.
        topic_dest={term:(starts[sid][0],fitz.Point(starts[sid][1].x0,starts[sid][1].y0)) for term,sid in RELATED.items()}
        for n,cp in chapter_pages.items():
            next_cp=chapter_pages.get(n+1,back)
            for term,(dest,point) in topic_dest.items():
                if cp<=dest<next_cp: continue
                used=False
                for i in range(cp,next_cp):
                    page=out[i]
                    rects=page.search_for(term)
                    rect=next((r for r in rects if r.y0>55 and r.y1<page.rect.height-42),None)
                    if rect:
                        page.insert_link({'kind':fitz.LINK_GOTO,'from':rect,'page':dest,'to':point}); related_count+=1; used=True; break
                if used: continue
            for old in range(cp,next_cp):
                p=out[old]
                r=fitz.Rect(p.rect.width-118,p.rect.height-27,p.rect.width-53,p.rect.height-14)
                p.insert_text((r.x0,r.y0+9),'Subject index',fontname='tiro',fontsize=7.5,color=(.1,.35,.45))
                p.insert_link({'kind':fitz.LINK_GOTO,'from':r,'page':index_dest,'to':fitz.Point(0,0)}); return_count+=1
    # Index page locators are page-numbered for this specific output.
    toc=[[1,book.TITLE,1],[1,'Contents',2]]
    for n,_,title,_ in chapters: toc.append([1,f'Chapter {n}: {title.title()}',chapter_pages[n]+1])
    toc.append([1,'Back Matter',back+1]); toc.append([1,'Subject Index',index_start+1]); out.set_toc(toc)
    out.set_metadata({'title':book.TITLE,'author':book.AUTHOR,'subject':'Indexed edition; internal chapter and topic navigation'})
    target=PROD/(filename.replace('.pdf','_Indexed.pdf')); out.save(target,garbage=4,deflate=True)
    # Reopen and confirm every index locator and original chapter link resolves inside this edition.
    saved=fitz.open(target); link_records=[]
    for pno in range(index_start,index_start+count):
        for link in saved[pno].get_links():
            if link.get('kind')==fitz.LINK_GOTO: link_records.append(link)
    if any(l.get('page',-1)<0 or l.get('page',len(saved))>=len(saved) for p in saved for l in p.get_links()): raise ValueError('Out-of-range PDF link destination')
    if len(saved[index_start].get_text().strip())<100: raise ValueError('Subject index output is empty')
    for old_page in range(len(doc)):
        actual=saved[old_page].get_text()
        if digital: actual=actual.replace('Subject index\n','')
        if actual!=doc[old_page].get_text(): raise ValueError(f'Manuscript text changed during indexing on page {old_page+1}')
    for old_page,page in enumerate(doc):
        new_page=old_page
        for link in page.get_links():
            if link.get('kind') not in (fitz.LINK_GOTO,fitz.LINK_NAMED) or link.get('page',-1)<0: continue
            destination=link['page']
            rect=link['from']
            if not any(l.get('kind')==fitz.LINK_GOTO and l.get('page')==destination and abs(l['from'].x0-rect.x0)<.1 and abs(l['from'].y0-rect.y0)<.1 for l in saved[new_page].get_links()):
                raise ValueError(f'An original contents/navigation link was not retained: source page {old_page+1}')
    saved[index_start].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(PRE/(target.stem+'_Index.png'))
    saved[back].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(PRE/(target.stem+'_Backmatter.png'))
    return saved,target,{'pages':len(saved),'index_pages':count,'entries':len(evidence),'index_locator_links':len(link_records),'related_links':related_count,'return_links':return_count,'evidence':evidence}

def main():
    records=[]; docs=[]
    for name,digital in [('Givers_and_Takers_in_Africa_Print_Interior_A5.pdf',False),('Givers_and_Takers_in_Africa_Digital_Readable.pdf',True)]:
        doc,target,info=process(name,digital); docs.append((doc,target)); records.append({'file':target.name,**{k:v for k,v in info.items() if k!='evidence'},'evidence':info['evidence']})
    source=docs[0][0]; w,h=source[0].rect.width,source[0].rect.height; spreads=fitz.open()
    for i in range(0,len(source),2):
        p=spreads.new_page(width=2*w,height=h); p.show_pdf_page(fitz.Rect(0,0,w,h),source,i)
        if i+1<len(source): p.show_pdf_page(fitz.Rect(w,0,2*w,h),source,i+1)
    # Preserve every one-page PDF link when it is imposed as a two-up spread.
    for i,p in enumerate(source):
        for l in p.get_links():
            if l.get('kind') not in (fitz.LINK_GOTO,fitz.LINK_NAMED) or l.get('page',-1)<0: continue
            rect=fitz.Rect(l['from']); shift=(i%2)*w; rect.x0+=shift; rect.x1+=shift
            dest=l['page']; point=fitz.Point(l.get('to',fitz.Point(0,0))); point.x+=(dest%2)*w
            spreads[i//2].insert_link({'kind':fitz.LINK_GOTO,'from':rect,'page':dest//2,'to':point})
    two=PROD/'Givers_and_Takers_in_Africa_Hardcopy_A5_2up_Indexed.pdf'; spreads.save(two,garbage=4,deflate=True)
    expected_links=sum(len(p.get_links()) for p in source); actual_links=sum(len(p.get_links()) for p in spreads)
    if actual_links!=expected_links: raise ValueError(f'Two-up link count changed: {expected_links} -> {actual_links}')
    audit={'editions':records,'two_up':{'file':two.name,'spreads':len(spreads),'links':actual_links}}
    (PROD/'Subject_Index_Audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
    (PROD/'Subject_Index_Notes.md').write_text('# Subject index and navigation\n\nThe subject index is specific to this manuscript. Locators are derived from the selected numbered chapter sections listed in `Subject_Index_Audit.json`; the index was inserted before the supplied back matter. Index locators, See references, contents links, chapter bookmarks and digital related-topic links are internal PDF links. The two-up A5 file preserves these destinations across imposition.\n\nThe index is a first editorial pass and should be reviewed for scope and terminology. Each locator points to the start of a relevant section; it does not imply that every passing mention is indexed.\n',encoding='utf-8')
    print(json.dumps([{k:v for k,v in x.items() if k!='evidence'} for x in records]+[audit['two_up']],indent=2))
if __name__=='__main__': main()
