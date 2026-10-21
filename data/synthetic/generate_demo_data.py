import argparse
from pathlib import Path
import numpy as np,pandas as pd
def generate(n=20000,seed=42):
    r=np.random.default_rng(seed); cgpa=np.clip(r.normal(7.1,1.15,n),0,10); backlog=r.poisson(.55,n).clip(0,8); intern=r.binomial(2,.35,n); projects=r.integers(0,6,n); aptitude=np.clip(r.normal(62,17,n),0,100); comm=np.clip(r.normal(64,16,n),0,100)
    logits=-4.2+.42*cgpa-.38*backlog+.5*intern+.12*projects+.018*aptitude+.012*comm; prob=1/(1+np.exp(-logits)); placed=r.binomial(1,prob)
    df=pd.DataFrame({'student_id':[f'SYN{i:05d}' for i in range(n)],'program':r.choice(['Computer Science','Data Science','Information Technology','Electronics'],n),'graduation_year':r.choice([2025,2026,2027,2028],n),'cgpa':cgpa.round(2),'backlogs':backlog,'internships':intern,'projects':projects,'aptitude':aptitude.round(1),'communication':comm.round(1),'placed':placed,'source':'synthetic-demo'})
    for col in ['aptitude','communication','cgpa']: df.loc[r.random(n)<.025,col]=np.nan
    return df
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--rows',type=int,default=20000); p.add_argument('--seed',type=int,default=42); p.add_argument('--output',default='data/synthetic/students.csv'); a=p.parse_args(); out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); d=generate(a.rows,a.seed); d.to_csv(out,index=False); print(f'Wrote {len(d)} synthetic rows to {out}; never real placement evidence.')
