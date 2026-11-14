from pathlib import Path
import subprocess,tempfile
base=Path(r'My First Book of Healthy Living/For_Professor'); chrome=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
for name in ['Print_Interior_A5','Digital_Readable_A4']:
 h=base/f'My_First_Book_of_Healthy_Living_{name}.html'; pdf=base/f'My_First_Book_of_Healthy_Living_{name}.pdf'
 profile=tempfile.mkdtemp(prefix='healthy-final-')
 r=subprocess.run([chrome,'--headless=new','--disable-gpu','--no-sandbox','--no-pdf-header-footer',f'--user-data-dir={profile}',f'--print-to-pdf={pdf.resolve()}',h.resolve().as_uri()],capture_output=True,text=True,timeout=240)
 print(pdf.name,r.returncode,pdf.stat().st_size if pdf.exists() else -1)
