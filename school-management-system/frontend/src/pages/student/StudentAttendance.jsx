import { useEffect, useState } from 'react'
import { useStudent } from '../../context/StudentContext'
import { getAttendanceByStudent } from '../../services/attendanceService'
import { getClasses } from '../../services/classService'

export default function StudentAttendance() {
  const { currentStudent } = useStudent()
  const [attendance, setAttendance] = useState([])
  const [classes, setClasses] = useState([])
  const [filterStatus, setFilterStatus] = useState('All')

  useEffect(() => {
    if (!currentStudent) return
    getAttendanceByStudent(currentStudent.id).then((r) =>
      setAttendance([...r.data].sort((a, b) => new Date(b.date) - new Date(a.date)))
    )
    getClasses().then((r) => setClasses(r.data))
  }, [currentStudent])

  const className = (id) => classes.find((c) => c.id === id)?.name || id

  const total    = attendance.length
  const present  = attendance.filter((a) => a.status === 'Present').length
  const absent   = attendance.filter((a) => a.status === 'Absent').length
  const late     = attendance.filter((a) => a.status === 'Late').length
  const rate     = total ? Math.round((present / total) * 100) : null

  const filtered =
    filterStatus === 'All' ? attendance : attendance.filter((a) => a.status === filterStatus)

  const statusColor = { Present: 'success', Absent: 'danger', Late: 'warning' }

  return (
    <div>
      <h4 className="fw-bold mb-4">My Attendance</h4>

      <div className="row g-3 mb-4">
        {[
          { label: 'Total Days', value: total,    color: '#1a2942' },
          { label: 'Present',    value: present,  color: '#2d6a4f' },
          { label: 'Absent',     value: absent,   color: '#c0392b' },
          { label: 'Late',       value: late,     color: '#e67e22' },
          { label: 'Rate',       value: rate !== null ? `${rate}%` : 'N/A', color: rate >= 75 ? '#2d6a4f' : '#c0392b' },
        ].map(({ label, value, color }) => (
          <div key={label} className="col">
            <div
              className="p-3 rounded text-white text-center"
              style={{ background: color, boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}
            >
              <div style={{ fontSize: '1.7rem', fontWeight: 700, lineHeight: 1 }}>{value}</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>{label}</div>
            </div>
          </div>
        ))}
      </div>

      {rate !== null && rate < 75 && (
        <div className="alert alert-warning mb-4">
          <i className="bi bi-exclamation-triangle-fill me-2" />
          Your attendance rate is below 75%. Please consult your class teacher.
        </div>
      )}

      <div className="d-flex gap-2 mb-3">
        {['All', 'Present', 'Absent', 'Late'].map((s) => (
          <button
            key={s}
            className={`btn btn-sm ${filterStatus === s ? `btn-${s === 'All' ? 'dark' : statusColor[s]}` : `btn-outline-${s === 'All' ? 'dark' : statusColor[s]}`}`}
            onClick={() => setFilterStatus(s)}
          >
            {s}
          </button>
        ))}
      </div>

      <div className="table-container">
        <table className="table table-hover mb-0">
          <thead className="table-light">
            <tr>
              <th>#</th><th>Date</th><th>Class</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr>
                <td colSpan={4} className="text-center text-muted py-4">
                  No attendance records
                </td>
              </tr>
            )}
            {filtered.map((a, i) => (
              <tr key={a.id}>
                <td>{i + 1}</td>
                <td>{a.date}</td>
                <td>{className(a.class_id)}</td>
                <td>
                  <span className={`badge bg-${statusColor[a.status] || 'secondary'}`}>
                    {a.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
