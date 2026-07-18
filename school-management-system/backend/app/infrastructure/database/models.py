from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Float,
    ForeignKey, UniqueConstraint, CheckConstraint, Numeric,
)
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base


class TeacherModel(Base):
    __tablename__ = "Teachers"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    first_name     = Column(String(100), nullable=False)
    last_name      = Column(String(100), nullable=False)
    email          = Column(String(255), nullable=False, unique=True)
    phone          = Column(String(30))
    specialization = Column(String(150))
    created_at     = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at     = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    classes  = relationship("ClassModel", back_populates="teacher", foreign_keys="ClassModel.teacher_id")
    subjects = relationship("SubjectModel", back_populates="teacher")


class ClassModel(Base):
    __tablename__ = "Classes"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String(100), nullable=False)
    grade_level   = Column(Integer, nullable=False)
    section       = Column(String(10), nullable=False, default="A")
    teacher_id    = Column(Integer, ForeignKey("Teachers.id", ondelete="SET NULL"), nullable=True)
    academic_year = Column(String(20), nullable=False)
    created_at    = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at    = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    teacher     = relationship("TeacherModel", back_populates="classes", foreign_keys=[teacher_id])
    subjects    = relationship("SubjectModel", back_populates="school_class", cascade="all, delete-orphan")
    enrollments = relationship("EnrollmentModel", back_populates="school_class", cascade="all, delete-orphan")
    attendances = relationship("AttendanceModel", back_populates="school_class")


class StudentModel(Base):
    __tablename__ = "Students"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    first_name    = Column(String(100), nullable=False)
    last_name     = Column(String(100), nullable=False)
    date_of_birth = Column(Date)
    gender        = Column(String(10))
    email         = Column(String(255))
    phone         = Column(String(30))
    address       = Column(String(500))
    created_at    = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at    = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    enrollments = relationship("EnrollmentModel", back_populates="student", cascade="all, delete-orphan")
    grades      = relationship("GradeModel", back_populates="student", cascade="all, delete-orphan")
    attendances = relationship("AttendanceModel", back_populates="student", cascade="all, delete-orphan")


class SubjectModel(Base):
    __tablename__ = "Subjects"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(150), nullable=False)
    code       = Column(String(20), nullable=False, unique=True)
    class_id   = Column(Integer, ForeignKey("Classes.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("Teachers.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    school_class = relationship("ClassModel", back_populates="subjects")
    teacher      = relationship("TeacherModel", back_populates="subjects")
    grades       = relationship("GradeModel", back_populates="subject")


class EnrollmentModel(Base):
    __tablename__ = "Enrollments"
    __table_args__ = (UniqueConstraint("student_id", "class_id", name="UQ_Enrollments"),)

    id          = Column(Integer, primary_key=True, autoincrement=True)
    student_id  = Column(Integer, ForeignKey("Students.id", ondelete="CASCADE"), nullable=False)
    class_id    = Column(Integer, ForeignKey("Classes.id", ondelete="CASCADE"), nullable=False)
    enrolled_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    student      = relationship("StudentModel", back_populates="enrollments")
    school_class = relationship("ClassModel", back_populates="enrollments")


class GradeModel(Base):
    __tablename__ = "Grades"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    student_id     = Column(Integer, ForeignKey("Students.id", ondelete="CASCADE"), nullable=False)
    subject_id     = Column(Integer, ForeignKey("Subjects.id"), nullable=False)
    marks_obtained = Column(Numeric(6, 2), nullable=False)
    max_marks      = Column(Numeric(6, 2), nullable=False, default=100)
    exam_type      = Column(String(50), nullable=False, default="Final")
    exam_date      = Column(Date, nullable=False)
    created_at     = Column(DateTime, nullable=False, default=datetime.utcnow)

    student = relationship("StudentModel", back_populates="grades")
    subject = relationship("SubjectModel", back_populates="grades")


class AttendanceModel(Base):
    __tablename__ = "Attendance"
    __table_args__ = (UniqueConstraint("student_id", "class_id", "date", name="UQ_Attendance"),)

    id         = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("Students.id", ondelete="CASCADE"), nullable=False)
    class_id   = Column(Integer, ForeignKey("Classes.id"), nullable=False)
    date       = Column(Date, nullable=False)
    status     = Column(String(10), nullable=False, default="Present")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    student      = relationship("StudentModel", back_populates="attendances")
    school_class = relationship("ClassModel", back_populates="attendances")
