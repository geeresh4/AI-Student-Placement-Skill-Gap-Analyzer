from pydantic import BaseModel, Field
class Login(BaseModel): email:str; password:str
class SkillIn(BaseModel): name:str=Field(min_length=1,max_length=80); level:int=Field(ge=0,le=5)
class JobSkillIn(BaseModel): skill:str=Field(min_length=1,max_length=80); level:int=Field(default=2,ge=1,le=5)
class ProfileIn(BaseModel):
    name:str=Field(min_length=1,max_length=120); program:str=Field(min_length=1,max_length=120); graduation_year:int=Field(ge=2020,le=2040); cgpa:float=Field(ge=0,le=10); backlogs:int=Field(ge=0,le=30); internships:int=Field(ge=0,le=20); projects:int=Field(ge=0,le=50); aptitude:float=Field(ge=0,le=100); communication:float=Field(ge=0,le=100); skills:list[SkillIn|str]=[]; projects_detail:list[str]=[]; internships_detail:list[str]=[]; certifications:list[str]=[]
class StudentCreate(BaseModel):
    student_id:str=Field(min_length=2,max_length=50,pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
    name:str=Field(min_length=1,max_length=120)
    email:str=Field(min_length=6,max_length=255,pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    initial_password:str=Field(min_length=12,max_length=128)
    program:str=Field(min_length=1,max_length=120)
    graduation_year:int=Field(ge=2020,le=2040)
    cgpa:float=Field(ge=0,le=10)
    skills:list[SkillIn]=Field(default_factory=list)
class JobIn(BaseModel): company:str=Field(min_length=1,max_length=150); title:str=Field(min_length=1,max_length=150); description:str=""; requirements:list[JobSkillIn]=Field(default_factory=list); min_cgpa:float=Field(0,ge=0,le=10); status:str=Field(default="published",pattern="^(draft|published|archived)$")
class ProgressIn(BaseModel): title:str; status:str=Field(pattern="^(not_started|in_progress|completed)$")
class TrainingIn(BaseModel): skill:str; cohort:str; priority:str="medium"; owner:str=""; status:str="planned"
