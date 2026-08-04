import { useEffect, useState } from 'react'
import { useStudent } from '../../context/StudentContext'
import { getEnrollmentsByStudent } from '../../services/enrollmentService'
import { getGradesByStudent } from '../../services/gradeService'
import { getAttendanceByStudent } from '../../services/attendanceService'
import { getClasses } from '../../services/classService'
import { getSubjects } from '../../services/subjectService'

const StatCard = ({ title, value, icon, color }) => (
  <div className="col-md-4">
    <div className={`card stat-card text-white h-100`} style={{ background: color }}>
      <div className="card-body d-flex align-items-center gap-3">
        <i className={`bi ${icon}`} style={{ fontSize: '2.2rem', opacity: 0.85 }} />
        <div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, lineHeight: 1 }}>{value}</div>
          <div style={{ fontSize: '0.85rem', opacity: 0.9 }}>{title}</div>
        </div>
      </div>
    </div>
  </div>
)

export default function StudentDashboard() {
  const { currentStudent } = useStudent()
  const [enrollments, setEnrollments] = useState([])
  const [grades, setGrades] = useState([])
  const [attendance, setAttendance] = useState([])
  const [classes, setClasses] = useState([])
  const [subjects, setSubjects] = useState([])

  useEffect(() => {
    if (!currentStudent) return
    getEnrollmentsByStudent(currentStudent.id).then((r) => setEnrollments(r.data))
    getGradesByStudent(currentStudent.id).then((r) => setGrades(r.data))
    getAttendanceByStudent(currentStudent.id).then((r) => setAttendance(r.data))
    getClasses().then((r) => setClasses(r.data))
    getSubjects().then((r) => setSubjects(r.data))
  }, [currentStudent])

  if (!currentStudent) return null

  const presentCount = attendance.filter((a) => a.status === 'Present').length
  const attendanceRate = attendance.length
    ? Math.round((presentCount / attendance.length) * 100)
    : null

  const avgGrade =
    grades.length
      ? Math.round(
          (grades.reduce((acc, g) => acc + parseFloat(g.marks_obtained) / parseFloat(g.max_marks), 0) /
            grades.length) *
            100
        )
      : null

  const recentGrades = [...grades]
    .sort((a, b) => new Date(b.exam_date) - new Date(a.exam_date))
    .slice(0, 5)

  const subjectName = (id) => subjects.find((s) => s.id === id)?.name || id
  const className   = (id) => classes.find((c) => c.id === id)?.name || id

  return (
    <div>
      <div className="mb-4">
        <h4 className="fw-bold mb-0">
          Welcome, {currentStudent.first_name}!
        </h4>
        <p className="text-muted mb-0">Here is your academic overview</p>
      </div>

      <div className="row g-4 mb-4">
        <StatCard title="Enrolled Classes"   value={enrollments.length}                      icon="bi-building"     color="#2d6a4f" />
        <StatCard title="Grades Recorded"    value={grades.length}                           icon="bi-bar-chart-fill" color="#1a6091" />
        <StatCard title="Attendance Rate"    value={attendanceRate !== null ? `${attendanceRate}%` : 'N/A'} icon="bi-calendar-check-fill" color={attendanceRate >= 75 ? '#5c6bc0' : '#c0392b'} />
      </div>

      {avgGrade !== null && (
        <div
          className="mb-4 p-3 rounded"
          style={{ background: '#fff', boxShadow: '0 2px 8px rgba(0,0,0,0.07)' }}
        >
          <span className="fw-semibold">Average Score across all exams: </span>
          <span
            className={`badge ms-2 fs-6`}
            style={{ background: avgGrade >= 50 ? '#2d6a4f' : '#c0392b' }}
          >
            {avgGrade}%
          </span>
        </div>
      )}

      <div className="row g-4">
        <div className="col-md-6">
          <div className="table-container">
            <h6 className="fw-semibold mb-3">My Classes</h6>
            {enrollments.length === 0 ? (
              <p className="text-muted">No classes enrolled</p>
            ) : (
              <ul className="list-group list-group-flush">
                {enrollments.map((e) => (
                  <li key={e.id} className="list-group-item px-0">
                    <i className="bi bi-building me-2 text-success" />
                    {className(e.class_id)}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="col-md-6">
          <div className="table-container">
            <h6 className="fw-semibold mb-3">Recent Grades</h6>
            {recentGrades.length === 0 ? (
              <p className="text-muted">No grades recorded yet</p>
            ) : (
              <table className="table table-sm mb-0">
                <thead className="table-light">
                  <tr><th>Subject</th><th>Marks</th><th>%</th></tr>
                </thead>
                <tbody>
                  {recentGrades.map((g) => {
                    const pct = Math.round((parseFloat(g.marks_obtained) / parseFloat(g.max_marks)) * 100)
                    return (
                      <tr key={g.id}>
                        <td>{subjectName(g.subject_id)}</td>
                        <td>{g.marks_obtained} / {g.max_marks}</td>
                        <td>
                          <span className={`badge bg-${pct >= 50 ? 'success' : 'danger'}`}>{pct}%</span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
