import sys,pandas as pd
p=pd.read_csv(sys.argv[1]); print('rows:',len(p)); print('columns:',list(p.columns)); print('missing:',p.isna().sum().to_dict()); print('duplicates:',int(p.duplicated().sum())); print('label_counts:',p['placed'].value_counts(dropna=False).to_dict() if 'placed' in p else 'target absent')
