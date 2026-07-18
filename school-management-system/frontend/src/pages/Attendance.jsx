import { useEffect, useState } from 'react'
import { getAttendanceByClass, upsertAttendance } from '../services/attendanceService'
import { getClasses } from '../services/classService'
import { getEnrollmentsByClass } from '../services/enrollmentService'
import { getStudents } from '../services/studentService'

export default function Attendance() {
  const [classes, setClasses] = useState([])
  const [students, setStudents] = useState([])
  const [enrollments, setEnrollments] = useState([])
  const [selectedClass, setSelectedClass] = useState('')
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])
  const [attendance, setAttendance] = useState({})
  const [error, setError] = useState(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    getClasses().then((r) => setClasses(r.data))
    getStudents().then((r) => setStudents(r.data))
  }, [])

  useEffect(() => {
    if (!selectedClass) return setEnrollments([])
    getEnrollmentsByClass(selectedClass).then((r) => {
      setEnrollments(r.data)
      loadAttendance(selectedClass, selectedDate)
    })
  }, [selectedClass])

  useEffect(() => {
    if (selectedClass) loadAttendance(selectedClass, selectedDate)
  }, [selectedDate])

  const loadAttendance = (classId, date) => {
    getAttendanceByClass(classId, date)
      .then((r) => {
        const map = {}
        r.data.forEach((a) => { map[a.student_id] = a.status })
        setAttendance(map)
      })
      .catch(() => setAttendance({}))
  }

  const handleStatusChange = (studentId, status) => {
    setAttendance((prev) => ({ ...prev, [studentId]: status }))
  }

  const handleSave = async () => {
    setSaved(false)
    try {
      const promises = enrollments.map((e) =>
        upsertAttendance({
          student_id: e.student_id,
          class_id: parseInt(selectedClass, 10),
          date: selectedDate,
          status: attendance[e.student_id] || 'Present',
        })
      )
      await Promise.all(promises)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch { setError('Save failed') }
  }

  const studentName = (id) => { const s = students.find((s) => s.id === id); return s ? `${s.first_name} ${s.last_name}` : id }

  const statusBadge = (status) => {
    const map = { Present: 'success', Absent: 'danger', Late: 'warning' }
    return map[status] || 'secondary'
  }

  return (
    <div>
      <h4 className="fw-bold mb-4">Attendance</h4>
      {error && <div className="alert alert-danger">{error}</div>}
      {saved && <div className="alert alert-success">Attendance saved successfully.</div>}

      <div className="row g-3 mb-4">
        <div className="col-md-4">
          <label className="form-label fw-semibold">Class</label>
          <select className="form-select" value={selectedClass} onChange={(e) => setSelectedClass(e.target.value)}>
            <option value="">Select a class...</option>
            {classes.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div className="col-md-3">
          <label className="form-label fw-semibold">Date</label>
          <input type="date" className="form-control" value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)} />
        </div>
      </div>

      {selectedClass && (
        <>
          <div className="table-container">
            <table className="table table-hover mb-0">
              <thead className="table-light">
                <tr><th>#</th><th>Student</th><th>Status</th></tr>
              </thead>
              <tbody>
                {enrollments.length === 0 && (
                  <tr><td colSpan={3} className="text-center text-muted py-4">No students enrolled in this class</td></tr>
                )}
                {enrollments.map((e, i) => (
                  <tr key={e.id}>
                    <td>{i + 1}</td>
                    <td>{studentName(e.student_id)}</td>
                    <td>
                      <div className="d-flex gap-2">
                        {['Present', 'Absent', 'Late'].map((s) => (
                          <button
                            key={s}
                            className={`btn btn-sm btn-${attendance[e.student_id] === s ? statusBadge(s) : 'outline-' + statusBadge(s)}`}
                            onClick={() => handleStatusChange(e.student_id, s)}
                          >
                            {s}
                          </button>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {enrollments.length > 0 && (
            <button className="btn btn-primary mt-3" onClick={handleSave}>
              <i className="bi bi-check2-all me-1" /> Save Attendance
            </button>
          )}
        </>
      )}
    </div>
  )
}
