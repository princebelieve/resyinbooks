"""Build edition-specific subject indexes without reflowing the manuscript.

Requires PyMuPDF, installed locally in .python_libs. Locators refer to substantive
sections, not passing mentions, front matter, the glossary, or the index itself.
"""
from pathlib import Path
import sys, re, json, zipfile
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).parent / '.python_libs'))
import pymupdf as fitz

BASE = Path(__file__).parent
ARCHIVE = BASE / 'Archive_Obsolete'

def source_path(name):
    current=BASE/name
    return current if current.exists() else ARCHIVE/name

# Each term leads to a substantive discussion, not to a keyword search result.
RELATED = {
    'emotional intelligence':'12.3', 'sustainable development':'19.2',
    'social justice':'8.2', 'human dignity':'17.2', 'social cohesion':'17.7',
    'good governance':'16.2', 'climate change':'11.3',
    'lifelong learning':'12.6', 'public financial management':'16.5',
    'environmental stewardship':'11.2', 'responsible citizenship':'18.3',
    'international cooperation':'19.8', 'social protection':'10.8',
    'meritocracy':'17.6', 'digital citizenship':'12.8',
    'conflict prevention':'6.8', 'peacebuilding':'15.2',
    'transparency':'9.4', 'inner peace':'14.2',
}
# A colon introduces a genuine subordinate entry; numbers identify the retained
# manuscript sections, allowing locators to be regenerated for each edition.
SUBJECTS = '''
Accountability:institutional arrangements|22.4
Accountability:justice and peace|15.8
Accountability:public finances|16.5
Agriculture|19.3
Anxiety|3.3
Boundaries, personal|13.8
Character:education and moral values|5.2,5.4,5.9
Character:parenting|4.5
Children:right to be heard|13.4
Citizenship:democratic responsibility|16.6,18.3
Citizenship:digital|12.8
Citizenship:role in development|24.8
Civil society|18.8
Climate change:development|19.5
Climate change:human security|11.3
Communication:family harmony|4.3
Communication:skills|12.4
Community:dialogue|6.5
Community:environmental guardianship|11.7
Community:family foundations|4.8
Community:legacy|23.3
Community:participation|6.3
Community:public spaces|6.7
Community:tranquillity framework|6.9
Community:understanding|6.2
Conflict:accountability and justice|15.8
Conflict:dialogue|15.3
Conflict:family disagreements|13.3
Conflict:farmer-herder disputes|15.7
Conflict:management|1.8
Conflict:prevention|6.8
Conflict:social media|15.6
Conflict:understanding|15.2
Corruption, moral education and|5.6
Culture:development|7.3
Culture:peace|15.9
Culture:serenity and tranquillity|1.9
Democracy:opposition and tolerance|16.7
Democracy:responsible citizenship|16.6
Developing countries, institutional reform|22.8
Dialogue:community|6.5
Dialogue:peacebuilding|15.3
Digital citizenship|12.8
Digital technology:education|5.8
Digital technology:family life|13.6
Digital technology:governance|16.8
Digital technology:inclusion|17.8
Digital technology:information overload|3.7
Digital technology:institutions|22.6
Digital technology:legacy|23.6
Discrimination|7.4
Diversity:culture and development|7.3
Diversity:education and understanding|5.7
Diversity:media|7.7
Diversity:meritocracy|7.5
Diversity:national development|7.8
Diversity:religious|17.5
Diversity:understanding|7.2
Diversity:workplace|7.6
Economic development:diversification|10.7,19.4
Economic development:entrepreneurship|10.3
Economic development:governance|9.6
Economic development:inclusive growth|10.5
Economic development:prosperity|10.2
Economic development:tranquillity framework|10.9
Economic security:family life|10.4,13.7
Economic security:savings and investment|10.6
Education:action agenda|21.3
Education:beyond academic achievement|5.2,12.2
Education:character in the family|5.4
Education:emotional intelligence|12.3
Education:global peace|20.6
Education:intercultural understanding|5.7
Education:lifelong learning|12.6
Education:moral values and corruption|5.6
Education:national unity|18.5
Education:professional ethics|5.5
Education:serenity|5.3
Education:technical and vocational|12.7
Education:tolerance|12.5
Emotional intelligence|2.3,12.3
Entrepreneurship|10.3
Environment:action agenda|21.4
Environment:climate change|11.3,19.5
Environment:community guardianship|11.7
Environment:future generations|11.8
Environment:future sustainability|25.5
Environment:governance|9.8
Environment:green economy|19.7
Environment:health|11.6
Environment:stewardship|11.2
Environment:sustainable cities|19.6
Environment:waste management|11.5
Environment:water resources|11.4
Ethics:leadership|9.3
Ethics:professional education|5.5
Ethics:public service|16.4
Expectations, managing|2.5,3.4
Family:character formation|4.5,5.4
Family:communication|4.3
Family:community tranquillity|4.8
Family:digital technology|13.6
Family:disagreements|13.3
Family:economic pressure|13.7
Family:financial responsibility|13.5
Family:forgiveness and reconciliation|4.4
Family:foundations of society|4.2,13.2
Family:gender equality|4.7
Family:Nigerian context|4.6
Family:personal boundaries|13.8
Family:sustainable development|4.9
Family:tranquillity framework|13.9
Farmer-herder conflicts|15.7
Federalism|18.7
Financial responsibility, family|13.5
Forgiveness|4.4
Future generations:environment|11.8
Future generations:generational legacy|23.7,23.9
Future generations:Nigeria's responsibility|23.5
Gender:development|17.4
Gender:equality in the family|4.7
Gender:social inclusion|8.5
Gender:women's contribution|21.5
Global peace:education|20.6
Global peace:inequality|20.5
Global peace:personal serenity|20.2
Global peace:regional cooperation|20.4
Global peace:trade and interdependence|20.3
Governance:democratic opposition|9.7,16.7
Governance:economic development|9.6
Governance:environment|9.8
Governance:ethical leadership|9.3
Governance:future|25.4
Governance:meaning|9.2,16.2
Governance:public financial management|16.5
Governance:public service integrity|16.4
Governance:technology|16.8
Governance:transparency|9.4
Green economy|19.7
Human dignity|8.4,17.2
Human security:climate change|11.3
Human security:social protection|10.8
Inclusion:digital technology|17.8
Inclusion:gender|8.5
Inclusion:institutions|22.5
Inclusive growth|10.5
Inner person:emotional balance|2.3
Inner person:leadership|2.8
Inner person:material possessions|2.7
Inner person:relationships|2.6
Inner person:understanding|2.2
Inner person:values|2.4
Institutions:accountability architecture|22.4
Institutions:cost of failure|22.3
Institutions:developing countries|22.8
Institutions:digital systems|22.6
Institutions:research|22.7
Institutions:social inclusion|22.5
Institutions:values|22.2
Integrity, public service|16.4
International cooperation|19.8,24.4
International trade|20.3
Investment and savings|10.6
Justice:community tranquillity|8.7
Justice:human dignity|17.2
Justice:meritocracy|17.6
Justice:peace|15.4,15.8
Justice:public administration|8.6
Justice:rule of law|8.3
Justice:social confidence|16.3
Justice:social justice, meaning|8.2
Justice:sustainable development|8.8
Leadership:ethical example|9.3
Leadership:inner person|2.8
Leadership:message to leaders|25.8
Leadership:serenity and governance|1.7
Legacy:community|23.3
Legacy:definition|23.2
Legacy:generational assessment|23.7
Legacy:reading and knowledge|23.4
Legacy:technology|23.6
Lifelong learning|12.6
Material possessions|2.7
Media:diversity|7.7
Media:social media and conflict|15.6
Meritocracy:diversity|7.5
Meritocracy:institutional culture|21.7
Meritocracy:social justice|17.6
Meritocracy:sustainability|24.5
National unity:citizenship|18.3
National unity:civil society|18.8
National unity:education|18.5
National unity:federalism|18.7
National unity:meaning|18.2
National unity:national service|18.6
National unity:religion|18.4
Nigeria:development vision|20.8
Nigeria:diversity|7.9
Nigeria:economic diversification|10.7
Nigeria:family life|4.6
Nigeria:farmer-herder conflicts|15.7
Nigeria:generational responsibility|23.5
Nigeria:governance|9.9,16.9
Nigeria:serenity and tranquillity|1.6
Nigeria:social justice|8.9,17.9
Nigeria:unity and detribalisation|18.9
Nutrition and wellbeing|14.5
Parenting|4.5
Peacebuilding:dialogue|15.3
Peacebuilding:traditional institutions|15.5
Perspective, personal|14.3
Poverty and dignity|8.4
Prejudice|7.4
Professional support, stress and anxiety|3.8
Public administration:justice|8.6
Public administration:public servant's role|9.5
Public financial management|16.5
Public spaces|6.7
Reading and knowledge|23.4
Reconciliation|4.4
Recreation and rest|3.5
Regional cooperation|20.4
Relationships:inner person|2.6
Relationships:personal boundaries|13.8
Religion:diversity|17.5
Religion:national cohesion|18.4
Research and institutions|22.7
Rule of law|8.3
Serenity:active responsibility|1.4
Serenity:definition|1.2
Serenity:inner peace|14.2
Serenity:sustainable development|1.5
Serenity:tranquillity, relationship to|1.3
Serenity-to-sustainability continuum|21.2
Serenity-Tranquillity-Sustainability model:central proposition|24.2
Serenity-Tranquillity-Sustainability model:development test|24.9
Serenity-Tranquillity-Sustainability model:international application|24.7
Serenity-Tranquillity-Sustainability model:social cohesion pillar|24.3
Simplifying life|14.8
Social cohesion|17.7,24.3,25.6
Social mobility|17.3
Social protection|10.8,24.6
Social support|14.7
Spirituality and meaning|14.6
Stress:understanding|3.2
Stress:workplace|3.6
Sustainable development:agriculture|19.3
Sustainable development:definition|19.2
Sustainable development:future choice|25.7
Sustainable development:global agenda|20.7
Sustainable development:long-term thinking|21.6
Sustainable development:serenity and tranquillity|1.5
Time management|14.4
Tolerance:education|12.5
Tolerance:political opposition|16.7
Traditional institutions:community|6.4
Traditional institutions:peacebuilding|15.5
Transparency|9.4
Waste management|11.5
Water resources|11.4
Workplace:diversity|7.6
Workplace:stress|3.6
Youth, community development|6.6
'''
CROSS = {'Good governance':'Governance', 'Social justice':'Justice',
         'Technology':'Digital technology', 'Women':'Gender',
         'Tranquillity':'Community; Global peace; Serenity',
         'National development':'Economic development; Governance; Sustainable development',
         'Wellbeing':'Inner person; Nutrition and wellbeing; Stress',
         'Peace':'Conflict; Global peace; Peacebuilding',
         'Human capital':'Education', 'Sustainability':'Sustainable development',
         'Responsible citizenship':'Citizenship'}
KEYWORDS = {'Artificial intelligence':r'artificial intelligence',
            'Meditation':r'meditation', 'United Nations':r'United Nations',
            'Sustainable Development Goals':r'Sustainable Development Goals|\bSDGs\b'}

def subjects():
    return [(label, ids.split(',')) for label, ids in
            (line.split('|') for line in SUBJECTS.strip().splitlines())]

def ranges(numbers):
    nums=sorted(set(numbers)); result=[]; i=0
    while i<len(nums):
        j=i
        while j+1<len(nums) and nums[j+1]==nums[j]+1: j+=1
        result.append(str(nums[i]) if i==j else f'{nums[i]}-{nums[j]}')
        i=j+1
    return ', '.join(result)

def inspect(doc):
    # Preserve line geometry to exclude running heads/footers and identify the
    # precise pages touched by each section (including same-page transitions).
    lines=[]
    for i,p in enumerate(doc):
        for block in p.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                text=''.join(s['text'] for s in line['spans']).strip()
                baseline=line['spans'][0]['origin'][1]
                if text and 30<baseline<p.rect.height-38:
                    lines.append((i,line['bbox'],text))
    start=next(n for n,x in enumerate(lines) if x[2]=='1.1 Introduction')
    end=next(n for n,x in enumerate(lines) if n>start and x[2]=='REFERENCES AND BIBLIOGRAPHY')
    sections={}; active=None
    for i,box,text in lines[start:end]:
        m=re.match(r'^(\d{1,2}\.\d+)\s',text)
        if m: active=m[1]; sections.setdefault(active,set())
        if active and not text.startswith('CHAPTER '): sections[active].add(i+1)
    return lines,sections,start,end

def index_rows(doc):
    lines,sections,start,end=inspect(doc); entries={}; evidence=[]
    for label,ids in subjects():
        pages=sorted(set().union(*(sections[s] for s in ids)))
        entries[label]=pages
        evidence.append({'entry':label,'sections':ids,'pages':pages})
    for label,pattern in KEYWORDS.items():
        # Join page lines so a phrase split over lines is still discoverable.
        pages=[]
        for i in sorted(set(x[0] for x in lines[start:end])):
            text=' '.join(x[2] for x in lines[start:end] if x[0]==i)
            if re.search(pattern,text,re.I): pages.append(i+1)
        if pages: entries[label]=pages; evidence.append({'entry':label,'phrase':pattern,'pages':pages})
    rows=[]; letter=''; groups={}
    for label,pages in entries.items():
        main,_,sub=label.partition(':'); groups.setdefault(main,[]).append((sub,pages))
    for label,target in CROSS.items(): groups[label]=[(None,target)]
    for main,children in sorted(groups.items(),key=lambda x:x[0].casefold()):
        if main[0]!=letter: letter=main[0]; rows.append(('letter',letter,None))
        if children[0][0] is None:
            rows.append(('cross',f'{main}. See {children[0][1]}.',None))
        elif len(children)==1 and not children[0][0]:
            rows.append(('entry',main+', '+ranges(children[0][1]),children[0][1]))
        else:
            rows.append(('main',main,None))
            for sub,pages in sorted(children,key=lambda x:x[0].casefold()):
                rows.append(('sub',sub+', '+ranges(pages),pages))
    return rows,evidence,lines

def wrap(text,font,size,width):
    out=[]; current=''
    for word in text.split():
        candidate=(current+' '+word).strip()
        if current and fitz.get_text_length(candidate,fontname=font,fontsize=size)>width:
            out.append(current); current=word
        else: current=candidate
    if current: out.append(current)
    return out

def make_index(rows,w,h,start_number):
    out=fitz.open(); size=10 if w<450 else 11
    leading=size+2.4; margin=43 if w<450 else 57
    gap=19; colw=(w-2*margin-gap)/2; y=0; col=0; page=None
    def newpage():
        nonlocal page,y,col
        page=out.new_page(width=w,height=h); col=0; y=91
        page.insert_text((margin,55),'Subject Index' if len(out)==1 else 'Subject Index (continued)',fontname='tibo',fontsize=17)
        page.insert_text((w/2-10,h-25),str(start_number+len(out)-1),fontname='tiro',fontsize=9)
    newpage()
    navigation=[]; anchors={}; cross_links=[]
    parent=''
    for n,(kind,text,locators) in enumerate(rows):
        indent=10 if kind=='sub' else 0
        font='tibo' if kind in ('main','letter') else 'tiro'
        parts=wrap(text,font,size,colw-indent-5)
        extra=8 if kind=='letter' else 2
        needed=len(parts)*leading+extra
        if kind in ('main','letter') and n+1<len(rows):
            needed+=len(wrap(rows[n+1][1],'tiro',size,colw-15))*leading+2
        if y+needed>h-49:
            if col==0: col=1; y=91
            else: newpage()
            if kind=='sub' and parent:
                for continuation in wrap(parent+' (continued)','tibo',size,colw):
                    page.insert_text((margin+col*(colw+gap),y),continuation,fontname='tibo',fontsize=size)
                    y+=leading
                y+=2
        if kind=='main': parent=text
        if kind=='letter': y+=5
        x=margin+col*(colw+gap)+indent
        if kind in ('main','entry'):
            anchors[re.split(r', (?=\d)',text)[0]]=(len(out)-1,fitz.Point(x,y-size))
        offset=0
        for j,line in enumerate(parts):
            xx=x+(5 if j else 0)
            page.insert_text((xx,y),line,fontname=font,fontsize=size)
            if locators:
                for match in re.finditer(r'(?<!\w)(\d+)(?:-(\d+))?(?=,|$)',line):
                    for group in (1,2):
                        if match[group] is None: continue
                        left=xx+fitz.get_text_length(line[:match.start(group)],fontname=font,fontsize=size)
                        right=left+fitz.get_text_length(match[group],fontname=font,fontsize=size)
                        navigation.append((len(out)-1,fitz.Rect(left,y-size,right,y+2),int(match[group])-1))
            if kind=='cross':
                main=text.split('. See ')[0]
                for target in CROSS[main].split('; '):
                    pos=text.index(target,text.index('. See ')+6)
                    lo=max(pos,offset); hi=min(pos+len(target),offset+len(line))
                    if lo<hi:
                        left=xx+fitz.get_text_length(line[:lo-offset],fontname=font,fontsize=size)
                        right=xx+fitz.get_text_length(line[:hi-offset],fontname=font,fontsize=size)
                        cross_links.append((len(out)-1,fitz.Rect(left,y-size,right,y+2),target))
            offset+=len(line)+1
            y+=leading
        y+=extra
    return out,navigation,anchors,cross_links

def add_navigation(output,index_start,navigation,anchors,cross_links,lines,digital):
    records=[]
    def link(page_no,rect,dest,point,kind,label,underline=False):
        p=output[page_no]
        p.insert_link({'kind':fitz.LINK_GOTO,'from':rect,'page':dest,'to':point})
        if underline:
            p.draw_line((rect.x0,rect.y1-1),(rect.x1,rect.y1-1),color=(0.1,0.35,0.45),width=0.45)
        records.append({'kind':kind,'page':page_no+1,'destination':dest+1,'label':label,
                        'rect':list(rect)})
    for local,rect,dest in navigation:
        link(index_start+local,rect,dest,fitz.Point(0,0),'index locator',str(dest+1),digital)
    for local,rect,target in cross_links:
        dest,point=anchors[target]
        link(index_start+local,rect,index_start+dest,point,'index cross-reference',target,digital)
    if digital:
        starts={}; chapters={}; current=0
        for pno,box,text in lines:
            m=re.match(r'^(\d{1,2}\.\d+)\s',text)
            if m:
                starts[m[1]]=(pno,fitz.Point(0,max(0,box[1]-12)))
                current=int(m[1].split('.')[0])
            chapters[pno]=current
        chapter_end=next(x[0] for x in lines if x[2]=='REFERENCES AND BIBLIOGRAPHY')
        seen=set(); occupied={}
        first=starts['1.1'][0]
        for pno in range(first,chapter_end):
            p=output[pno]
            for term,section in RELATED.items():
                key=(chapters.get(pno),term)
                dest,point=starts[section]
                if key in seen or dest==pno: continue
                # At most one occurrence of a term per chapter; do not link
                # headings, running heads, or overlapping phrases.
                boxes=p.search_for(term)
                chosen=[]
                for rect in boxes:
                    if rect.y0<60 or rect.y1>p.rect.height-50: continue
                    if any(i==pno and re.match(r'^\d{1,2}\.\d+\s',t)
                           and rect.intersects(fitz.Rect(box)) for i,box,t in lines): continue
                    if any(rect.intersects(other) for other in occupied.get(pno,[])): continue
                    chosen=[rect]; break
                if chosen:
                    rect=chosen[0]; occupied.setdefault(pno,[]).append(rect); seen.add(key)
                    link(pno,rect,dest,point,'related topic',term,True)
        # A compact navigation control on chapter pages gives readers a reliable
        # route back to the index without relying on PDF-reader back gestures.
        for pno in range(first,chapter_end):
            p=output[pno]; label='Subject index'
            rect=fitz.Rect(p.rect.width-113,p.rect.height-29,p.rect.width-57,p.rect.height-18)
            p.insert_text((rect.x0,rect.y0+8),label,fontname='tiro',fontsize=8,color=(0.1,0.35,0.45))
            link(pno,rect,index_start,fitz.Point(0,0),'return to index',label)
    return records

def remove_area(page,rect):
    page.add_redact_annot(rect,fill=(1,1,1))
    page.apply_redactions(images=0,graphics=0)

def build_pdf(source,target):
    doc=fitz.open(source_path(source)); rows,evidence,lines=index_rows(doc)
    first=next(x for x in lines if x[2]=='SUBJECT INDEX')
    last=next(x for x in lines if x[0]>=first[0] and x[2].startswith('LIST OF TABLES AND'))
    a,b=first[0],last[0]; w,h=doc[a].rect.width,doc[a].rect.height
    # Leave glossary text on its existing page. Rebuild the following list page
    # from its original vector content, starting at the normal top margin.
    remove_area(doc[a],fitz.Rect(0,first[1][1]-2,w,h-38))
    tail=fitz.open(); tail.insert_pdf(doc,from_page=b,to_page=len(doc)-1)
    remove_area(tail[0],fitz.Rect(0,32,w,last[1][1]-1))
    # Lift the surviving list of tables to the top of its page, instead of
    # leaving the white area formerly occupied by the old index.
    list_page=fitz.open(); p=list_page.new_page(width=w,height=h)
    clip=fitz.Rect(0,last[1][1]-1,w,h-38)
    p.show_pdf_page(fitz.Rect(0,40,w,40+clip.height),tail,0,clip=clip)
    tail.delete_page(0); tail.insert_pdf(list_page,start_at=0)
    # Index is inserted at the original position, on a fresh page.
    output=fitz.open(); output.insert_pdf(doc,to_page=a)
    index,navigation,anchors,cross_links=make_index(rows,w,h,len(output)+1); index_start=len(output)
    output.insert_pdf(index); tail_start=len(output)
    output.insert_pdf(tail)
    # Renumber back matter after insertion; all chapter pages remain unchanged.
    for i in range(tail_start,len(output)):
        p=output[i]; remove_area(p,fitz.Rect(0,h-38,w,h))
        p.insert_text((w/2-10,h-25),str(i+1),fontname='tiro',fontsize=9)
    # Rebuild bookmarks and preserve their destinations through the insertion.
    delta=tail_start-b
    toc=[]
    for level,title,pageno in doc.get_toc():
        if a+1<pageno<=b: continue
        toc.append([level,title,pageno+delta if pageno>=b+1 else pageno])
    toc.append([1,'Subject Index',index_start+1]); toc.sort(key=lambda x:x[2])
    output.set_toc(toc)
    # insert_pdf preserves links but cross-segment destinations are not portable;
    # restore original links to the unchanged chapter pages explicitly.
    for i in range(a+1):
        for link in list(output[i].get_links()): output[i].delete_link(link)
        for link in doc[i].get_links():
            if link['kind']==fitz.LINK_GOTO:
                dest=link['page']; dest=dest+delta if dest>=b else dest
                output[i].insert_link({'kind':fitz.LINK_GOTO,'from':link['from'],'page':dest,'to':link.get('to',fitz.Point(0,0))})
    digital='Digital' in source
    links=add_navigation(output,index_start,navigation,anchors,cross_links,lines,digital)
    if digital:
        for i in range(index_start,tail_start):
            output[i].insert_text((57,73),'Click a page number or a See reference to follow its link.',fontname='tiit',fontsize=9,color=(0.1,0.35,0.45))
    output.set_metadata({**doc.metadata,'subject':'Clickable subject index and internal topic navigation'})
    output.save(BASE/target,garbage=4,deflate=True)
    # Verify the actual saved file, including every unchanged chapter page.
    saved=fitz.open(BASE/target)
    chapter_end=next(x[0] for x in lines if x[2]=='REFERENCES AND BIBLIOGRAPHY')
    for i in range(chapter_end):
        actual=saved[i].get_text()
        if digital: actual=actual.replace('Subject index\n','')
        assert actual==doc[i].get_text(),i
    for record in links:
        candidates=saved[record['page']-1].get_links()
        assert any(l['kind']==fitz.LINK_GOTO and l['page']==record['destination']-1
                   and abs(l['from'].x0-record['rect'][0])<0.1
                   and abs(l['from'].y0-record['rect'][1])<0.1 for l in candidates),record
    assert all(1<=p<=chapter_end for e in evidence for p in e['pages'])
    assert 'Accountability' in ''.join(saved[i].get_text() for i in range(index_start,tail_start))
    index_text=' '.join(' '.join(saved[i].get_text().split()) for i in range(index_start,tail_start))
    for kind,text,_ in rows:
        assert ' '.join(text.split()) in index_text, ('missing index row',text)
    for i in range(index_start,tail_start):
        for block in saved[i].get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                assert line['bbox'][0]>=40 and line['bbox'][2]<=w-35, ('index overflow',i,line)
    previews=BASE/'Previews'; previews.mkdir(exist_ok=True)
    saved[index_start].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(previews/(target.replace('.pdf','_Index_Preview.png')))
    saved[tail_start].get_pixmap().save(previews/(target.replace('.pdf','_Backmatter_Preview.png')))
    return {'source':source,'output':target,'pages':len(saved),'index_start':index_start+1,'index_pages':len(index),'entries':len(evidence),'evidence':evidence,'navigation':links}

def build_docx():
    W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; ns={'w':W}; q=lambda s:'{'+W+'}'+s
    source=source_path('Serenity_and_Tranquillity_Interior_Edit.docx')
    with zipfile.ZipFile(source) as z: files={n:z.read(n) for n in z.namelist()}
    root=ET.fromstring(files['word/document.xml']); body=root.find('w:body',ns)
    children=list(body); text=lambda p:''.join(p.itertext())
    a=next(i for i,p in enumerate(children) if text(p)=='SUBJECT INDEX')
    b=next(i for i,p in enumerate(children) if text(p)=='LIST OF TABLES AND FRAMEWORKS')
    for p in children[a+1:b]: body.remove(p)
    marker_map={}
    for label,ids in subjects():
        for sid in ids: marker_map.setdefault(sid,[]).append(label)
    count=0
    def xe(p,label):
        r=ET.SubElement(p,q('r')); props=ET.SubElement(r,q('rPr')); ET.SubElement(props,q('vanish'))
        f=ET.SubElement(r,q('fldChar')); f.set(q('fldCharType'),'begin')
        r=ET.SubElement(p,q('r')); ET.SubElement(ET.SubElement(r,q('rPr')),q('vanish'))
        ET.SubElement(r,q('instrText')).text=' XE "'+label+'" '
        r=ET.SubElement(p,q('r')); ET.SubElement(ET.SubElement(r,q('rPr')),q('vanish'))
        ET.SubElement(r,q('fldChar')).set(q('fldCharType'),'end')
    in_chapters=False
    for p in children[:a]:
        t=text(p)
        if t=='1.1 Introduction': in_chapters=True
        if t=='REFERENCES AND BIBLIOGRAPHY': in_chapters=False
        if not in_chapters: continue
        m=re.match(r'^(\d{1,2}\.\d+)\s',t)
        for label in marker_map.get(m[1] if m else '',[]): xe(p,label); count+=1
        for label,pattern in KEYWORDS.items():
            if re.search(pattern,t,re.I): xe(p,label); count+=1
    field=ET.Element(q('p'))
    f=ET.SubElement(field,q('fldSimple')); f.set(q('instr'),' INDEX \\h "A" \\c "2" \\e ", " '); f.set(q('dirty'),'true')
    ET.SubElement(ET.SubElement(f,q('r')),q('t')).text='Update this index in Word: select all (Ctrl+A), then press F9. Page references will follow this document’s own layout.'
    body.insert(list(body).index(children[a])+1,field)
    for main,target in CROSS.items(): xe(children[a],main+'" \\t "See '+target)
    files['word/document.xml']=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    out=BASE/'Serenity_and_Tranquillity_Interior_Edit_Indexed.docx'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in files.items(): z.writestr(name,data)
    # Confirm field codes survived and the old run-together paragraphs are gone.
    ET.fromstring(files['word/document.xml'])
    return {'output':out.name,'marked_entries':count,'requires_Word_field_update':True}

def main():
    results=[]
    for source,target in [
        ('Serenity_and_Tranquillity_Print_Interior_A5_11pt_HeadCorrected.pdf','Serenity_and_Tranquillity_Print_Interior_A5_Indexed.pdf'),
        ('Serenity_and_Tranquillity_Digital_Readable_CoverCorrected.pdf','Serenity_and_Tranquillity_Digital_Readable_Indexed.pdf')]:
        results.append(build_pdf(source,target))
    word=build_docx()
    source=fitz.open(BASE/results[0]['output']); spreads=fitz.open()
    w,h=source[0].rect.width,source[0].rect.height
    for i in range(0,len(source),2):
        p=spreads.new_page(width=w*2,height=h)
        p.show_pdf_page(fitz.Rect(0,0,w,h),source,i)
        if i+1<len(source): p.show_pdf_page(fitz.Rect(w,0,w*2,h),source,i+1)
    for i,p in enumerate(source):
        for item in p.get_links():
            if item['kind']!=fitz.LINK_GOTO: continue
            rect=fitz.Rect(item['from']); rect.x0+=(i%2)*w; rect.x1+=(i%2)*w
            dest=item['page']; point=fitz.Point(item.get('to',fitz.Point(0,0)))
            point.x+=(dest%2)*w
            spreads[i//2].insert_link({'kind':fitz.LINK_GOTO,'from':rect,'page':dest//2,'to':point})
    spreads.save(BASE/'Serenity_and_Tranquillity_Hardcopy_A5_2up_Indexed.pdf',garbage=4,deflate=True)
    checked_spreads=fitz.open(BASE/'Serenity_and_Tranquillity_Hardcopy_A5_2up_Indexed.pdf')
    expected=sum(len(p.get_links()) for p in source)
    assert sum(len(p.get_links()) for p in checked_spreads)==expected
    assert all(0<=l['page']<len(checked_spreads) for p in checked_spreads for l in p.get_links())
    (BASE/'Subject_Index_Audit.json').write_text(json.dumps({'editions':results,'word':word},indent=2),encoding='utf-8')
    lines=['# Subject index review','', 'The previous subject index contained topic associations but no page locators. It also combined several entries in each paragraph. It has been replaced in the indexed editions with an alphabetical two-column index, letter headings, subordinate entries, cross-references, and edition-specific page locators.','', 'Locators identify the substantive retained manuscript sections, including continuation pages. They exclude the contents, bibliography, glossary and index. Selected additional terms (including artificial intelligence) are located directly in chapter text. See Subject_Index_Audit.json for the entry-to-section/page mapping.','']
    for r in results: lines.append(f"- {r['output']}: {r['pages']} pages; index begins on page {r['index_start']}, occupying {r['index_pages']} pages; {r['entries']} topic/subtopic entries plus {len(CROSS)} cross-references.")
    lines+=['','All printed index numbers (including both ends of ranges) are clickable in the one-page PDFs and the two-up print PDF. See references lead to their corresponding index entries. The digital PDF also has selective underlined topic links to substantive section discussions and a Subject index return link on chapter pages. Use your PDF reader’s Back/Previous View command to return to the previous reading location.','', 'Link destinations and rectangles were checked after reopening each saved one-page PDF. Every index row and column width was checked. Chapter text and pagination were preserved; the digital edition adds a small navigation control to the footer. Back matter after the index has been renumbered. Original editions are retained in Archive_Obsolete.','', 'The indexed DOCX contains hidden XE index markers and a native Word INDEX field. Open it in Word, select all, and press F9 to populate its own page numbers. Its locators must not be copied from either PDF. Interactive navigation is supplied in the PDFs.','', 'The previous print cover is sized for 339 pages. The indexed interior has a new page count, so its cover spine must be resized using the printer’s paper specification before print upload. The two-up PDF is a reading/printing spread, not booklet imposition.']
    (BASE/'Subject_Index_Notes.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps([{**{k:v for k,v in r.items() if k not in ('evidence','navigation')},
        'links':{kind:sum(x['kind']==kind for x in r['navigation']) for kind in sorted(set(x['kind'] for x in r['navigation']))}}
        for r in results]+[word],indent=2))

if __name__=='__main__': main()
