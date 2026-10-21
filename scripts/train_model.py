import argparse,json
from pathlib import Path
import pandas as pd,joblib
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,average_precision_score,confusion_matrix,brier_score_loss
from sklearn.base import clone
FEATURES=['cgpa','backlogs','internships','projects','aptitude','communication','program','graduation_year']
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',default='data/synthetic/students.csv'); ap.add_argument('--output',default='models/placement_model.joblib'); a=ap.parse_args(); df=pd.read_csv(a.input)
    if 'placed' not in df or len(df)<100: raise SystemExit('Need at least 100 records and a placed target')
    df=df.dropna(subset=['placed']); y=df.placed.astype(int)
    if y.nunique()!=2: raise SystemExit('Training target must contain both placement classes')
    X=df[FEATURES]; num=FEATURES[:6]+['graduation_year']; cat=['program']; prep=ColumnTransformer([('n',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num),('c',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('encode',OneHotEncoder(handle_unknown='ignore'))]),cat)]); xtr,xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y); candidates={'logistic':LogisticRegression(max_iter=1000),'random_forest':RandomForestClassifier(n_estimators=180,min_samples_leaf=3,random_state=42,class_weight='balanced')}
    try:
        from xgboost import XGBClassifier
        candidates['xgboost']=XGBClassifier(n_estimators=180,max_depth=4,learning_rate=.06,subsample=.85,colsample_bytree=.85,eval_metric='logloss',random_state=42,n_jobs=-1)
    except ImportError: pass
    scores={k:cross_val_score(Pipeline([('prep',clone(prep)),('model',clone(m))]),xtr,ytr,cv=5,scoring='f1').mean() for k,m in candidates.items()}; best=max(scores,key=scores.get); base=Pipeline([('prep',prep),('model',candidates[best])]); pipeline=CalibratedClassifierCV(estimator=base,method='sigmoid',cv=5).fit(xtr,ytr); pred=pipeline.predict(xte); prob=pipeline.predict_proba(xte)[:,1]
    metrics={'accuracy':accuracy_score(yte,pred),'precision':precision_score(yte,pred,zero_division=0),'recall':recall_score(yte,pred,zero_division=0),'f1':f1_score(yte,pred,zero_division=0),'roc_auc':roc_auc_score(yte,prob) if yte.nunique()==2 else None,'average_precision':average_precision_score(yte,prob),'brier_score':brier_score_loss(yte,prob),'confusion_matrix':confusion_matrix(yte,pred).tolist(),'train_cv_f1':scores,'test_rows':len(yte),'class_distribution':y.value_counts().to_dict()}; out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); joblib.dump({'pipeline':pipeline,'version':'demo-1.0','metrics':metrics,'sample_count':len(df),'source':str(df.get('source',pd.Series(['unspecified'])).iloc[0]),'features':FEATURES,'label':'placed'},out); print(json.dumps(metrics,indent=2)); print('Saved',out)
if __name__=='__main__': main()
