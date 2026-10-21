import argparse,json
from pathlib import Path
import joblib
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',default='models/placement_model.joblib');a=p.parse_args();f=Path(a.model)
    if not f.exists(): raise SystemExit('No trained artifact; run scripts/train_model.py first.')
    item=joblib.load(f);print(json.dumps({'version':item['version'],'dataset_source':item['source'],'sample_count':item['sample_count'],'label':item['label'],'metrics':item['metrics'],'limitations':'Stored holdout evaluation; synthetic-demo metrics only do not establish field validity.'},indent=2,default=float))
