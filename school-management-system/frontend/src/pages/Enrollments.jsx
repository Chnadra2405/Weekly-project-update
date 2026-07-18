import { useEffect, useState } from 'react'
import { getEnrollments, createEnrollment, deleteEnrollment } from '../services/enrollmentService'
import { getStudents } from '../services/studentService'
import { getClasses } from '../services/classService'

export default function Enrollments() {
  const [enrollments, setEnrollments] = useState([])
  const [students, setStudents] = useState([])
  const [classes, setClasses] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ student_id: '', class_id: '' })
  const [error, setError] = useState(null)

  const load = () => {
    getEnrollments().then((r) => setEnrollments(r.data)).catch(() => setError('Failed to load enrollments'))
    getStudents().then((r) => setStudents(r.data))
    getClasses().then((r) => setClasses(r.data))
  }

  useEffect(() => { load() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await createEnrollment({ student_id: parseInt(form.student_id, 10), class_id: parseInt(form.class_id, 10) })
      setShowModal(false)
      setForm({ student_id: '', class_id: '' })
      load()
    } catch { setError('Enrollment failed - student may already be enrolled in this class') }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Remove this enrollment?')) return
    await deleteEnrollment(id)
    load()
  }

  const studentName = (id) => { const s = students.find((s) => s.id === id); return s ? `${s.first_name} ${s.last_name}` : id }
  const className   = (id) => classes.find((c) => c.id === id)?.name || id

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">Enrollments</h4>
        <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
          <i className="bi bi-plus-lg me-1" /> Enroll Student
        </button>
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      <div className="table-container">
        <table className="table table-hover mb-0">
          <thead className="table-light">
            <tr><th>#</th><th>Student</th><th>Class</th><th>Enrolled At</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {enrollments.length === 0 && (
              <tr><td colSpan={5} className="text-center text-muted py-4">No enrollments found</td></tr>
            )}
            {enrollments.map((e) => (
              <tr key={e.id}>
                <td>{e.id}</td>
                <td>{studentName(e.student_id)}</td>
                <td>{className(e.class_id)}</td>
                <td>{new Date(e.enrolled_at).toLocaleDateString()}</td>
                <td>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(e.id)}>
                    <i className="bi bi-x-circle" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-box" onClick={(ev) => ev.stopPropagation()}>
            <h5 className="fw-bold mb-4">Enroll Student in Class</h5>
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label">Student *</label>
                <select className="form-select" required value={form.student_id}
                  onChange={(e) => setForm({ ...form, student_id: e.target.value })}>
                  <option value="">Select student...</option>
                  {students.map((s) => <option key={s.id} value={s.id}>{s.first_name} {s.last_name}</option>)}
                </select>
              </div>
              <div className="mb-3">
                <label className="form-label">Class *</label>
                <select className="form-select" required value={form.class_id}
                  onChange={(e) => setForm({ ...form, class_id: e.target.value })}>
                  <option value="">Select class...</option>
                  {classes.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div className="d-flex gap-2 justify-content-end mt-4">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Enroll</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
