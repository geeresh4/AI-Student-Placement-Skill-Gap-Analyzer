import json, csv, io
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from .db import Base, engine, get_db
from .models import User, StudentProfile, Job, Prediction, Progress, TrainingPlan, DataImport
from .schemas import Login, ProfileIn, StudentCreate, JobIn, ProgressIn, TrainingIn
from .auth import hash_password, verify_password, token, current_user, officer
from .config import CORS_ORIGINS
from .services import coverage,extract_skills,match_score,model_info,predict
app=FastAPI(title="Student Placement & Skill Gap API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=CORS_ORIGINS,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
Base.metadata.create_all(bind=engine)
def serialize(p): return {"student_id":p.student_id,"name":p.name,"program":p.program,"graduation_year":p.graduation_year,"cgpa":p.cgpa,"backlogs":p.backlogs,"internships":p.internships,"projects":p.projects,"aptitude":p.aptitude,"communication":p.communication,"skills":json.loads(p.skills_json),"projects_detail":json.loads(p.projects_detail_json or '[]'),"internships_detail":json.loads(p.internships_detail_json or '[]'),"certifications":json.loads(p.certifications_json or '[]'),"placed":p.placed,"source":p.source,"updated_at":p.updated_at.isoformat() if p.updated_at else None}
def own_profile(db,user):
    p=db.scalar(select(StudentProfile).where(StudentProfile.user_id==user.id))
    if not p: raise HTTPException(404,"Student profile not found")
    return p
@app.get('/api/health')
def health(): return {"status":"ok","model":model_info()['status']}
@app.post('/api/auth/login')
def login(body:Login,db:Session=Depends(get_db)):
    u=db.scalar(select(User).where(User.email==body.email.lower()))
    if not u or not verify_password(body.password,u.password_hash): raise HTTPException(401,"Incorrect email or password")
    return {"access_token":token(u),"token_type":"bearer","user":{"email":u.email,"role":u.role,"student_id":u.student_id}}
@app.get('/api/auth/me')
def me(u:User=Depends(current_user)): return {"email":u.email,"role":u.role,"student_id":u.student_id}
@app.get('/api/student/profile')
def profile(u:User=Depends(current_user),db:Session=Depends(get_db)): return serialize(own_profile(db,u))
@app.put('/api/student/profile')
def update_profile(body:ProfileIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
    p=own_profile(db,u); data=body.model_dump(); skills=data.pop('skills'); projects_detail=data.pop('projects_detail'); internships_detail=data.pop('internships_detail'); certifications=data.pop('certifications'); skills=[{'name':x,'level':2} if isinstance(x,str) else x for x in skills]; [setattr(p,k,v) for k,v in data.items()]; p.skills_json=json.dumps(skills); p.projects_detail_json=json.dumps(projects_detail); p.internships_detail_json=json.dumps(internships_detail); p.certifications_json=json.dumps(certifications); db.commit(); db.refresh(p); return serialize(p)
@app.post('/api/student/predict')
def student_predict(u:User=Depends(current_user),db:Session=Depends(get_db)):
    p=own_profile(db,u); info=model_info()
    if not info['available']: return {"available":False,"model":info}
    prob,outcome,explanation,version=predict({"cgpa":p.cgpa,"backlogs":p.backlogs,"internships":p.internships,"projects":p.projects,"aptitude":p.aptitude,"communication":p.communication,"program":p.program,"graduation_year":p.graduation_year})
    row=Prediction(student_id=p.student_id,probability=prob,outcome=outcome,model_version=version,explanation_json=json.dumps(explanation)); db.add(row); db.commit(); return {"available":True,"probability":prob,"outcome":outcome,"explanation":explanation,"model_version":version,"timestamp":row.created_at.isoformat(),"limitation":"Synthetic-demo model; estimate is not an employment guarantee."}
@app.get('/api/student/history')
def history(u:User=Depends(current_user),db:Session=Depends(get_db)):
    p=own_profile(db,u); preds=db.scalars(select(Prediction).where(Prediction.student_id==p.student_id).order_by(Prediction.created_at.desc()).limit(50)).all(); prog=db.scalars(select(Progress).where(Progress.student_id==p.student_id)).all(); return {"predictions":[{"probability":x.probability,"outcome":x.outcome,"model_version":x.model_version,"created_at":x.created_at.isoformat()} for x in preds],"recommendations":[{"title":x.title,"status":x.status} for x in prog]}
@app.get('/api/jobs')
def jobs(u:User=Depends(current_user),db:Session=Depends(get_db)): return [{"id":j.id,"company":j.company,"title":j.title,"description":j.description,"requirements":json.loads(j.requirements_json),"min_cgpa":j.min_cgpa,"status":j.status} for j in db.scalars(select(Job).where(Job.status=='published')).all()]
@app.get('/api/student/jobs/{job_id}/gaps')
def job_gaps(job_id:int,u:User=Depends(current_user),db:Session=Depends(get_db)):
    p=own_profile(db,u); j=db.get(Job,job_id)
    if not j: raise HTTPException(404,"Job not found")
    return {"job":{"id":j.id,"title":j.title,"company":j.company},**coverage(json.loads(p.skills_json),json.loads(j.requirements_json)),"note":"Skill coverage is not a hiring probability."}
@app.put('/api/student/recommendations')
def progress(body:ProgressIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
    p=own_profile(db,u); x=db.scalar(select(Progress).where(Progress.student_id==p.student_id,Progress.title==body.title))
    if not x: x=Progress(student_id=p.student_id,title=body.title); db.add(x)
    x.status=body.status; db.commit(); return {"title":x.title,"status":x.status}
@app.get('/api/officer/stats')
def stats(u:User=Depends(officer),db:Session=Depends(get_db)):
    ps=db.scalars(select(StudentProfile)).all(); known=[p for p in ps if p.placed is not None and 'synthetic' not in p.source.lower()]; skills={}; cohorts={}
    for p in ps:
        for s in json.loads(p.skills_json): skills[s['name']]=skills.get(s['name'],0)+1
    for p in ps:
        y=cohorts.setdefault(str(p.graduation_year),{"year":p.graduation_year,"students":0,"cgpa_sum":0.0,"known_outcomes":0,"placed":0})
        y['students']+=1; y['cgpa_sum']+=p.cgpa
        if p.placed is not None and 'synthetic' not in p.source.lower(): y['known_outcomes']+=1; y['placed']+=int(p.placed)
    cohort_rows=[{"year":v['year'],"students":v['students'],"average_cgpa":round(v['cgpa_sum']/v['students'],2) if v['students'] else None,"known_outcomes":v['known_outcomes'],"placed":v['placed'],"recorded_rate":v['placed']/v['known_outcomes'] if v['known_outcomes'] else None} for v in sorted(cohorts.values(),key=lambda x:x['year'])]
    bins=[{"range":label,"count":sum(lo<=p.cgpa<hi if hi<10 else lo<=p.cgpa<=hi for p in ps)} for label,lo,hi in [('0–4',0,4),('4–6',4,6),('6–8',6,8),('8–10',8,10)]]
    return {"students":len(ps),"complete_profiles":sum(bool(p.skills_json and p.cgpa is not None) for p in ps),"placed":sum(p.placed is True for p in known),"not_placed":sum(p.placed is False for p in known),"known_outcomes":len(known),"actual_placement_rate":sum(p.placed is True for p in known)/len(known) if known else None,"synthetic_outcomes_excluded":sum(p.placed is not None and 'synthetic' in p.source.lower() for p in ps),"outcome_sources":sorted({p.source for p in known}),"average_cgpa":sum(p.cgpa for p in ps)/len(ps) if ps else None,"cgpa_distribution":bins,"cohort_summary":cohort_rows,"top_skills":sorted([{"skill":k,"count":v} for k,v in skills.items()],key=lambda x:-x['count'])[:8],"jobs":len(db.scalars(select(Job)).all()),"model":model_info(),"synthetic_students":sum('synthetic' in p.source.lower() for p in ps)}
@app.get('/api/officer/students')
def students(search:str="",page:int=1,limit:int=50,program:str|None=None,year:int|None=None,u:User=Depends(officer),db:Session=Depends(get_db)):
    q=select(StudentProfile)
    if search: q=q.where((StudentProfile.student_id.contains(search))|(StudentProfile.name.contains(search)))
    if program: q=q.where(StudentProfile.program==program)
    if year: q=q.where(StudentProfile.graduation_year==year)
    rows=db.scalars(q.order_by(StudentProfile.student_id).offset((page-1)*min(limit,100)).limit(min(limit,100))).all(); return {"items":[serialize(p) for p in rows],"page":page,"limit":min(limit,100)}
@app.get('/api/officer/students/{sid}')
def student_detail(sid:str,u:User=Depends(officer),db:Session=Depends(get_db)):
    p=db.scalar(select(StudentProfile).where(StudentProfile.student_id==sid))
    if not p: raise HTTPException(404,"Student not found")
    return serialize(p)
@app.post('/api/officer/students',status_code=201)
def create_student(body:StudentCreate,u:User=Depends(officer),db:Session=Depends(get_db)):
    email=body.email.strip().lower(); sid=body.student_id.strip()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,"An account with this email already exists")
    if db.scalar(select(StudentProfile).where(StudentProfile.student_id==sid)): raise HTTPException(409,"A student with this identifier already exists")
    account=User(email=email,password_hash=hash_password(body.initial_password),role='student',student_id=sid)
    db.add(account); db.flush()
    profile=StudentProfile(student_id=sid,user_id=account.id,name=body.name.strip(),program=body.program.strip(),graduation_year=body.graduation_year,cgpa=body.cgpa,backlogs=0,internships=0,projects=0,aptitude=0,communication=0,skills_json=json.dumps([x.model_dump() for x in body.skills]),source='officer-entered')
    db.add(profile); db.commit(); db.refresh(profile)
    return {**serialize(profile),"email":account.email,"account_created":True}
@app.post('/api/officer/jobs')
def create_job(body:JobIn,u:User=Depends(officer),db:Session=Depends(get_db)):
    reqs=[x.model_dump() for x in body.requirements] or extract_skills(body.description); j=Job(company=body.company,title=body.title,description=body.description,requirements_json=json.dumps(reqs),min_cgpa=body.min_cgpa,status=body.status); db.add(j); db.commit(); db.refresh(j); return {"id":j.id,"company":j.company,"title":j.title,"requirements":reqs,"status":j.status}
@app.put('/api/officer/jobs/{job_id}')
def update_job(job_id:int,body:JobIn,u:User=Depends(officer),db:Session=Depends(get_db)):
    j=db.get(Job,job_id)
    if not j: raise HTTPException(404,"Job not found")
    j.company=body.company; j.title=body.title; j.description=body.description; j.requirements_json=json.dumps([x.model_dump() for x in body.requirements] or extract_skills(body.description)); j.min_cgpa=body.min_cgpa; j.status=body.status; db.commit()
    return {"id":j.id,"company":j.company,"title":j.title,"requirements":json.loads(j.requirements_json),"status":j.status}
@app.get('/api/officer/jobs')
def all_jobs(u:User=Depends(officer),db:Session=Depends(get_db)):
    return [{"id":j.id,"company":j.company,"title":j.title,"description":j.description,"requirements":json.loads(j.requirements_json),"min_cgpa":j.min_cgpa,"status":j.status} for j in db.scalars(select(Job)).all()]
@app.get('/api/officer/jobs/{job_id}/matches')
def matches(job_id:int,u:User=Depends(officer),db:Session=Depends(get_db)):
    j=db.get(Job,job_id)
    if not j: raise HTTPException(404,"Job not found")
    req=json.loads(j.requirements_json); ranked=[]
    for p in db.scalars(select(StudentProfile)).all():
        if p.cgpa>=j.min_cgpa: ranked.append({"student_id":p.student_id,"name":p.name,**match_score(p,req)})
    return {"job":j.title,"ranking_basis":"80% skill coverage + 20% eligibility; not a selection probability","candidates":sorted(ranked,key=lambda x:-x['score'])}
@app.post('/api/officer/training-plans')
def create_plan(body:TrainingIn,u:User=Depends(officer),db:Session=Depends(get_db)):
    x=TrainingPlan(**body.model_dump()); db.add(x); db.commit(); db.refresh(x); return {"id":x.id,**body.model_dump()}
@app.get('/api/officer/training-plans')
def plans(u:User=Depends(officer),db:Session=Depends(get_db)): return [{"id":x.id,"skill":x.skill,"cohort":x.cohort,"priority":x.priority,"owner":x.owner,"status":x.status} for x in db.scalars(select(TrainingPlan)).all()]
@app.get('/api/officer/model-info')
def model_endpoint(u:User=Depends(officer)): return model_info()
@app.get('/api/officer/export/{kind}')
def export(kind:str,u:User=Depends(officer),db:Session=Depends(get_db)):
    if kind not in {"students","outcomes","gaps","model"}: raise HTTPException(404,"Unknown export")
    out=io.StringIO(); w=csv.writer(out)
    if kind in ('students','outcomes'):
        w.writerow(["student_id","program","graduation_year","cgpa","backlogs","internships","projects","placed","source"])
        for p in db.scalars(select(StudentProfile)).all():
            if kind=='students' or p.placed is not None: w.writerow([p.student_id,p.program,p.graduation_year,p.cgpa,p.backlogs,p.internships,p.projects,p.placed,p.source])
    elif kind=='gaps':
        w.writerow(["student_id","skill","proficiency"])
        for p in db.scalars(select(StudentProfile)).all():
            for s in json.loads(p.skills_json): w.writerow([p.student_id,s.get('name'),s.get('level')])
    else:
        info=model_info(); w.writerow(["available","status","version","sample_count","metrics"]); w.writerow([info.get('available'),info.get('status'),info.get('version'),info.get('sample_count'),json.dumps(info.get('metrics'))])
    return StreamingResponse(iter([out.getvalue()]),media_type='text/csv',headers={"Content-Disposition":f"attachment; filename={kind}.csv"})
@app.post('/api/officer/import/preview')
async def preview(file:UploadFile=File(...),u:User=Depends(officer)):
    if not file.filename.lower().endswith('.csv'): raise HTTPException(400,"CSV files only")
    content=await file.read(10_000_001)
    if len(content)>10_000_000: raise HTTPException(413,"File exceeds 10 MB")
    try:
        import pandas as pd
        df=pd.read_csv(io.BytesIO(content)); return {"filename":file.filename,"columns":list(df.columns),"sample":df.head(5).fillna('').to_dict('records'),"rows":len(df),"missing":df.isna().sum().to_dict(),"duplicates":int(df.duplicated().sum()),"suggested_mapping":{x:x for x in ['student_id','program','graduation_year','cgpa','backlogs','internships','projects','aptitude','communication','placed'] if x in df.columns},"message":"Preview only. Review source-to-target mappings and explicitly confirm."}
    except Exception as e: raise HTTPException(400,f"Invalid CSV: {e}")
@app.post('/api/officer/import/confirm')
async def confirm_import(file:UploadFile=File(...),mapping:str=Form(...),source:str=Form('manual upload'),u:User=Depends(officer),db:Session=Depends(get_db)):
    if not file.filename.lower().endswith('.csv'): raise HTTPException(400,"CSV files only")
    content=await file.read(10_000_001)
    if len(content)>10_000_000: raise HTTPException(413,"File exceeds 10 MB")
    try:
        import pandas as pd
        mapping_obj=json.loads(mapping); df=pd.read_csv(io.BytesIO(content))
    except Exception as e: raise HTTPException(400,f"Invalid CSV or mapping: {e}")
    required={'student_id','program','graduation_year','cgpa','backlogs','internships','projects','aptitude','communication','placed'}
    if not required.issubset(mapping_obj): raise HTTPException(422,"Map all required fields: "+', '.join(sorted(required)))
    if any(col not in df.columns for col in mapping_obj.values()): raise HTTPException(422,"Mapping references a missing CSV column")
    inserted=0; rejected=[]; seen=set()
    for idx,row in df.iterrows():
        try:
            d={key:row[col] for key,col in mapping_obj.items()}; sid=str(d['student_id']).strip()
            if any(pd.isna(value) for value in d.values()): raise ValueError('missing required value')
            if not sid or sid.lower()=='nan' or sid in seen or db.scalar(select(StudentProfile).where(StudentProfile.student_id==sid)): raise ValueError('missing or duplicate student_id')
            placed_value=d['placed']
            if isinstance(placed_value,str):
                normalized=placed_value.strip().lower()
                if normalized not in {'0','1','true','false','yes','no','placed','not placed'}: raise ValueError('unrecognized placed label')
                placed_value=normalized in {'1','true','yes','placed'}
            elif placed_value not in (0,1,False,True): raise ValueError('placed label must be binary')
            p=StudentProfile(student_id=sid,name=sid,program=str(d['program']),graduation_year=int(d['graduation_year']),cgpa=float(d['cgpa']),backlogs=int(d['backlogs']),internships=int(d['internships']),projects=int(d['projects']),aptitude=float(d['aptitude']),communication=float(d['communication']),placed=bool(placed_value),source='imported:'+source[:20],skills_json='[]')
            if not 0<=p.cgpa<=10 or not 0<=p.aptitude<=100 or not 0<=p.communication<=100: raise ValueError('value outside permitted range')
            db.add(p); seen.add(sid); inserted+=1
        except Exception as e: rejected.append({'row':int(idx)+2,'reason':str(e)[:160]})
    item=DataImport(filename=file.filename[:255],source=source[:120],rows_imported=inserted); db.add(item)
    try: db.commit()
    except Exception:
        db.rollback(); raise HTTPException(400,"Import transaction failed; no rows were imported")
    return {"import_id":item.id,"rows_imported":inserted,"rows_rejected":len(rejected),"rejections":rejected[:100],"source":source,"note":"Imported outcome labels are recorded as supplied, not independently verified."}
