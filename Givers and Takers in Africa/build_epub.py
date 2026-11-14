"""Create a reflowable EPUB from the preserved source manuscript."""
from pathlib import Path
from html import escape
import re, uuid, zipfile, ast
import build_manuscript as book

BASE=Path(__file__).resolve().parent
OUT=BASE/'Working_Manuscript'/'Givers_and_Takers_in_Africa.epub'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
CSS='''body{font-family:serif;line-height:1.55;margin:0 5%;overflow-wrap:anywhere}h1{font-size:1.6em;line-height:1.2;margin:1.5em 0 .7em;color:#173f35;overflow-wrap:anywhere}h2{font-size:1.2em;line-height:1.25;margin:1.5em 0 .6em;color:#173f35;overflow-wrap:anywhere}p{margin:.65em 0}a{color:#173f35}.title{text-align:center;margin-top:20vh}.title h1{font-size:2em}.subtitle{font-size:1.1em}.author{margin-top:2em}.index{list-style:none;padding:0}.index li{margin:.6em 0}.cover{margin:0;text-align:center}.cover img{height:96vh;max-width:100%;object-fit:contain}table{border-collapse:collapse;width:100%;font-size:.9em}td,th{border:1px solid #999;padding:.35em;vertical-align:top}'''
INDEX_TREE=ast.parse((BASE/'build_pdf_indexes.py').read_text(encoding='utf-8'))
SUBJECTS=next(ast.literal_eval(n.value) for n in INDEX_TREE.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SUBJECTS' for t in n.targets))
CROSS=next(ast.literal_eval(n.value) for n in INDEX_TREE.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CROSS' for t in n.targets))
RELATED=next(ast.literal_eval(n.value) for n in INDEX_TREE.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RELATED' for t in n.targets))

def xhtml(title, body):
    return ('<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en-GB" xml:lang="en-GB"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>'+escape(title)+'</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>'+body+'</body></html>')

def build():
    chapters=book.collect_chapters(); back=book.collect_backmatter()
    docs=[]; nav=[]; sections=[]
    cover_file=BASE/'Production'/'Cover_Front_OnlineStore.jpg'
    coverbody='<section class="cover" epub:type="cover"><img src="Cover_Front_OnlineStore.jpg" alt="Front cover of Givers and Takers in Africa"/></section>'
    docs.append(('cover.xhtml','Cover',xhtml('Cover',coverbody),'cover'))
    nav.append(('cover.xhtml','Cover'))
    titlebody=f'<section class="title"><h1>{escape(book.TITLE)}</h1><p class="subtitle">{escape(book.SUBTITLE)}</p><p class="author">{escape(book.AUTHOR)}</p><p>{escape(book.PUBLISHER)}</p></section>'
    docs.append(('title.xhtml',book.TITLE,xhtml(book.TITLE,titlebody),'titlepage'))
    nav.append(('title.xhtml','Title page'))
    for n,label,title,paras in chapters:
        name=f'chapter-{n:02}.xhtml'; out=[f'<h1 id="chapter-title">Chapter {n}: {escape(title)}</h1>']; active=None; buff=[]; seen_topics=set()
        for p in paras:
            if book.SECTION_RE.match(p):
                if buff: out.extend(f'<p>{link_paragraph(x,n,seen_topics)}</p>' for x in buff); buff=[]
                sid='s-'+re.match(r'^(\d+\.\d+)',p).group(1).replace('.','-')
                out.append(f'<h2 id="{sid}">{escape(p)}</h2>'); sections.append((p,name,sid))
            else: buff.append(p)
        if buff: out.extend(f'<p>{link_paragraph(x,n,seen_topics)}</p>' for x in buff)
        docs.append((name,f'Chapter {n}: {title}',xhtml(title,''.join(out)),'chapter'))
        nav.append((name,f'Chapter {n}: {title}'))
    # Preserve back matter text. The policy recommendation rows are represented in a semantic HTML table.
    body=[]; i=0
    while i<len(back):
        t=back[i]
        if t=='No.' and i+64<=len(back):
            rows=[back[i+j:i+j+4] for j in range(0,64,4)]
            if len(rows)==16 and rows[0]==['No.','Policy Area','Recommended Action','Expected Outcome']:
                body.append('<table><thead><tr>'+''.join('<th>'+escape(c)+'</th>' for c in rows[0])+'</tr></thead><tbody>')
                body.extend('<tr>'+''.join('<td>'+escape(c)+'</td>' for c in row)+'</tr>' for row in rows[1:]); body.append('</tbody></table>'); i+=64; continue
        if book.TOP_BACK_RE.match(t): body.append('<h1>'+escape(t)+'</h1>')
        else: body.append('<p>'+escape(t)+'</p>')
        i+=1
    docs.append(('back-matter.xhtml','Back Matter',xhtml('Back Matter','<h1>Back Matter</h1>'+''.join(body)),'backmatter'))
    nav.append(('back-matter.xhtml','Back Matter'))
    idx=['<h1>Subject Index</h1><ul class="index">']
    index=[]
    for label,ids in sorted(SUBJECTS.items(),key=lambda x:x[0].casefold()):
        locs=[]
        for sid in ids.split(','):
            chapter=int(sid.split('.')[0]); fn=f'chapter-{chapter:02}.xhtml'; anchor='s-'+sid.replace('.','-')
            locs.append((fn,anchor))
        index.append((label,locs))
        idx.append('<li id="index-'+slug(label)+'"><strong>'+escape(label)+'</strong>: '+', '.join(f'<a href="{fn}#{sid}">{sid[2:].replace("-",".")}</a>' for fn,sid in locs)+'</li>')
    for term,target in CROSS.items():
        idx.append('<li>'+escape(term)+': See <a href="#index-'+slug(target)+'">'+escape(target)+'</a></li>')
    idx.append('</ul>')
    docs.append(('subject-index.xhtml','Subject Index',xhtml('Subject Index',''.join(idx)),'index'))
    nav.append(('subject-index.xhtml','Subject Index'))
    navxml='<nav xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" epub:type="toc" id="toc"><h1>Contents</h1><ol>'+''.join(f'<li><a href="{escape(f)}">{escape(t)}</a></li>' for f,t in nav)+'</ol></nav>'
    files={'nav.xhtml':xhtml('Contents',navxml),'style.css':CSS,'Cover_Front_OnlineStore.jpg':cover_file.read_bytes()}
    for f,_,data,_ in docs: files[f]=data
    uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'resyin:givers-and-takers-in-africa:epub:source-v1'))
    manifest=['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>','<item id="css" href="style.css" media-type="text/css"/>','<item id="cover-image" href="Cover_Front_OnlineStore.jpg" media-type="image/jpeg" properties="cover-image"/>']
    spine=[]
    for j,(f,t,_,kind) in enumerate(docs):
        manifest.append(f'<item id="d{j}" href="{f}" media-type="application/xhtml+xml"/>'); spine.append(f'<itemref idref="d{j}"/>')
    opf=f'''<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="en-GB"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="uid">urn:uuid:{uid}</dc:identifier><dc:title>{escape(book.TITLE)}</dc:title><dc:language>en-GB</dc:language><dc:creator>{escape(book.AUTHOR)}</dc:creator><dc:publisher>{escape(book.PUBLISHER)}</dc:publisher><dc:description>{escape(book.SUBTITLE)}</dc:description><meta property="dcterms:modified">2026-11-14T00:00:00Z</meta></metadata><manifest>{''.join(manifest)}</manifest><spine>{''.join(spine)}</spine></package>'''
    files['package.opf']=opf
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(OUT,'w') as z:
        z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml','''<?xml version="1.0"?><container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0"><rootfiles><rootfile full-path="package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>''')
        for f,data in files.items(): z.writestr(f,data,compress_type=zipfile.ZIP_DEFLATED)
    print(f'{OUT}\nChapters: {len(chapters)}; numbered sections: {len(sections)}; subject terms: {len(index)}; cover included.')

def link_paragraph(text,chapter,section_items):
    mappings={}
    for term,sid in RELATED.items():
        n=int(sid.split('.')[0]); mappings[term]=(f'chapter-{n:02}.xhtml','s-'+sid.replace('.','-'))
    matches=[]
    for term,target in mappings.items():
        if term in section_items: continue
        m=re.search(re.escape(term),text,re.I)
        if m and int(target[0][8:10])!=chapter: matches.append((m.start(),m.end(),term,target))
    matches.sort(); chosen=[]; last=0
    for item in matches:
        if item[0]>=last: chosen.append(item); last=item[1]
    out=[]; last=0
    for a,b,term,(fn,sid) in chosen:
        out.append(escape(text[last:a])); out.append(f'<a href="{fn}#{sid}">{escape(text[a:b])}</a>'); section_items.add(term); last=b
    out.append(escape(text[last:]))
    return ''.join(out)

def slug(text):
    return re.sub(r'[^a-z0-9]+','-',text.casefold()).strip('-')
if __name__=='__main__': build()
