"""Prepare an EPUB preview tree and structural report for mobile reflow review."""
from pathlib import Path, PurePosixPath
import zipfile, json, xml.etree.ElementTree as ET, re
BASE=Path(__file__).resolve().parent; PROD=BASE/'Production'; EPUB=BASE.parent/'For_Professor'/'Givers_and_Takers_in_Africa.epub'
PREVIEW=PROD/'EPUB_Preview'; REPORT=PROD/'EPUB_Validation'; PREVIEW.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(EPUB) as z:
    names=z.namelist()
    for name in names:
        path=PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts: raise ValueError('Unsafe EPUB member path: '+name)
    z.extractall(PREVIEW)
    assert z.read('mimetype')==b'application/epub+zip' and z.infolist()[0].filename=='mimetype' and z.infolist()[0].compress_type==zipfile.ZIP_STORED
opf=ET.parse(PREVIEW/'package.opf').getroot(); ns={'o':'http://www.idpf.org/2007/opf','x':'http://www.w3.org/1999/xhtml'}
items={x.attrib['id']:x.attrib for x in opf.findall('.//o:manifest/o:item',ns)}
spine=[x.attrib['idref'] for x in opf.findall('.//o:spine/o:itemref',ns)]
html_files=[PREVIEW/a['href'] for a in items.values() if a['media-type']=='application/xhtml+xml']
ids={p.name:set(re.findall(r'\bid=["\']([^"\']+)',p.read_text(encoding='utf-8'))) for p in html_files}
links=0; missing=[]
for p in html_files:
    text=p.read_text(encoding='utf-8')
    for href in re.findall(r'href=["\']([^"\']+)',text):
        if href.startswith(('http:','https:','mailto:')): continue
        links+=1; file,_,frag=href.partition('#'); target=(p.parent/file).resolve() if file else p
        if not target.exists(): missing.append({'file':p.name,'href':href,'error':'missing file'})
        elif frag and frag not in ids.get(target.name,set()): missing.append({'file':p.name,'href':href,'error':'missing fragment'})
report={'epub':EPUB.name,'package_members':len(names),'xhtml_documents':len(html_files),'spine_documents':len(spine),'internal_links_checked':links,'missing_targets':missing,'cover_image':items.get('cover-image'),'chapter_documents':sum(p.name.startswith('chapter-') for p in html_files),'mimetype_first_uncompressed':True}
(REPORT/'Structure_Report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))
