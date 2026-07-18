# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- School Management System full-stack application
- Python FastAPI backend following clean architecture (Domain / Application / Infrastructure / Presentation layers)
- SQL Server database schema with tables: Students, Teachers, Classes, Subjects, Enrollments, Grades, Attendance
- SQLAlchemy 2.0 ORM models and repository pattern implementations
- REST API endpoints for all entities at /api/v1/
- Dashboard stats endpoint returning aggregate counts
- React 18 + Vite frontend with Bootstrap 5 UI
- Pages: Dashboard, Students, Teachers, Classes, Subjects, Enrollments, Grades, Attendance
- Sidebar navigation and modal-based CRUD forms
- Axios service layer for all API communication
- CORS middleware configured for frontend-backend integration
- Database seed data with sample teachers, classes, students, subjects, and enrollments
- README with setup instructions for backend, frontend, and database
