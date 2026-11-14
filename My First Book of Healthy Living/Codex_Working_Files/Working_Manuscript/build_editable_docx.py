from pathlib import Path
from html import escape
import re, zipfile
base=Path('My First Book of Healthy Living'); work=base/'Codex_Working_Files'/'Working_Manuscript'; delivery=base/'For_Professor'
txt=(work/'My_First_Book_of_Healthy_Living_Final_Manuscript.md').read_text(encoding='utf-8-sig')
lines=txt.splitlines(); lines=lines[next((i+1 for i,x in enumerate(lines) if x.strip()=='---'),0):]
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'; A='http://schemas.openxmlformats.org/drawingml/2006/main'; WP='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'; PIC='http://schemas.openxmlformats.org/drawingml/2006/picture'
def clean(s):
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1 (\2)',s)
 return s.replace('**','').replace('*','').replace('“','"').replace('”','"').replace('’',"'").replace('—','-').replace('–','-')
def para(s='',size=26,bold=False,color=None,align=None,page=False,after=140):
 pp=[]
 if page:pp.append('<w:pageBreakBefore/>')
 if align:pp.append(f'<w:jc w:val="{align}"/>')
 pp.append(f'<w:spacing w:after="{after}" w:line="300" w:lineRule="auto"/>')
 clr=f'<w:color w:val="{color}"/>' if color else ''
 rpr=f'<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="{size}"/>{"<w:b/>" if bold else ""}{clr}</w:rPr>'
 run=f'<w:r>{rpr}<w:t xml:space="preserve">{escape(clean(s),quote=False)}</w:t></w:r>' if s else ''
 return f'<w:p><w:pPr>{"".join(pp)}</w:pPr>{run}</w:p>'
def image(n):
 cx=4114800;cy=6172200;rid=f'rIdImg{n}'
 return f'<w:p><w:pPr><w:pageBreakBefore/><w:jc w:val="center"/></w:pPr><w:r><w:drawing><wp:inline><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{n}" name="Chapter illustration {n}"/><wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="{A}" noChangeAspect="1"/></wp:cNvGraphicFramePr><a:graphic xmlns:a="{A}"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="{PIC}"><pic:nvPicPr><pic:cNvPr id="{n}" name="Chapter_{n:02d}.png"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
parts=[para('MY FIRST BOOK OF HEALTHY LIVING',40,True,'167340','center',False,320),para("A Children's Guide to Personal Well-Being, Healthy Habits and Responsible Living",28,False,None,'center',False,1000),para('By Prof. Johnson Agharese Egonmwan',28,False,None,'center',False,500),para('Resyin (NG) Consults',24,False,None,'center',False,3000)]
n=0;skip=False;imagebreak=False;front={'Copyright','Dedication','Preface','A Note to Parents, Teachers and Caregivers','How to Use This Book','Contents','My Healthy Living Pledge','My Weekly Healthy Habits Reflection','Glossary','Questions for Revision','References for Adults','About the Author'}
for raw in lines:
 s=raw.strip()
 if not s or s=='---':continue
 if s.startswith('# CHAPTER '):n+=1;parts.append(image(n));skip=True;imagebreak=True;continue
 if s.startswith('# '):parts.append(para(s[2:],34,True,'0B2C62',page=True));continue
 if s.startswith('## '):
  h=s[3:]
  if skip:skip=False;continue
  parts.append(para(h,28,True,'0B2C62',page=h in front));continue
 if s.startswith('### '):parts.append(para(s[4:],24,True,'167340',page=imagebreak));imagebreak=False;continue
 if s.startswith('|'):
  cells=[c.strip() for c in s.strip('|').split('|')]
  if all(re.fullmatch(r':?-{2,}:?',c.replace(' ','')) for c in cells):continue
  parts.append(para('   |   '.join(cells),22));continue
 if s.startswith(('- ','* ')):s='•  '+s[2:]
 parts.append(para(s,26,page=imagebreak));imagebreak=False
body=''.join(parts)
doc=f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{W}" xmlns:r="{R}" xmlns:wp="{WP}" xmlns:a="{A}"><w:body>{body}<w:sectPr><w:pgSz w:w="8391" w:h="11906"/><w:pgMar w:top="720" w:right="760" w:bottom="800" w:left="760" w:header="300" w:footer="360"/></w:sectPr></w:body></w:document>'
styles=f'<?xml version="1.0" encoding="UTF-8"?><w:styles xmlns:w="{W}"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="26"/><w:lang w:val="en-GB"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:widowControl/></w:pPr></w:pPrDefault></w:docDefaults></w:styles>'
ct='''<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'''
root='''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
rels=[f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>']
for k in range(1,11):rels.append(f'<Relationship Id="rIdImg{k}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/Chapter_{k:02d}.png"/>')
relxml='<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(rels)+'</Relationships>'
out=delivery/'My_First_Book_of_Healthy_Living_Editable_Manuscript.docx'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml',ct);z.writestr('_rels/.rels',root);z.writestr('word/document.xml',doc);z.writestr('word/styles.xml',styles);z.writestr('word/_rels/document.xml.rels',relxml)
 for k in range(1,11):z.write(delivery/'Illustrations'/f'Chapter_{k:02d}.png',f'word/media/Chapter_{k:02d}.png')
print(out,out.stat().st_size)
