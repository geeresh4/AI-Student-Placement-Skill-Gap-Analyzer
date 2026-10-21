import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sqlalchemy import select
from backend.app.db import Base,engine,SessionLocal
from backend.app.models import User,StudentProfile,Job
from backend.app.auth import hash_password
Base.metadata.create_all(engine); db=SessionLocal()
def user(email,pw,role,sid=None):
    x=db.scalar(select(User).where(User.email==email))
    if not x: db.add(User(email=email,password_hash=hash_password(pw),role=role,student_id=sid)); db.flush()
    return db.scalar(select(User).where(User.email==email))
stu=user('student@demo.local','StudentDemo!2026','student','STU-001'); user('officer@demo.local','OfficerDemo!2026','officer')
if not db.scalar(select(StudentProfile).where(StudentProfile.student_id=='STU-001')): db.add(StudentProfile(student_id='STU-001',user_id=stu.id,name='Aarav Sharma',program='Computer Science',graduation_year=2027,cgpa=8.2,backlogs=0,internships=1,projects=3,aptitude=76,communication=72,skills_json=json.dumps([{'name':'python','level':2},{'name':'sql','level':1},{'name':'react','level':2},{'name':'git','level':2}]),source='demo-seed'))
if not db.scalar(select(Job)):
    db.add_all([Job(company='Northstar Analytics',title='Junior Data Analyst',description='SQL and Python analytics',requirements_json=json.dumps([{'skill':'sql','level':2},{'skill':'python','level':2},{'skill':'statistics','level':2}]),min_cgpa=6.5),Job(company='BrightStack',title='Frontend Engineer',description='React and JavaScript',requirements_json=json.dumps([{'skill':'react','level':2},{'skill':'javascript','level':2},{'skill':'git','level':1}]),min_cgpa=6)])
db.commit(); db.close(); print('Seed complete')
