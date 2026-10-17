"""Render an isolated temporary copy; never changes the source PPTX.
Usage: python tools/render_source.py source.pptx output-directory
Requires LibreOffice/soffice on PATH. Font substitution is for intermediate
render placement; the final native HTML uses embedded Jost.
"""
import sys,zipfile,re,shutil,subprocess
from pathlib import Path
source=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve()
out.mkdir(parents=True,exist_ok=True)
target=out/'render-source.pptx'
with zipfile.ZipFile(source) as z,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as w:
 for item in z.infolist():
  data=z.read(item.filename)
  if item.filename.startswith('ppt/') and item.filename.endswith('.xml'):
   data=re.sub(rb'typeface="[^"]*"',b'typeface="Arial"',data)
  w.writestr(item,data)
exe=shutil.which('soffice') or shutil.which('libreoffice')
if not exe:raise SystemExit('Install LibreOffice and add soffice to PATH.')
subprocess.run([exe,'-env:UserInstallation='+str((out/'lo-profile').as_uri()),'--headless','--convert-to','pdf','--outdir',str(out),str(target)],check=True)
print(out/'render-source.pdf')
