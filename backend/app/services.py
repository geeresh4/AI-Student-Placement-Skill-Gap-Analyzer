import json, re
from .config import MODEL_PATH
SKILLS={"python","sql","machine learning","data analysis","excel","react","javascript","typescript","fastapi","communication","problem solving","statistics","java","git","rest api","cloud"}
def coverage(student_skills, requirements):
    mine={str(x.get('name','')).lower():int(x.get('level',0)) for x in student_skills}; rows=[]; earned=0
    for req in requirements:
        name=str(req.get('skill','')).lower(); need=int(req.get('level',2)); have=mine.get(name,0); earned+=min(have,need)/max(need,1); rows.append({"skill":name,"required":need,"current":have,"status":"match" if have>=need else "partial" if have else "missing"})
    return {"score":round(earned/len(rows)*100,1) if rows else 0,"skills":rows,"gaps":[x for x in rows if x['status']!='match']}
def extract_skills(description):
    d=description.lower(); return [{"skill":s,"level":2} for s in sorted(SKILLS) if re.search(r'\b'+re.escape(s)+r'\b',d)]
def match_score(profile,reqs):
    result=coverage(json.loads(profile.skills_json),reqs)
    return {"score":result['score']*.8+(20 if profile.cgpa>=0 else 0),"coverage":result['score'],"gaps":result['gaps'],"eligible":True}
def model_info():
    if not MODEL_PATH.exists(): return {"available":False,"status":"unavailable","message":"Model is not trained. Run scripts/train_model.py.","version":None,"metrics":{}}
    try:
        import joblib; obj=joblib.load(MODEL_PATH); return {"available":True,"status":"synthetic-demo","version":obj['version'],"metrics":obj['metrics'],"sample_count":obj['sample_count'],"source":obj['source'],"limitations":"Synthetic demo data only; metrics do not establish real-world performance."}
    except Exception as e: return {"available":False,"status":"error","message":str(e),"metrics":{}}
def predict(features):
    import joblib, pandas as pd
    obj=joblib.load(MODEL_PATH); model=obj['pipeline']; prob=float(model.predict_proba(pd.DataFrame([features]))[0][1]); outcome="higher_estimated_readiness" if prob>=.5 else "lower_estimated_readiness"; base=model.calibrated_classifiers_[0].estimator; prep=base.named_steps['prep']; clf=base.named_steps['model']; names=list(prep.get_feature_names_out()); imp=getattr(clf,'feature_importances_',None)
    if imp is None: imp=getattr(clf,'coef_',[[0]])[0]
    explanation=sorted([{"feature":n.replace('n__','').replace('c__',''),"importance":round(float(v),4)} for n,v in zip(names,imp)],key=lambda x:abs(x['importance']),reverse=True)[:5]
    return prob,outcome,explanation,obj['version']
