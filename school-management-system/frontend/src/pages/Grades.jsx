import { useEffect, useState } from 'react'
import { getGradesByStudent, createGrade, updateGrade, deleteGrade } from '../services/gradeService'
import { getStudents } from '../services/studentService'
import { getSubjects } from '../services/subjectService'

const EMPTY = { student_id: '', subject_id: '', marks_obtained: '', max_marks: '100', exam_type: 'Final', exam_date: '' }

export default function Grades() {
  const [grades, setGrades] = useState([])
  const [students, setStudents] = useState([])
  const [subjects, setSubjects] = useState([])
  const [selectedStudent, setSelectedStudent] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState(null)

  useEffect(() => {
    getStudents().then((r) => setStudents(r.data))
    getSubjects().then((r) => setSubjects(r.data))
  }, [])

  const load = (studentId) => {
    if (!studentId) return setGrades([])
    getGradesByStudent(studentId)
      .then((r) => setGrades(r.data))
      .catch(() => setError('Failed to load grades'))
  }

  const handleStudentChange = (e) => {
    setSelectedStudent(e.target.value)
    load(e.target.value)
  }

  const openCreate = () => { setEditing(null); setForm({ ...EMPTY, student_id: selectedStudent }); setShowModal(true) }
  const openEdit   = (g)  => {
    setEditing(g)
    setForm({ ...g, marks_obtained: String(g.marks_obtained), max_marks: String(g.max_marks), student_id: String(g.student_id), subject_id: String(g.subject_id) })
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const payload = { student_id: parseInt(form.student_id, 10), subject_id: parseInt(form.subject_id, 10), marks_obtained: parseFloat(form.marks_obtained), max_marks: parseFloat(form.max_marks), exam_type: form.exam_type, exam_date: form.exam_date }
    try {
      if (editing) { await updateGrade(editing.id, { marks_obtained: payload.marks_obtained, max_marks: payload.max_marks, exam_type: payload.exam_type, exam_date: payload.exam_date }) }
      else         { await createGrade(payload) }
      setShowModal(false)
      load(selectedStudent)
    } catch { setError('Save failed') }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this grade?')) return
    await deleteGrade(id)
    load(selectedStudent)
  }

  const subjectName = (id) => subjects.find((s) => s.id === id)?.name || id

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">Grades</h4>
        <button className="btn btn-danger btn-sm" onClick={openCreate} disabled={!selectedStudent}>
          <i className="bi bi-plus-lg me-1" /> Add Grade
        </button>
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      <div className="mb-3" style={{ maxWidth: 320 }}>
        <label className="form-label fw-semibold">Filter by Student</label>
        <select className="form-select" value={selectedStudent} onChange={handleStudentChange}>
          <option value="">Select a student...</option>
          {students.map((s) => <option key={s.id} value={s.id}>{s.first_name} {s.last_name}</option>)}
        </select>
      </div>
      <div className="table-container">
        <table className="table table-hover mb-0">
          <thead className="table-light">
            <tr><th>#</th><th>Subject</th><th>Marks</th><th>Max</th><th>%</th><th>Exam Type</th><th>Date</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {grades.length === 0 && (
              <tr><td colSpan={8} className="text-center text-muted py-4">{selectedStudent ? 'No grades found' : 'Select a student above'}</td></tr>
            )}
            {grades.map((g) => (
              <tr key={g.id}>
                <td>{g.id}</td>
                <td>{subjectName(g.subject_id)}</td>
                <td>{g.marks_obtained}</td>
                <td>{g.max_marks}</td>
                <td><span className={`badge bg-${parseFloat(g.marks_obtained) / parseFloat(g.max_marks) >= 0.5 ? 'success' : 'danger'}`}>{Math.round((parseFloat(g.marks_obtained) / parseFloat(g.max_marks)) * 100)}%</span></td>
                <td>{g.exam_type}</td>
                <td>{g.exam_date}</td>
                <td>
                  <button className="btn btn-sm btn-outline-secondary me-1" onClick={() => openEdit(g)}><i className="bi bi-pencil" /></button>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(g.id)}><i className="bi bi-trash" /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h5 className="fw-bold mb-4">{editing ? 'Edit Grade' : 'Add Grade'}</h5>
            <form onSubmit={handleSubmit}>
              <div className="row g-3">
                {!editing && (
                  <>
                    <div className="col-6">
                      <label className="form-label">Student *</label>
                      <select className="form-select" required value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })}>
                        <option value="">Select...</option>
                        {students.map((s) => <option key={s.id} value={s.id}>{s.first_name} {s.last_name}</option>)}
                      </select>
                    </div>
                    <div className="col-6">
                      <label className="form-label">Subject *</label>
                      <select className="form-select" required value={form.subject_id} onChange={(e) => setForm({ ...form, subject_id: e.target.value })}>
                        <option value="">Select...</option>
                        {subjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                      </select>
                    </div>
                  </>
                )}
                <div className="col-6">
                  <label className="form-label">Marks Obtained *</label>
                  <input type="number" step="0.01" className="form-control" required value={form.marks_obtained} onChange={(e) => setForm({ ...form, marks_obtained: e.target.value })} />
                </div>
                <div className="col-6">
                  <label className="form-label">Max Marks *</label>
                  <input type="number" step="0.01" className="form-control" required value={form.max_marks} onChange={(e) => setForm({ ...form, max_marks: e.target.value })} />
                </div>
                <div className="col-6">
                  <label className="form-label">Exam Type</label>
                  <select className="form-select" value={form.exam_type} onChange={(e) => setForm({ ...form, exam_type: e.target.value })}>
                    <option>Final</option><option>Midterm</option><option>Quiz</option><option>Assignment</option>
                  </select>
                </div>
                <div className="col-6">
                  <label className="form-label">Exam Date *</label>
                  <input type="date" className="form-control" required value={form.exam_date} onChange={(e) => setForm({ ...form, exam_date: e.target.value })} />
                </div>
              </div>
              <div className="d-flex gap-2 justify-content-end mt-4">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-danger">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
