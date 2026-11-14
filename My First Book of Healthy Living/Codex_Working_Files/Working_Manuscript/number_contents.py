from pathlib import Path
import re, sys
sys.path.insert(0, r'Serenity and Tranquillity/Codex_Working_Files/.python_libs')
import pymupdf as fitz

delivery=Path(r'My First Book of Healthy Living/For_Professor')
files=['My_First_Book_of_Healthy_Living_Print_Interior_A5',
       'My_First_Book_of_Healthy_Living_Digital_Readable_A4']

def opener_pages(pdf):
    doc=fitz.open(pdf); found=[]
    for i,page in enumerate(doc):
        blocks=page.get_text('dict')['blocks']
        large=[b for b in blocks if b.get('type')==1 and
               (b['bbox'][2]-b['bbox'][0])>page.rect.width*.52 and
               (b['bbox'][3]-b['bbox'][1])>page.rect.height*.55]
        if large: found.append(i+1)
    # Digital PDF begins with the cover image; exclude it from the ten chapter openers.
    if len(found)>10: found=found[-10:]
    if len(found)!=10: raise ValueError(f'Expected 10 chapter artwork pages in {pdf}, found {found}')
    return found

for stem in files:
    html=delivery/(stem+'.html'); pdf=delivery/(stem+'.pdf')
    s=html.read_text(encoding='utf-8')
    nums=opener_pages(pdf)
    a=s.index('<h1 class="front-section" id="contents">Contents</h1>')
    b=s.index('<h1 class="chapter-title"',a)
    section=s[a:b]
    def add(m):
        n=int(m.group(1))
        return f'<li><a href="#chapter-{n}">{m.group(2)}<span class="page-reference">{nums[n-1]}</span></a></li>'
    section,count=re.subn(r'<li><a href="#chapter-(\d+)">(.*?)</a></li>',add,section,count=10,flags=re.S)
    if count!=10: raise ValueError(f'Expected 10 chapter links in {stem}; updated {count}')
    s=s[:a]+section+s[b:]
    s=s.replace('li{margin-bottom:4pt}', 'li{margin-bottom:4pt}.page-reference{float:right;color:#52615c;font-size:11pt}a{color:#0b5d42;text-decoration:underline}.navigation{font:12pt Arial,sans-serif;margin:12pt 0}')
    if stem.endswith('Print_Interior_A5'):
        # Print copies have page locators, not inert clickable annotations.
        s=re.sub(r'<a\b[^>]*>(.*?)</a>',r'\1',s,flags=re.S)
    html.write_text(s,encoding='utf-8')
    print(stem,nums)
