from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.presentation.routers import students, teachers, classes, subjects, enrollments, grades, attendance
from app.infrastructure.database.connection import engine
from app.infrastructure.database import models

# Create all tables on startup (idempotent)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="School Management System API",
    description="REST API for managing students, teachers, classes, subjects, grades, and attendance.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router, prefix="/api/v1")
app.include_router(teachers.router, prefix="/api/v1")
app.include_router(classes.router, prefix="/api/v1")
app.include_router(subjects.router, prefix="/api/v1")
app.include_router(enrollments.router, prefix="/api/v1")
app.include_router(grades.router, prefix="/api/v1")
app.include_router(attendance.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "service": "School Management System API"}


@app.get("/api/v1/dashboard/stats")
def dashboard_stats(db=None):
    from app.infrastructure.database.connection import SessionLocal
    from app.infrastructure.database.models import StudentModel, TeacherModel, ClassModel, SubjectModel
    session = SessionLocal()
    try:
        return {
            "total_students": session.query(StudentModel).count(),
            "total_teachers": session.query(TeacherModel).count(),
            "total_classes": session.query(ClassModel).count(),
            "total_subjects": session.query(SubjectModel).count(),
        }
    finally:
        session.close()
