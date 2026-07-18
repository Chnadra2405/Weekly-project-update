import { useEffect, useState } from 'react'
import { getClasses, createClass, updateClass, deleteClass } from '../services/classService'
import { getTeachers } from '../services/teacherService'

const EMPTY = { name: '', grade_level: '', section: 'A', teacher_id: '', academic_year: '' }

export default function Classes() {
  const [classes, setClasses] = useState([])
  const [teachers, setTeachers] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState(null)

  const load = () => {
    getClasses().then((r) => setClasses(r.data)).catch(() => setError('Failed to load classes'))
    getTeachers().then((r) => setTeachers(r.data))
  }

  useEffect(() => { load() }, [])

  const openCreate = () => { setEditing(null); setForm(EMPTY); setShowModal(true) }
  const openEdit   = (c)  => {
    setEditing(c)
    setForm({ ...c, grade_level: String(c.grade_level), teacher_id: c.teacher_id ? String(c.teacher_id) : '' })
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const payload = {
      ...form,
      grade_level: parseInt(form.grade_level, 10),
      teacher_id: form.teacher_id ? parseInt(form.teacher_id, 10) : null,
    }
    try {
      if (editing) { await updateClass(editing.id, payload) }
      else         { await createClass(payload) }
      setShowModal(false)
      load()
    } catch { setError('Save failed') }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this class?')) return
    await deleteClass(id)
    load()
  }

  const teacherName = (id) => {
    const t = teachers.find((t) => t.id === id)
    return t ? `${t.first_name} ${t.last_name}` : '-'
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">Classes</h4>
        <button className="btn btn-warning btn-sm" onClick={openCreate}>
          <i className="bi bi-plus-lg me-1" /> Add Class
        </button>
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      <div className="table-container">
        <table className="table table-hover mb-0">
          <thead className="table-light">
            <tr>
              <th>#</th><th>Name</th><th>Grade</th><th>Section</th>
              <th>Class Teacher</th><th>Academic Year</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {classes.length === 0 && (
              <tr><td colSpan={7} className="text-center text-muted py-4">No classes found</td></tr>
            )}
            {classes.map((c) => (
              <tr key={c.id}>
                <td>{c.id}</td>
                <td>{c.name}</td>
                <td>{c.grade_level}</td>
                <td>{c.section}</td>
                <td>{teacherName(c.teacher_id)}</td>
                <td>{c.academic_year}</td>
                <td>
                  <button className="btn btn-sm btn-outline-secondary me-1" onClick={() => openEdit(c)}>
                    <i className="bi bi-pencil" />
                  </button>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(c.id)}>
                    <i className="bi bi-trash" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h5 className="fw-bold mb-4">{editing ? 'Edit Class' : 'Add Class'}</h5>
            <form onSubmit={handleSubmit}>
              <div className="row g-3">
                <div className="col-8">
                  <label className="form-label">Class Name *</label>
                  <input className="form-control" required value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
                <div className="col-4">
                  <label className="form-label">Section</label>
                  <input className="form-control" value={form.section}
                    onChange={(e) => setForm({ ...form, section: e.target.value })} />
                </div>
                <div className="col-6">
                  <label className="form-label">Grade Level *</label>
                  <input type="number" className="form-control" required value={form.grade_level}
                    onChange={(e) => setForm({ ...form, grade_level: e.target.value })} />
                </div>
                <div className="col-6">
                  <label className="form-label">Academic Year *</label>
                  <input className="form-control" required placeholder="2025-2026" value={form.academic_year}
                    onChange={(e) => setForm({ ...form, academic_year: e.target.value })} />
                </div>
                <div className="col-12">
                  <label className="form-label">Class Teacher</label>
                  <select className="form-select" value={form.teacher_id || ''}
                    onChange={(e) => setForm({ ...form, teacher_id: e.target.value })}>
                    <option value="">None</option>
                    {teachers.map((t) => (
                      <option key={t.id} value={t.id}>{t.first_name} {t.last_name}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="d-flex gap-2 justify-content-end mt-4">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-warning">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
