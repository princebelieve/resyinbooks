from pathlib import Path
import sys
sys.path.insert(0,r'Serenity and Tranquillity/Codex_Working_Files/.python_libs')
import fitz
base=Path('My First Book of Healthy Living/For_Professor')
src=fitz.open(base/'My_First_Book_of_Healthy_Living_Print_Interior_A5.pdf')
out=fitz.open()
for i in range(0,len(src),2):
 page=out.new_page(width=842,height=595)
 page.show_pdf_page(fitz.Rect(0,0,421,595),src,i,keep_proportion=True)
 if i+1<len(src):page.show_pdf_page(fitz.Rect(421,0,842,595),src,i+1,keep_proportion=True)
# This output is for printing; it intentionally carries no interactive annotations.
out.set_metadata({'title':'My First Book of Healthy Living - A5 two-up print file','author':'Prof. Johnson Agharese Egonmwan','producer':'Resyin Publications'})
dest=base/'My_First_Book_of_Healthy_Living_Hardcopy_A5_2up.pdf';out.save(dest,garbage=4,deflate=True);print(dest,len(out),dest.stat().st_size)
