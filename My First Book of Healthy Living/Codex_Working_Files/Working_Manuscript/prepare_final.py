from pathlib import Path
import re, shutil
base=Path(r'My First Book of Healthy Living')
work=base/'Codex_Working_Files'/'Working_Manuscript'
src=work/'My_First_Book_of_Healthy_Living_Working_Manuscript.md'
text=src.read_text(encoding='utf-8-sig')
text=text.replace('**Developmental working manuscript — Version 1**\n\n*Prepared from Professor\'s supplied raw material. This is an editorial working draft, not a final proof.*\n\n','')
text=text.replace('## Copyright Page (working text)','## Copyright')
text=re.sub(r'ISBN: to be verified and assigned by the publisher for each format before publication\.\n\n','',text)
text=re.sub(r'\n\*The copyright wording and imprint follow the approved copyright page in\*.*?\n','\n',text,flags=re.S)
text=text.replace('The situations and child characters in this working draft are fictional examples created to teach the ideas.','The child characters in this book are fictional examples created to teach the ideas.')
text=text.replace('## A Note to Parents, Teachers and Caregivers','## A Note to Parents, Teachers and Caregivers')
# Add a complete contents list before chapter one.
anchor='# CHAPTER ONE'
contents='''## Contents\n\n1. Understanding Healthy Living\n2. Eating Well: Food That Helps Us Grow\n3. Exercise, Play and Physical Fitness\n4. Personal Hygiene and Cleanliness\n5. Preventive Healthcare: Staying Healthy and Safe\n6. Managing Stress, Feelings and Emotions\n7. Sleep, Rest and Relaxation\n8. Balancing School, Chores, Play and Family Life\n9. Developing Healthy Daily Habits\n10. Personal Well-Being: Building a Healthy Future\n\nMy Healthy Living Pledge\nMy Weekly Healthy Habits Reflection\nGlossary\nQuestions for Revision\nReferences for Adults\nAbout the Author\n\n'''
if '## Contents\n' not in text: text=text.replace(anchor,contents+anchor,1)
out=work/'My_First_Book_of_Healthy_Living_Final_Manuscript.md'
out.write_text(text,encoding='utf-8')
# Make the reusable renderer take the cleaned book text and selected full-size art.
r=work/'render_illustrated_preview.py'; s=r.read_text(encoding='utf-8')
s=s.replace('SOURCE = ROOT / "My_First_Book_of_Healthy_Living_Working_Manuscript.md"','SOURCE = ROOT / "My_First_Book_of_Healthy_Living_Final_Manuscript.md"')
s=s.replace('OUT = ROOT / "Illustrated_Review_Prototype.html"','OUT = ROOT / "Healthy_Living_Final_Book.html"')
s=s.replace('<div class="notice"><strong>DEVELOPMENTAL REVIEW PROTOTYPE — NOT A FINAL PRINT FILE.</strong> The illustrated chapter cards are native-size crops from Prof\'s supplied ten-panel storyboard. They are included to show the children\'s-book direction; their embedded small text and resolution need replacing with original high-resolution chapter art before final print layout.</div>','')
s=s.replace('Selected_Illustrations/png_review/Chapter_{ch:02d}.png','Selected_Illustrations/png_review/Chapter_{ch:02d}.png')
s=s.replace('out.append(f\'<h1 class="{cls}">{inline(stripped[2:])}</h1>\')','out.append(f\'<h1 class="{cls}" id="chapter-{ch}">{inline(stripped[2:])}</h1>\' if ch else f\'<h1 class="{cls}">{inline(stripped[2:])}</h1>\')')
s=s.replace('Chapter {ch} illustration · review artwork','Chapter {ch} illustration')
r.write_text(s,encoding='utf-8')
# Move the selected set into reusable production-source location; copies remain untouched.
sel=work/'Selected_Illustrations'/'png_review'
delivery=base/'For_Professor'
for n in range(1,11):
    shutil.copy2(sel/f'Chapter_{n:02d}.png',delivery/'Illustrations'/f'Chapter_{n:02d}.png')
shutil.copy2(base/'Codex_Working_Files'/'Production'/'Healthy_Living_Front_Cover_Working_Reference.png',delivery/'Cover_Front.png')
print(out)
