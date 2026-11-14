"""Add native Word XE markers and an INDEX field to a separate production copy."""
from pathlib import Path
import sys, zipfile, xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'Serenity and Tranquillity'/'.python_libs'))
import build_pdf_indexes as idx

BASE=Path(__file__).resolve().parent; WORK=BASE/'Working_Manuscript'; PROD=BASE/'Production'
NS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; ET.register_namespace('w',NS)
q=lambda name:'{'+NS+'}'+name

def visible(p): return ''.join((x.text or '') for x in p.iter(q('t')))
def xe(paragraph,label,see=None):
    r=ET.SubElement(paragraph,q('r')); props=ET.SubElement(r,q('rPr')); ET.SubElement(props,q('vanish')); ET.SubElement(r,q('fldChar')).set(q('fldCharType'),'begin')
    r=ET.SubElement(paragraph,q('r')); props=ET.SubElement(r,q('rPr')); ET.SubElement(props,q('vanish')); instr=ET.SubElement(r,q('instrText')); instr.set('{http://www.w3.org/XML/1998/namespace}space','preserve'); instr.text=' XE "'+label.replace('"','\\"')+'"'+(' \\t "See '+see+'"' if see else '')+' '
    r=ET.SubElement(paragraph,q('r')); props=ET.SubElement(r,q('rPr')); ET.SubElement(props,q('vanish')); ET.SubElement(r,q('fldChar')).set(q('fldCharType'),'end')

def main():
    src=WORK/'Givers_and_Takers_in_Africa_Manuscript_Edit.docx'; out=PROD/'Givers_and_Takers_in_Africa_Manuscript_Edit_Indexed.docx'; PROD.mkdir(exist_ok=True)
    with zipfile.ZipFile(src) as z: files={n:z.read(n) for n in z.namelist()}
    root=ET.fromstring(files['word/document.xml']); body=root.find(q('body')); children=list(body); markers=0
    marker_map={}
    for label,ids in idx.SUBJECTS.items():
        for sid in ids.split(','): marker_map.setdefault(sid,[]).append(label)
    for p in children:
        t=visible(p)
        style=p.find('w:pPr/w:pStyle',{'w':NS})
        if style is None or style.get(q('val'))!='Heading2': continue
        import re
        m=re.match(r'^(\d+\.\d+)\s',t)
        if not m: continue
        for label in marker_map.get(m.group(1),[]): xe(p,label); markers+=1
    # Insert an index heading and native Word INDEX field after the supplied back matter.
    heading=ET.Element(q('p')); ppr=ET.SubElement(heading,q('pPr')); ET.SubElement(ppr,q('pStyle')).set(q('val'),'FrontHead'); ET.SubElement(ppr,q('pageBreakBefore'))
    run=ET.SubElement(heading,q('r')); text=ET.SubElement(run,q('t')); text.text='SUBJECT INDEX'
    for label,target in idx.CROSS.items(): xe(heading,label,see=target)
    fieldp=ET.Element(q('p')); ppr=ET.SubElement(fieldp,q('pPr')); ET.SubElement(ppr,q('pStyle')).set(q('val'),'Normal')
    fld=ET.SubElement(fieldp,q('fldSimple')); fld.set(q('instr'),' INDEX \\h "A" \\c "2" \\e ", " '); fld.set(q('dirty'),'true')
    r=ET.SubElement(fld,q('r')); t=ET.SubElement(r,q('t')); t.text='Open in Word, select all, and press F9 to populate the subject index page references.'
    sect=body.find(q('sectPr')); pos=list(body).index(sect) if sect is not None else len(body)
    body.insert(pos,heading); body.insert(pos+1,fieldp)
    files['word/document.xml']=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in files.items(): z.writestr(name,data)
    print(f'{out}\nNative Word index markers: {markers}; index field: present; original master unchanged.')
if __name__=='__main__': main()
