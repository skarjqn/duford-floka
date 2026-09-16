"""Create the handoff archive from validated source, without build duplicates."""
import csv
import json
import zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
state=json.loads((root/'capture-manifest.json').read_text())
with (root/'PAGE-INVENTORY.csv').open('w',newline='',encoding='utf-8-sig') as stream:
    writer=csv.writer(stream);writer.writerow(['Source URL','Captured file','Source HTTP status','SHA-256'])
    for url,entry in sorted(state['pages'].items()):writer.writerow([url,entry['path'],entry.get('status',200),entry['sha256']])
destination=root.parent/'Floka-GitHub-Clone.zip'
excluded={'site','file-preview','github-preview','__pycache__','.git'}
with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for file in sorted(root.rglob('*')):
        if not file.is_file():continue
        rel=file.relative_to(root)
        if any(part in excluded for part in rel.parts) or file.name=='file-preview-build-report.json' or file.name=='preview-server.mjs':continue
        archive.write(file,'floka-github/'+str(rel))
with zipfile.ZipFile(destination) as archive:
    bad=archive.testzip()
    if bad:raise RuntimeError('Corrupt archive: '+bad)
    print(json.dumps({'archive':str(destination),'bytes':destination.stat().st_size,'files':len(archive.infolist()),'tested':True}))
