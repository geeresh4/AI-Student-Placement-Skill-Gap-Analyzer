from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base
def now(): return datetime.now(timezone.utc)
class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True)
    email: Mapped[str]=mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    role: Mapped[str]=mapped_column(String(20), index=True)
    student_id: Mapped[str|None]=mapped_column(String(50), unique=True, nullable=True)
class StudentProfile(Base):
    __tablename__="student_profiles"
    id: Mapped[int]=mapped_column(primary_key=True)
    student_id: Mapped[str]=mapped_column(String(50), unique=True, index=True)
    user_id: Mapped[int|None]=mapped_column(ForeignKey("users.id"), nullable=True, unique=True)
    name: Mapped[str]=mapped_column(String(120), default="Student")
    program: Mapped[str]=mapped_column(String(120), default="Computer Science")
    graduation_year: Mapped[int]=mapped_column(Integer, default=2027)
    cgpa: Mapped[float]=mapped_column(Float, default=7.5)
    backlogs: Mapped[int]=mapped_column(Integer, default=0)
    internships: Mapped[int]=mapped_column(Integer, default=0)
    projects: Mapped[int]=mapped_column(Integer, default=1)
    aptitude: Mapped[float]=mapped_column(Float, default=60)
    communication: Mapped[float]=mapped_column(Float, default=60)
    skills_json: Mapped[str]=mapped_column(Text, default="[]")
    projects_detail_json: Mapped[str]=mapped_column(Text, default="[]")
    internships_detail_json: Mapped[str]=mapped_column(Text, default="[]")
    certifications_json: Mapped[str]=mapped_column(Text, default="[]")
    placed: Mapped[bool|None]=mapped_column(Boolean, nullable=True)
    source: Mapped[str]=mapped_column(String(30), default="demo-seed")
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, onupdate=now)
class Job(Base):
    __tablename__="jobs"
    id: Mapped[int]=mapped_column(primary_key=True)
    company: Mapped[str]=mapped_column(String(150))
    title: Mapped[str]=mapped_column(String(150))
    description: Mapped[str]=mapped_column(Text, default="")
    requirements_json: Mapped[str]=mapped_column(Text, default="[]")
    min_cgpa: Mapped[float]=mapped_column(Float, default=0)
    status: Mapped[str]=mapped_column(String(20), default="published")
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
class Prediction(Base):
    __tablename__="predictions"
    id: Mapped[int]=mapped_column(primary_key=True)
    student_id: Mapped[str]=mapped_column(ForeignKey("student_profiles.student_id"), index=True)
    probability: Mapped[float]=mapped_column(Float)
    outcome: Mapped[str]=mapped_column(String(30))
    model_version: Mapped[str]=mapped_column(String(80))
    explanation_json: Mapped[str]=mapped_column(Text, default="[]")
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
class Progress(Base):
    __tablename__="recommendation_progress"
    id: Mapped[int]=mapped_column(primary_key=True)
    student_id: Mapped[str]=mapped_column(ForeignKey("student_profiles.student_id"), index=True)
    title: Mapped[str]=mapped_column(String(200))
    status: Mapped[str]=mapped_column(String(20), default="not_started")
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, onupdate=now)
class TrainingPlan(Base):
    __tablename__="training_plans"
    id: Mapped[int]=mapped_column(primary_key=True)
    skill: Mapped[str]=mapped_column(String(100))
    cohort: Mapped[str]=mapped_column(String(120))
    priority: Mapped[str]=mapped_column(String(20), default="medium")
    owner: Mapped[str]=mapped_column(String(120), default="")
    status: Mapped[str]=mapped_column(String(30), default="planned")
class DataImport(Base):
    __tablename__="data_imports"
    id: Mapped[int]=mapped_column(primary_key=True)
    filename: Mapped[str]=mapped_column(String(255))
    source: Mapped[str]=mapped_column(String(120), default="manual upload")
    rows_imported: Mapped[int]=mapped_column(Integer, default=0)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
