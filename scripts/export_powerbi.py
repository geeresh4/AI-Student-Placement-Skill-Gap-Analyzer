import os
from pathlib import Path
from urllib.request import Request,urlopen
base=os.getenv('API_URL','http://localhost:8000'); token=os.getenv('OFFICER_TOKEN'); out=Path('data/exports'); out.mkdir(parents=True,exist_ok=True)
if not token: raise SystemExit('Set OFFICER_TOKEN from officer login, or use the Reports UI')
for kind in ['students','outcomes','gaps','model']:
    req=Request(f'{base}/api/officer/export/{kind}',headers={'Authorization':'Bearer '+token}); (out/f'{kind}.csv').write_bytes(urlopen(req).read()); print('exported',kind)
