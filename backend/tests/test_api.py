from fastapi.testclient import TestClient
from sqlalchemy import select
from backend.app.main import app
from backend.app.db import SessionLocal
from backend.app.models import User,StudentProfile
from backend.app.auth import hash_password

def setup_users():
    db=SessionLocal()
    if not db.scalar(select(User).where(User.email=='test-student@demo.local')):
        # Construct fields explicitly so the test fixture mirrors real account storage.
        u=User(email='test-student@demo.local',password_hash=hash_password('StudentTest!123'),role='student',student_id='TEST-STU')
        db.add(u); db.flush(); db.add(StudentProfile(student_id='TEST-STU',user_id=u.id,name='Test Student',program='CS',graduation_year=2027,cgpa=8,skills_json='[]'))
        db.add(User(email='test-officer@demo.local',password_hash=hash_password('OfficerTest!123'),role='officer'))
        db.commit()
    db.close()

def test_health(): assert TestClient(app).get('/api/health').status_code==200
def test_requires_login(): assert TestClient(app).get('/api/student/profile').status_code==401
def test_login_and_role_isolation():
    setup_users(); c=TestClient(app); r=c.post('/api/auth/login',json={'email':'test-student@demo.local','password':'StudentTest!123'}); assert r.status_code==200
    c.headers['Authorization']='Bearer '+r.json()['access_token']; assert c.get('/api/student/profile').json()['student_id']=='TEST-STU'
    assert c.get('/api/officer/stats').status_code==403
    assert c.get('/api/officer/students/ANOTHER-ID').status_code==403
def test_invalid_password():
    setup_users(); assert TestClient(app).post('/api/auth/login',json={'email':'test-student@demo.local','password':'wrong'}).status_code==401
def test_csv_preview_and_confirm():
    setup_users(); c=TestClient(app); auth=c.post('/api/auth/login',json={'email':'test-officer@demo.local','password':'OfficerTest!123'}).json(); c.headers['Authorization']='Bearer '+auth['access_token']
    headers=['student_id','program','graduation_year','cgpa','backlogs','internships','projects','aptitude','communication','placed']
    row=['CSV-TEST','CS','2027','7.5','0','1','2','60','70','1']; csv=','.join(headers)+'\n'+','.join(row)+'\n'
    preview=c.post('/api/officer/import/preview',files={'file':('sample.csv',csv,'text/csv')}); assert preview.status_code==200 and preview.json()['rows']==1
    mapping={k:k for k in headers}; result=c.post('/api/officer/import/confirm',data={'mapping':__import__('json').dumps(mapping),'source':'test'},files={'file':('sample.csv',csv,'text/csv')}); assert result.status_code==200 and result.json()['rows_imported']==1
def test_prediction_is_model_backed_or_explicitly_unavailable():
    setup_users(); c=TestClient(app); auth=c.post('/api/auth/login',json={'email':'test-student@demo.local','password':'StudentTest!123'}).json(); c.headers['Authorization']='Bearer '+auth['access_token']; result=c.post('/api/student/predict'); assert result.status_code==200
    data=result.json()
    if data['available']:
        assert 0<=data['probability']<=1 and data['model_version'] and c.get('/api/student/history').json()['predictions']
    else: assert data['model']['status']=='unavailable'
def test_profile_update_persists_skills_and_portfolio_items():
    setup_users(); c=TestClient(app); auth=c.post('/api/auth/login',json={'email':'test-student@demo.local','password':'StudentTest!123'}).json(); c.headers['Authorization']='Bearer '+auth['access_token']
    payload={'name':'Updated Student','program':'CS','graduation_year':2027,'cgpa':8.4,'backlogs':0,'internships':1,'projects':2,'aptitude':75,'communication':70,'skills':[{'name':'sql','level':3}],'projects_detail':['Capstone dashboard'],'internships_detail':['Data internship'],'certifications':['SQL basics']}
    saved=c.put('/api/student/profile',json=payload); assert saved.status_code==200; profile=c.get('/api/student/profile').json(); assert profile['skills']==payload['skills'] and profile['certifications']==payload['certifications']

def test_officer_can_create_student_login_and_profile():
    setup_users(); c=TestClient(app); auth=c.post('/api/auth/login',json={'email':'test-officer@demo.local','password':'OfficerTest!123'}).json(); c.headers['Authorization']='Bearer '+auth['access_token']
    payload={'student_id':'ADDED-TEST-01','name':'Added Test Student','email':'added-test@example.local','initial_password':'NewStudent!2026','program':'Computer Science','graduation_year':2028,'cgpa':8.1,'skills':[{'name':'python','level':2}]}
    created=c.post('/api/officer/students',json=payload); assert created.status_code==201; assert created.json()['student_id']=='ADDED-TEST-01'; assert 'initial_password' not in created.json()
    assert c.post('/api/officer/students',json=payload).status_code==409
    login=c.post('/api/auth/login',json={'email':payload['email'],'password':payload['initial_password']}); assert login.status_code==200
    c.headers['Authorization']='Bearer '+login.json()['access_token']; assert c.get('/api/student/profile').json()['student_id']=='ADDED-TEST-01'
