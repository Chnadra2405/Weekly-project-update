import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useStudent } from '../../context/StudentContext'
import { getStudents } from '../../services/studentService'
import { getEnrollmentsByStudent } from '../../services/enrollmentService'
import { getGradesByStudent } from '../../services/gradeService'
import { getAttendanceByStudent } from '../../services/attendanceService'

export default function StudentSelectPage() {
  const [students, setStudents] = useState([])
  const [selected, setSelected] = useState('')
  const { setCurrentStudent } = useStudent()
  const navigate = useNavigate()

  useEffect(() => {
    getStudents().then((r) => setStudents(r.data))
  }, [])

  const handleEnter = () => {
    const student = students.find((s) => String(s.id) === selected)
    if (!student) return
    setCurrentStudent(student)
    navigate('/student/dashboard')
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #1a3d2b 0%, #2d6a4f 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          background: '#fff',
          borderRadius: 16,
          padding: '40px 48px',
          width: '100%',
          maxWidth: 440,
          boxShadow: '0 16px 48px rgba(0,0,0,0.2)',
          textAlign: 'center',
        }}
      >
        <i className="bi bi-mortarboard-fill" style={{ fontSize: '3rem', color: '#2d6a4f' }} />
        <h4 className="fw-bold mt-3 mb-1">Student Portal</h4>
        <p className="text-muted mb-4" style={{ fontSize: '0.9rem' }}>
          Select your name to access your academic information
        </p>

        <div className="mb-3 text-start">
          <label className="form-label fw-semibold">Select Student</label>
          <select
            className="form-select form-select-lg"
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
          >
            <option value="">Choose your name...</option>
            {students.map((s) => (
              <option key={s.id} value={s.id}>
                {s.first_name} {s.last_name}
              </option>
            ))}
          </select>
        </div>

        <button
          className="btn btn-lg w-100 mt-2"
          style={{ background: '#2d6a4f', color: '#fff' }}
          onClick={handleEnter}
          disabled={!selected}
        >
          <i className="bi bi-box-arrow-in-right me-2" />
          Enter Student Portal
        </button>

        <hr className="my-4" />
        <button
          className="btn btn-outline-secondary btn-sm"
          onClick={() => navigate('/dashboard')}
        >
          <i className="bi bi-shield-lock me-1" />
          Go to Admin Panel
        </button>
      </div>
    </div>
  )
}
