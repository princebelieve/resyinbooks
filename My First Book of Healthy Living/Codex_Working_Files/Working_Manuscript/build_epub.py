from pathlib import Path
import re, zipfile, uuid, datetime
base=Path('My First Book of Healthy Living'); w=base/'Codex_Working_Files'/'Working_Manuscript'; d=base/'For_Professor'
s=(w/'Healthy_Living_Final_Book.html').read_text(encoding='utf-8')
s=s.replace('Selected_Illustrations/png_review/','Images/').replace('../Production/Healthy_Living_Front_Cover_Working_Reference.png','Images/cover.png')
s=s.replace('“','"').replace('”','"').replace('’',"'").replace('—','-').replace('–','-').replace('©','&#169;')
# Give the contents, glossary entries and topic finder stable, human-readable targets.
slug=lambda value: re.sub(r'[^a-z0-9]+','-',value.lower()).strip('-')
s=re.sub(r'<h2(?: id="contents")?>Contents</h2>',r'<h2 id="contents">Contents</h2>',s)
s=re.sub(r'<h2(?: id="find-a-topic")?>Find a Topic</h2>',r'<h2 id="find-a-topic">Find a Topic</h2>',s)
g=s.find('<h2 id="glossary">Glossary</h2>')
if g<0:g=s.find('<h2>Glossary</h2>')
if g>=0:
    s=s[:g]+re.sub(r'<p><strong>([^<]+):</strong>',lambda m:f'<p id="glossary-{slug(m.group(1))}"><strong>{m.group(1)}:</strong>',s[g:])
s=re.sub(r'<p><strong>New words:</strong>\s*(.*?)</p>',lambda m:'<p><strong>New words:</strong> '+', '.join(f'<a href="#glossary-{slug(x.strip())}">{x.strip()}</a>' for x in m.group(1).split(','))+'</p><p class="navigation"><a href="#contents">Contents</a> | <a href="#find-a-topic">Find a Topic</a></p>',s)
# title page follows the digital front cover
title='<section class="titlepage"><h1>MY FIRST BOOK OF HEALTHY LIVING</h1><p>A Children&#39;s Guide to Personal Well-Being, Healthy Habits and Responsible Living</p><p>By Prof. Johnson Agharese Egonmwan</p><p>Resyin (NG) Consults</p></section>'
s=s.replace('</figure>','</figure>'+title,1)
s=s.replace('<!doctype html>','<?xml version="1.0" encoding="utf-8"?>',1)
s=s.replace('<html lang="en">','<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">')
s=re.sub(r'<meta charset="utf-8">','<meta charset="utf-8" />',s)
s=re.sub(r'<meta name="viewport"([^>]*)>','<meta name="viewport"\\1 />',s)
s=re.sub(r'<img([^>]*)>',lambda m:'<img'+m.group(1).rstrip('/')+' />',s)
s=re.sub(r'<hr([^>]*)>',lambda m:'<hr'+m.group(1).rstrip('/')+' />',s)
# EPUB remains reflowable and lets reading apps enlarge text; it has no print page dimensions.
epub_css='''<style>html{font-size:112%}body{margin:0 5%;font-family:serif;line-height:1.65;color:#263238}h1,h2,h3{line-height:1.25;break-after:avoid}h1{font-size:1.65em;color:#0b2c62}h2{font-size:1.35em;color:#0b2c62}h3{font-size:1.15em;color:#167340}p{margin:.7em 0;orphans:2;widows:2}a{color:#0b5d42;text-decoration:underline}.cover{text-align:center}.cover img{max-width:100%;height:auto}.storyboard{margin:1em auto;text-align:center}.storyboard img{max-width:100%;height:auto}.navigation{font-size:.92em;margin:1.2em 0}.remember,.promise{padding:.6em;border-left:.25em solid #167340;background:#eef6e8}.worktable{width:100%;border-collapse:collapse}.worktable td,.worktable th{padding:.35em;border:1px solid #89999b}li{margin:.35em 0}</style>'''
s=re.sub(r'<style>.*?</style>',epub_css,s,flags=re.S)
navitems=[]
titles=['Understanding Healthy Living','Eating Well: Food That Helps Us Grow','Exercise, Play and Physical Fitness','Personal Hygiene and Cleanliness','Preventive Healthcare: Staying Healthy and Safe','Managing Stress, Feelings and Emotions','Sleep, Rest and Relaxation','Balancing School, Chores, Play and Family Life','Developing Healthy Daily Habits','Personal Well-Being: Building a Healthy Future']
for n,t in enumerate(titles,1):navitems.append(f'<li><a href="book.xhtml#chapter-{n}">{t}</a></li>')
navitems.append('<li><a href="book.xhtml#find-a-topic">Find a Topic</a></li>')
nav='<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en"><head><title>Contents</title><meta charset="utf-8" /></head><body><nav epub:type="toc"><h1 id="contents">Contents</h1><ol>'+''.join(navitems)+'</ol></nav></body></html>'
manifest='<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="book" href="book.xhtml" media-type="application/xhtml+xml"/><item id="cover" href="Images/cover.png" media-type="image/png" properties="cover-image"/>'
for n in range(1,11):manifest+=f'<item id="img{n}" href="Images/Chapter_{n:02d}.png" media-type="image/png"/>'
uid='urn:uuid:'+str(uuid.uuid4());modified=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
opf=f'<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="id">{uid}</dc:identifier><dc:title>My First Book of Healthy Living</dc:title><dc:creator>Prof. Johnson Agharese Egonmwan</dc:creator><dc:publisher>Resyin (NG) Consults</dc:publisher><dc:language>en</dc:language><meta property="dcterms:modified">{modified}</meta></metadata><manifest>{manifest}</manifest><spine><itemref idref="book"/></spine></package>'
out=d/'My_First_Book_of_Healthy_Living.epub'
with zipfile.ZipFile(out,'w') as z:
 z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
 z.writestr('META-INF/container.xml','<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
 z.writestr('EPUB/package.opf',opf);z.writestr('EPUB/nav.xhtml',nav);z.writestr('EPUB/book.xhtml',s)
 z.write(d/'Cover_Front.png','EPUB/Images/cover.png')
 for n in range(1,11):z.write(d/'Illustrations'/f'Chapter_{n:02d}.png',f'EPUB/Images/Chapter_{n:02d}.png')
print(out,out.stat().st_size)
