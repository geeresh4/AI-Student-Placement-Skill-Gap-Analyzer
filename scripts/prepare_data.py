import argparse
from pathlib import Path
import pandas as pd
REQUIRED=['student_id','cgpa','backlogs','internships','projects','aptitude','communication','program','graduation_year','placed']
def prepare(source:Path):
    df=pd.read_csv(source)
    missing=set(REQUIRED)-set(df.columns)
    if missing: raise ValueError('Required columns missing: '+', '.join(sorted(missing)))
    before=len(df); df=df.drop_duplicates(subset=['student_id'],keep='first').copy()
    labels=df['placed'].astype(str).str.strip().str.lower(); mapping={'1':1,'true':1,'yes':1,'placed':1,'0':0,'false':0,'no':0,'not placed':0}
    bad=~labels.isin(mapping)
    if bad.any(): raise ValueError(f'{int(bad.sum())} rows have unknown placed labels; review before training')
    df['placed']=labels.map(mapping).astype(int)
    for col in ['cgpa','backlogs','internships','projects','aptitude','communication','graduation_year']: df[col]=pd.to_numeric(df[col],errors='coerce')
    if df['student_id'].isna().any() or df['program'].isna().any(): raise ValueError('student_id and program cannot be missing')
    ranges={'cgpa':(0,10),'backlogs':(0,30),'internships':(0,20),'projects':(0,50),'aptitude':(0,100),'communication':(0,100),'graduation_year':(2020,2040)}
    for col,(lo,hi) in ranges.items():
        values=df[col].dropna()
        if ((values<lo)|(values>hi)).any(): raise ValueError(f'{col} outside permitted range {lo}–{hi}')
    return df,before-len(df)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',default='data/processed/training.csv');a=p.parse_args();out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);d,dupes=prepare(Path(a.input));d.to_csv(out,index=False);print(f'Wrote {len(d)} validated rows; removed {dupes} duplicate IDs; output {out}')
