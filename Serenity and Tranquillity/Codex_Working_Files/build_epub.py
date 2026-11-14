"""Create a reflowable EPUB 3 from the editable manuscript, with no PDF extraction.

Python standard library only. Run EPUBCheck separately after building.
"""
from pathlib import Path, PurePosixPath
import ast
from collections import defaultdict
from datetime import datetime, timezone
from html import escape
import json
import posixpath
import re
import uuid
import zipfile
import xml.etree.ElementTree as ET

BASE=Path(__file__).resolve().parent
PROJECT=BASE.parent
DELIVERY=PROJECT/'For_Professor'
OUT=DELIVERY/'Serenity_and_Tranquillity.epub'
W={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
H={'h':'http://www.w3.org/1999/xhtml'}
TITLE='Serenity and Tranquillity'
SUBTITLE='In Personal Life, Community Life, National Development and the Future of Humanity'
AUTHOR='Prof. Johnson Agharese Egonmwan'
UID='urn:uuid:'+str(uuid.uuid5(uuid.NAMESPACE_URL,'resyin:serenity-and-tranquillity:epub:2026'))

CSS='''
html { font-size: 100%; }
body { margin: 0 5%; font-family: serif; line-height: 1.5; }
h1, h2, h3 { line-height: 1.25; text-align: left; break-after: avoid; }
h1 { font-size: 1.65em; margin: 1.5em 0 1em; }
h2 { font-size: 1.25em; margin: 1.5em 0 .7em; }
h3 { font-size: 1.1em; margin: 1em 0 .4em; }
p { margin: .65em 0; orphans: 2; widows: 2; }
a { text-decoration: underline; }
.titlepage { text-align: center; }
.titlepage h1 { text-align: center; margin-top: 2em; }
.subtitle { font-size: 1.2em; }
.tagline { font-style: italic; }
.author { margin-top: 2em; }
.chapter-title { font-size: 1.3em; font-weight: bold; margin-bottom: 1.5em; }
.navigation { font-size: .9em; margin-top: 2em; }
.cover { margin: 0; text-align: center; }
.cover img { width: 100%; max-width: 100%; height: auto; }
nav ol { padding-left: 1.3em; }
nav li { margin: .45em 0; }
.references p { margin-left: 1em; text-indent: -1em; }
dl { margin: .7em 0; }
dt { font-weight: bold; margin-top: .75em; }
dd { margin: .25em 0 .6em 1em; }
.index { padding-left: 0; list-style-type: none; }
.index li { margin: .55em 0; }
.index ul { list-style-type: none; padding-left: 1.2em; }
.letters { line-height: 2; }
'''

def config():
    tree=ast.parse((BASE/'build_subject_index.py').read_text(encoding='utf-8'))
    result={}
    for item in tree.body:
        if isinstance(item,ast.Assign):
            for target in item.targets:
                if isinstance(target,ast.Name) and target.id in {'SUBJECTS','CROSS','KEYWORDS','RELATED'}:
                    result[target.id]=ast.literal_eval(item.value)
    return result

def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def text(p): return ''.join(x.text or '' for x in p.findall('.//w:t',W)).strip()
def xhtml(title,body,kind='bodymatter'):
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en-GB" xml:lang="en-GB">'
        '<head><title>'+escape(title)+'</title><meta charset="utf-8"/>'
        '<link rel="stylesheet" type="text/css" href="styles/book.css"/></head>'
        '<body epub:type="'+kind+'">'+body+'</body></html>')

def read_manuscript():
    with zipfile.ZipFile(DELIVERY/'Serenity_and_Tranquillity_Interior_Edit_Indexed.docx') as z:
        root=ET.fromstring(z.read('word/document.xml'))
    docs=[]; current=None; chapter=0; skipped=[]; isbn=[]
    special={'GLOSSARY OF KEY TERMS','SUBJECT INDEX','LIST OF TABLES AND FRAMEWORKS',"AUTHOR'S NOTE",'BACK MATTER'}
    for i,p in enumerate(root.findall('w:body/w:p',W)):
        t=text(p)
        if not t: continue
        style=p.find('w:pPr/w:pStyle',W)
        style=style.get('{'+W['w']+'}val') if style is not None else ''
        if p.find('.//w:fldSimple',W) is not None:
            skipped.append({'paragraph':i,'reason':'Word-generated contents/index placeholder'}); continue
        if t.startswith('ISBN '):
            isbn.append({'paragraph':i,'text':t,'reason':'Invalid source ISBN checksum; no ebook ISBN supplied'}); continue
        if current is None:
            current={'file':'title.xhtml','title':TITLE,'kind':'titlepage','items':[],'chapter':0}; docs.append(current)
        if style=='Heading1':
            chapter+=1
            current={'file':f'chapter-{chapter:02}.xhtml','title':f'Chapter {chapter}', 'kind':'chapter','items':[],'chapter':chapter}
            docs.append(current)
        elif style in {'FrontHead','PartTitle'} or t in special:
            kind='part' if style=='PartTitle' else 'frontmatter' if chapter==0 else 'backmatter'
            if t=='TABLE OF CONTENTS': kind='toc'
            elif t=='SUBJECT INDEX': kind='index'
            elif t=='GLOSSARY OF KEY TERMS': kind='glossary'
            elif t=='REFERENCES AND BIBLIOGRAPHY': kind='bibliography'
            name=slug(t)
            suffix=sum(d['file'].startswith(name) for d in docs)
            name+=('-'+str(suffix+1)) if suffix else ''
            current={'file':name+'.xhtml','title':t.title(),'kind':kind,'items':[],'chapter':chapter if kind=='chapter' else 0}
            docs.append(current)
        is_title=not current['items']
        item={'text':t,'style':style,'id':f'p-{i}','source':i,'heading':is_title}
        m=re.match(r'^(\d{1,2}\.\d+)\s',t)
        if m and style=='Heading2': item['section']=m[1]; item['id']='section-'+m[1].replace('.','-')
        if current['kind']=='chapter' and len(current['items'])==1:
            current['title']=f'Chapter {chapter}: '+t.title(); item['subtitle']=True
        current['items'].append(item)
    assert chapter==25
    return docs,skipped,isbn

def build():
    DELIVERY.mkdir(parents=True,exist_ok=True)
    cfg=config(); docs,skipped,isbn=read_manuscript(); files={}; sections={}; targets={}; related_links=[]
    for d in docs:
        for item in d['items']:
            if 'section' in item:
                sections[item['section']]={'href':d['file']+'#'+item['id'],'title':item['text']}
    assert len(sections)==250
    def anchor(uri,label): return '<a href="'+escape(uri,quote=True)+'">'+escape(label)+'</a>'
    def inline(d,item,seen):
        t=item['text']
        if d['kind']!='chapter' or item.get('heading') or item.get('subtitle') or 'section' in item: return escape(t)
        # At most one occurrence of each related term per chapter. Skip links
        # whose destination is the section currently being read.
        matches=[]
        for term,sid in cfg['RELATED'].items():
            if term in seen or sid==item.get('active_section'): continue
            m=re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',t,re.I)
            if m: matches.append((m.start(),m.end(),term,sid))
        matches.sort(); result=[]; last=0
        for a,b,term,sid in matches:
            if a<last: continue
            result.extend([escape(t[last:a]),anchor(sections[sid]['href'],t[a:b])]); last=b; seen.add(term)
            related_links.append({'chapter':d['chapter'],'term':term,'source':d['file']+'#'+item['id'],'target':sections[sid]['href']})
        result.append(escape(t[last:])); return ''.join(result)
    # Identify paragraph locations for supplementary index terms; do not search
    # front matter, bibliography, glossary, or generated index text.
    for label,pattern in cfg['KEYWORDS'].items():
        matches=[]; seen_sections=set()
        for d in docs:
            if d['kind']!='chapter': continue
            active=''
            for item in d['items']:
                if 'section' in item: active=item['section']
                if re.search(pattern,item['text'],re.I) and active not in seen_sections:
                    matches.append((d['file']+'#'+item['id'],'Section '+active)); seen_sections.add(active)
        targets[label]=matches
    subjects=[(label,ids.split(',')) for label,ids in (s.split('|') for s in cfg['SUBJECTS'].strip().splitlines())]
    for label,ids in subjects:
        targets[label]=[(sections[s]['href'],'Section '+s) for s in ids]
    groups=defaultdict(list)
    for label,links in targets.items():
        main,_,sub=label.partition(':'); groups[main].append((sub,links))
    for main,target in cfg['CROSS'].items(): groups[main]=[(None,target)]
    letters=sorted(set(x[0] for x in groups))
    index=['<section epub:type="index" id="subject-index"><h1>Subject Index</h1>',
           '<p>Choose a section link to read the discussion. Ebook text adjusts to your screen, so this index uses section references rather than fixed page numbers.</p>',
           '<nav aria-label="Index letters" class="letters"><p>'+' · '.join(anchor('#letter-'+l,l) for l in letters)+'</p></nav>']
    for letter in letters:
        index.append(f'<section id="letter-{letter}"><h2>{letter}</h2><ul class="index">')
        for main in sorted((s for s in groups if s[0]==letter),key=str.casefold):
            children=groups[main]; index.append('<li id="idx-'+slug(main)+'"><strong>'+escape(main)+'</strong>')
            if children[0][0] is None:
                index.append('. See '+'; '.join(anchor('#idx-'+slug(t),t) for t in children[0][1].split('; '))+'.')
            elif len(children)==1 and not children[0][0]:
                index.append(': '+'; '.join(anchor(u,l) for u,l in children[0][1]))
            else:
                index.append('<ul>')
                for sub,links in sorted(children,key=lambda x:x[0].casefold()):
                    index.append('<li>'+escape(sub)+': '+'; '.join(anchor(u,l) for u,l in links)+'</li>')
                index.append('</ul>')
            index.append('</li>')
        index.append('</ul></section>')
    index.append('</section>')
    index_file=next(d['file'] for d in docs if d['kind']=='index')
    preserved=[]
    for d in docs:
        if d['kind'] in {'index','toc'}: continue
        body=[]; seen=set(); active=''; list_open=False
        if d['kind']=='titlepage': body.append('<section epub:type="titlepage" class="titlepage">')
        elif d['kind']=='bibliography': body.append('<section epub:type="bibliography" class="references">')
        else: body.append('<section>')
        if d['kind']=='glossary':
            body.append('<h1>'+escape(d['items'][0]['text'])+'</h1><dl>')
            rest=d['items'][1:]; assert len(rest)%2==0
            for term,definition in zip(rest[::2],rest[1::2]):
                body.append('<dt id="'+term['id']+'">'+escape(term['text'])+'</dt><dd id="'+definition['id']+'">'+escape(definition['text'])+'</dd>')
            body.append('</dl>'); preserved.extend(x['source'] for x in d['items'])
        else:
            for item in d['items']:
                if 'section' in item: active=item['section']
                item['active_section']=active; t=item['text']; ident=item['id']
                is_bullet=t.startswith('- ')
                if list_open and not is_bullet: body.append('</ul>'); list_open=False
                if is_bullet:
                    if not list_open: body.append('<ul>'); list_open=True
                    # Keep the manuscript's exact punctuation and words; the
                    # structural list replaces only the leading bullet marker.
                    copy={**item,'text':t[2:]}
                    body.append('<li id="'+ident+'">'+inline(d,copy,seen)+'</li>')
                else:
                    tag='h1' if item['heading'] else 'h2' if 'section' in item else 'p'
                    cls=''
                    if item.get('subtitle'): cls=' class="chapter-title"'
                    elif item['style'] in {'BookSubtitle','Tagline','AuthorLine'}:
                        cls=' class="'+{'BookSubtitle':'subtitle','Tagline':'tagline','AuthorLine':'author'}[item['style']]+'"'
                    body.append('<'+tag+' id="'+ident+'"'+cls+'>'+inline(d,item,seen)+'</'+tag+'>')
                preserved.append(item['source'])
            if list_open: body.append('</ul>')
        if d['kind']=='chapter':
            body.append('<p class="navigation">'+anchor('nav.xhtml#toc','Contents')+' · '+anchor(index_file+'#subject-index','Subject index')+'</p>')
        body.append('</section>')
        epub_kind='frontmatter' if d['kind'] in {'frontmatter','titlepage','part'} else 'bodymatter' if d['kind']=='chapter' else 'backmatter'
        files['EPUB/'+d['file']]=xhtml(d['title'],''.join(body),epub_kind)
    files['EPUB/'+index_file]=xhtml('Subject Index',''.join(index),'backmatter')
    files['EPUB/cover.xhtml']=xhtml('Cover','<section epub:type="cover" class="cover"><h1 hidden="hidden">Cover</h1><img src="images/cover.jpg" alt="Cover of Serenity and Tranquillity by Prof. Johnson Agharese Egonmwan"/></section>','cover')
    toc=['<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>']
    for d in docs:
        if d['kind']=='toc': continue
        uri=d['file']+('#subject-index' if d['kind']=='index' else '')
        toc.append('<li>'+anchor(uri,d['title']))
        if d['kind']=='chapter':
            toc.append('<ol>')
            for item in d['items']:
                if 'section' in item: toc.append('<li>'+anchor(d['file']+'#'+item['id'],item['text'])+'</li>')
            toc.append('</ol>')
        toc.append('</li>')
    toc.append('</ol></nav>')
    toc.append('<nav epub:type="landmarks" hidden="hidden"><h2>Landmarks</h2><ol>')
    for kind,uri,label in [('cover','cover.xhtml','Cover'),('titlepage','title.xhtml','Title page'),('toc','nav.xhtml#toc','Contents'),('bodymatter','chapter-01.xhtml','Start reading'),('index',index_file+'#subject-index','Subject index')]:
        toc.append('<li><a epub:type="'+kind+'" href="'+uri+'">'+label+'</a></li>')
    toc.append('</ol></nav>')
    files['EPUB/nav.xhtml']=xhtml('Contents',''.join(toc),'frontmatter')
    files['EPUB/styles/book.css']=CSS
    files['EPUB/images/cover.jpg']=(DELIVERY/'Cover_Front_OnlineStore_From_Original.jpg').read_bytes()
    spine=['cover.xhtml']+[('nav.xhtml' if d['kind']=='toc' else d['file']) for d in docs]
    assert len(spine)==len(set(spine))
    # NCX is included for older ebook readers in addition to EPUB 3 navigation.
    ncx=['<?xml version="1.0" encoding="utf-8"?><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="'+UID+'"/></head><docTitle><text>'+TITLE+'</text></docTitle><navMap>']
    titles={'cover.xhtml':'Cover','nav.xhtml':'Contents',**{d['file']:d['title'] for d in docs}}
    for i,name in enumerate(spine,1):
        ncx.append(f'<navPoint id="nav-{i}" playOrder="{i}"><navLabel><text>'+escape(titles[name])+'</text></navLabel><content src="'+name+'"/></navPoint>')
    ncx.append('</navMap></ncx>'); files['EPUB/toc.ncx']=''.join(ncx)
    modified=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    metadata=f'''<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="pub-id">{UID}</dc:identifier>
<dc:title id="title">{TITLE}</dc:title><meta refines="#title" property="title-type">main</meta>
<dc:creator id="author">{AUTHOR}</dc:creator><meta refines="#author" property="role" scheme="marc:relators">aut</meta>
<meta refines="#author" property="file-as">Egonmwan, Johnson Agharese</meta>
<dc:language>en-GB</dc:language><dc:publisher>Resyin (NG) Consults</dc:publisher>
<dc:rights>Copyright © 2026 Prof. Johnson Agharese Egonmwan. All rights reserved.</dc:rights>
<dc:description>{SUBTITLE}. A philosophy of personal serenity, community tranquillity, ethical governance and sustainable development, with particular attention to Nigeria and the shared future of humanity.</dc:description>
<dc:subject>Sustainable development</dc:subject><dc:subject>Peace and conflict studies</dc:subject><dc:subject>Personal development</dc:subject>
<meta property="dcterms:modified">{modified}</meta>
<meta property="rendition:layout">reflowable</meta><meta property="rendition:spread">auto</meta>
<meta name="cover" content="cover-image"/>
<meta property="schema:accessMode">textual</meta><meta property="schema:accessMode">visual</meta>
<meta property="schema:accessModeSufficient">textual</meta>
<meta property="schema:accessibilityFeature">structuralNavigation</meta><meta property="schema:accessibilityFeature">tableOfContents</meta>
<meta property="schema:accessibilityFeature">index</meta><meta property="schema:accessibilityFeature">alternativeText</meta>
<meta property="schema:accessibilityHazard">none</meta>
<meta property="schema:accessibilitySummary">Reflowable text with semantic headings and lists, linked contents and subject index, and alternative text for the cover. No fixed fonts or scripted interactions. Formal accessibility conformance has not been certified.</meta>
</metadata>'''
    manifest=[]; ids={}
    for i,name in enumerate(sorted(files),1):
        rel=name.removeprefix('EPUB/'); ident='item-'+str(i)
        media='application/xhtml+xml' if name.endswith('.xhtml') else 'text/css' if name.endswith('.css') else 'image/jpeg' if name.endswith('.jpg') else 'application/x-dtbncx+xml'
        props=''
        if rel=='nav.xhtml': props=' properties="nav"'
        elif rel=='images/cover.jpg': props=' properties="cover-image"'; ident='cover-image'
        ids[rel]=ident
        manifest.append('<item id="'+ident+'" href="'+rel+'" media-type="'+media+'"'+props+'/>')
    files['EPUB/package.opf']='<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id" prefix="rendition: http://www.idpf.org/vocab/rendition/# schema: http://schema.org/">'+metadata+'<manifest>'+''.join(manifest)+'</manifest><spine toc="'+ids['toc.ncx']+'">'+''.join('<itemref idref="'+ids[name]+'"/>' for name in spine)+'</spine></package>'
    files['META-INF/container.xml']='<?xml version="1.0" encoding="utf-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
    with zipfile.ZipFile(OUT,'w') as z:
        z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
        for name,data in files.items(): z.writestr(name,data,compress_type=zipfile.ZIP_DEFLATED)
    # Verify the saved artifact, not just the strings used to build it.
    report=validate(OUT)
    assert len(preserved)==len(set(preserved))
    expected=[x for d in docs if d['kind'] not in {'index','toc'} for x in d['items']]
    assert sorted(preserved)==sorted(x['source'] for x in expected)
    # Confirm every retained source paragraph survives exactly as visible text,
    # allowing only the removal of a structural leading bullet marker.
    with zipfile.ZipFile(OUT) as z:
        for d in docs:
            if d['kind'] in {'index','toc'}: continue
            root=ET.fromstring(z.read('EPUB/'+d['file']))
            elements={e.get('id'):e for e in root.iter() if e.get('id')}
            for item in d['items']:
                if d['kind']=='glossary' and item is d['items'][0]: continue
                actual=''.join(elements[item['id']].itertext())
                want=item['text'][2:] if item['text'].startswith('- ') else item['text']
                assert actual==want,(item['source'],actual,want)
    report.update({'output':OUT.name,'bytes':OUT.stat().st_size,'chapters':25,'sections':250,
        'source_paragraphs_preserved':len(preserved),'index_entries':len(targets),'cross_references':len(cfg['CROSS']),
        'related_topic_links':len(related_links),'source': 'Serenity_and_Tranquillity_Interior_Edit_Indexed.docx',
        'omitted_word_fields':skipped,'omitted_invalid_isbn':isbn,'identifier':UID,
        'epubcheck':'Run separately; see EPUB_Validation/epubcheck.txt',
        'related_link_evidence':related_links})
    validation=BASE/'EPUB_Validation'; validation.mkdir(exist_ok=True)
    (validation/'Structure_Report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    # Keep a representative chapter and stylesheet available for visual preview.
    preview=BASE/'Previews'/'EPUB'; (preview/'styles').mkdir(parents=True,exist_ok=True)
    (preview/'chapter-01.xhtml').write_text(files['EPUB/chapter-01.xhtml'],encoding='utf-8')
    (preview/'styles'/'book.css').write_text(CSS,encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in {'related_link_evidence','omitted_word_fields'}},indent=2))

def validate(path):
    links=0; fragments=0
    with zipfile.ZipFile(path) as z:
        names=z.namelist(); assert names[0]=='mimetype'
        assert z.getinfo('mimetype').compress_type==zipfile.ZIP_STORED
        assert z.read('mimetype')==b'application/epub+zip'
        assert len(names)==len(set(names))
        roots={}; idmap={}
        for name in names:
            if name.endswith(('.xml','.opf','.ncx','.xhtml')):
                root=ET.fromstring(z.read(name)); roots[name]=root
                ids=[e.get('id') for e in root.iter() if e.get('id')]
                assert len(ids)==len(set(ids)),name
                idmap[name]=set(ids)
        for name,root in roots.items():
            for e in root.iter():
                if e.tag.endswith('}img'): assert e.get('alt'),name
                for attr in ('href','src'):
                    uri=e.get(attr)
                    if not uri: continue
                    assert not re.match(r'^[a-z]+:',uri),('unexpected remote resource',uri)
                    target,_,fragment=uri.partition('#')
                    dest=posixpath.normpath(posixpath.join(posixpath.dirname(name),target)) if target else name
                    assert dest in names,(name,uri,dest)
                    if fragment: assert fragment in idmap[dest],(name,uri); fragments+=1
                    links+=1
        opf=roots['EPUB/package.opf']; ns={'o':'http://www.idpf.org/2007/opf'}
        manifest=opf.findall('o:manifest/o:item',ns); items={x.get('id'):x for x in manifest}
        assert len(items)==len(manifest)
        for item in opf.findall('o:spine/o:itemref',ns): assert item.get('idref') in items
        declared={posixpath.normpath('EPUB/'+x.get('href')) for x in manifest}
        assert declared==set(names)-{'mimetype','META-INF/container.xml','EPUB/package.opf'}
        assert sum(x.get('properties')=='nav' for x in manifest)==1
        assert sum(x.get('properties')=='cover-image' for x in manifest)==1
    return {'xml_and_package_checks':'passed','internal_links_and_resources_checked':links,'fragment_targets_checked':fragments}

if __name__=='__main__': build()
