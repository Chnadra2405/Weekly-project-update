-- =============================================================
-- School Management System - SQL Server Database Schema
-- Database: SchoolDB
-- =============================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'SchoolDB')
BEGIN
    CREATE DATABASE SchoolDB;
END
GO

USE SchoolDB;
GO

-- =============================================================
-- TABLE: Teachers
-- =============================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.Teachers') AND type = 'U')
BEGIN
    CREATE TABLE dbo.Teachers (
        id          INT IDENTITY(1,1)   NOT NULL,
        first_name  NVARCHAR(100)       NOT NULL,
        last_name   NVARCHAR(100)       NOT NULL,
        email       NVARCHAR(255)       NOT NULL,
        phone       NVARCHAR(30)        NULL,
        specialization NVARCHAR(150)   NULL,
        created_at  DATETIME2           NOT NULL DEFAULT GETUTCDATE(),
        updated_at  DATETIME2           NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT PK_Teachers PRIMARY KEY CLUSTERED (id),
        CONSTRAINT UQ_Teachers_Email UNIQUE (email)
    );
END
GO

-- =============================================================
-- TABLE: Classes
-- =============================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.Classes') AND type = 'U')
BEGIN
    CREATE TABLE dbo.Classes (
        id              INT IDENTITY(1,1)   NOT NULL,
        name            NVARCHAR(100)       NOT NULL,
        grade_level     INT                 NOT NULL,
        section         NVARCHAR(10)        NOT NULL DEFAULT 'A',
        teacher_id      INT                 NULL,
        academic_year   NVARCHAR(20)        NOT NULL,
        created_at      DATETIME2           NOT NULL DEFAULT GETUTCDATE(),
        updated_at      DATETIME2           NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT PK_Classes PRIMARY KEY CLUSTERED (id),
        CONSTRAINT FK_Classes_Teacher FOREIGN KEY (teacher_id)
            REFERENCES dbo.Teachers (id) ON DELETE SET NULL
    );
END
GO

-- =============================================================
-- TABLE: Students
-- =============================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.Students') AND type = 'U')
BEGIN
    CREATE TABLE dbo.Students (
        id              INT IDENTITY(1,1)   NOT NULL,
        first_name      NVARCHAR(100)       NOT NULL,
        last_name       NVARCHAR(100)       NOT NULL,
        date_of_birth   DATE                NULL,
        gender          NVARCHAR(10)        NULL CHECK (gender IN ('Male', 'Female', 'Other')),
        email           NVARCHAR(255)       NULL,
        phone           NVARCHAR(30)        NULL,
        address         NVARCHAR(500)       NULL,
        created_at      DATETIME2           NOT NULL DEFAULT GETUTCDATE(),
        updated_at      DATETIME2           NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT PK_Students PRIMARY KEY CLUSTERED (id)
    );
END
GO

-- =============================================================
-- TABLE: Subjects
-- =============================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.Subjects') AND type = 'U')
BEGIN
    CREATE TABLE dbo.Subjects (
        id          INT IDENTITY(1,1)   NOT NULL,
        name        NVARCHAR(150)       NOT NULL,
        code        NVARCHAR(20)        NOT NULL,
        class_id    INT                 NOT NULL,
        teacher_id  INT                 NULL,
        created_at  DATETIME2           NOT NULL DEFAULT GETUTCDATE(),
        updated_at  DATETIME2           NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT PK_Subjects PRIMARY KEY CLUSTERED (id),
        CONSTRAINT UQ_Subjects_Code UNIQUE (code),
        CONSTRAINT FK_Subjects_Class FOREIGN KEY (class_id)
            REFERENCES dbo.Classes (id) ON DELETE CASCADE,
        CONSTRAINT FK_Subjects_Teacher FOREIGN KEY (teacher_id)
            REFERENCES dbo.Teachers (id) ON DELETE SET NULL
    );
END
GO

-- =============================================================
-- TABLE: Enrollments (Student <-> Class)
-- =============================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.Enrollments') AND type = 'U')
BEGIN
    CREATE TABLE dbo.Enrollments (
        id          INT IDENTITY(1,1)   NOT NULL,
        student_id  INT                 NOT NULL,
        class_id    INT                 NOT NULL,
        enrolled_at DATETIME2           NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT PK_Enrollments PRIMARY KEY CLUSTERED (id),
        CONSTRAINT UQ_Enrollments UNIQUE (student_id, class_id),
        CONSTRAINT FK_Enrollments_Student FOREIGN KEY (student_id)
            REFERENCES dbo.Students (id) ON DELETE CASCADE,
        CONSTRAINT FK_Enrollments_Class FOREIGN KEY (class_id)
            REFERENCES dbo.Classes (id) ON DELETE CASCADE
    );
END
GO

-- =============================================================
-- TABLE: Grades
-- =============================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.Grades') AND type = 'U')
BEGIN
    CREATE TABLE dbo.Grades (
        id              INT IDENTITY(1,1)   NOT NULL,
        student_id      INT                 NOT NULL,
        subject_id      INT                 NOT NULL,
        marks_obtained  DECIMAL(6,2)        NOT NULL,
        max_marks       DECIMAL(6,2)        NOT NULL DEFAULT 100,
        exam_type       NVARCHAR(50)        NOT NULL DEFAULT 'Final',
        exam_date       DATE                NOT NULL,
        created_at      DATETIME2           NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT PK_Grades PRIMARY KEY CLUSTERED (id),
        CONSTRAINT FK_Grades_Student FOREIGN KEY (student_id)
            REFERENCES dbo.Students (id) ON DELETE CASCADE,
        CONSTRAINT FK_Grades_Subject FOREIGN KEY (subject_id)
            REFERENCES dbo.Subjects (id),
        CONSTRAINT CHK_Grades_Marks CHECK (marks_obtained >= 0 AND marks_obtained <= max_marks)
    );
END
GO

-- =============================================================
-- TABLE: Attendance
-- =============================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.Attendance') AND type = 'U')
BEGIN
    CREATE TABLE dbo.Attendance (
        id          INT IDENTITY(1,1)   NOT NULL,
        student_id  INT                 NOT NULL,
        class_id    INT                 NOT NULL,
        date        DATE                NOT NULL,
        status      NVARCHAR(10)        NOT NULL DEFAULT 'Present'
                        CHECK (status IN ('Present', 'Absent', 'Late')),
        created_at  DATETIME2           NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT PK_Attendance PRIMARY KEY CLUSTERED (id),
        CONSTRAINT UQ_Attendance UNIQUE (student_id, class_id, date),
        CONSTRAINT FK_Attendance_Student FOREIGN KEY (student_id)
            REFERENCES dbo.Students (id) ON DELETE CASCADE,
        CONSTRAINT FK_Attendance_Class FOREIGN KEY (class_id)
            REFERENCES dbo.Classes (id)
    );
END
GO

-- =============================================================
-- INDEXES
-- =============================================================
CREATE INDEX IX_Students_LastName ON dbo.Students (last_name);
CREATE INDEX IX_Enrollments_Student ON dbo.Enrollments (student_id);
CREATE INDEX IX_Enrollments_Class ON dbo.Enrollments (class_id);
CREATE INDEX IX_Grades_Student ON dbo.Grades (student_id);
CREATE INDEX IX_Grades_Subject ON dbo.Grades (subject_id);
CREATE INDEX IX_Attendance_Date ON dbo.Attendance (date);
CREATE INDEX IX_Attendance_Student ON dbo.Attendance (student_id);
GO

-- =============================================================
-- SAMPLE DATA (optional seed)
-- =============================================================
INSERT INTO dbo.Teachers (first_name, last_name, email, phone, specialization)
VALUES
    ('Alice',   'Johnson', 'alice.johnson@school.edu',  '555-0101', 'Mathematics'),
    ('Robert',  'Smith',   'robert.smith@school.edu',   '555-0102', 'Science'),
    ('Carol',   'Williams','carol.williams@school.edu', '555-0103', 'English'),
    ('David',   'Brown',   'david.brown@school.edu',    '555-0104', 'History');
GO

INSERT INTO dbo.Classes (name, grade_level, section, teacher_id, academic_year)
VALUES
    ('Grade 10-A', 10, 'A', 1, '2025-2026'),
    ('Grade 10-B', 10, 'B', 2, '2025-2026'),
    ('Grade 11-A', 11, 'A', 3, '2025-2026'),
    ('Grade 11-B', 11, 'B', 4, '2025-2026');
GO

INSERT INTO dbo.Students (first_name, last_name, date_of_birth, gender, email, phone)
VALUES
    ('Emma',    'Davis',   '2010-03-15', 'Female', 'emma.davis@mail.com',   '555-1001'),
    ('Liam',    'Wilson',  '2010-07-22', 'Male',   'liam.wilson@mail.com',  '555-1002'),
    ('Olivia',  'Moore',   '2009-11-08', 'Female', 'olivia.moore@mail.com', '555-1003'),
    ('Noah',    'Taylor',  '2009-05-30', 'Male',   'noah.taylor@mail.com',  '555-1004'),
    ('Ava',     'Anderson','2010-01-19', 'Female', 'ava.anderson@mail.com', '555-1005');
GO

INSERT INTO dbo.Subjects (name, code, class_id, teacher_id)
VALUES
    ('Mathematics',   'MATH10A', 1, 1),
    ('Science',       'SCI10A',  1, 2),
    ('English',       'ENG10A',  1, 3),
    ('Mathematics',   'MATH10B', 2, 1),
    ('Science',       'SCI10B',  2, 2),
    ('History',       'HIS11A',  3, 4);
GO

INSERT INTO dbo.Enrollments (student_id, class_id)
VALUES (1, 1), (2, 1), (3, 2), (4, 2), (5, 3);
GO
