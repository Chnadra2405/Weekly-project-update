import { useEffect, useState } from 'react'
import { getSubjects, createSubject, updateSubject, deleteSubject } from '../services/subjectService'
import { getClasses } from '../services/classService'
import { getTeachers } from '../services/teacherService'

const EMPTY = { name: '', code: '', class_id: '', teacher_id: '' }

export default function Subjects() {
  const [subjects, setSubjects] = useState([])
  const [classes, setClasses] = useState([])
  const [teachers, setTeachers] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState(null)

  const load = () => {
    getSubjects().then((r) => setSubjects(r.data)).catch(() => setError('Failed to load subjects'))
    getClasses().then((r) => setClasses(r.data))
    getTeachers().then((r) => setTeachers(r.data))
  }

  useEffect(() => { load() }, [])

  const openCreate = () => { setEditing(null); setForm(EMPTY); setShowModal(true) }
  const openEdit   = (s)  => {
    setEditing(s)
    setForm({ ...s, class_id: String(s.class_id), teacher_id: s.teacher_id ? String(s.teacher_id) : '' })
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const payload = {
      ...form,
      class_id: parseInt(form.class_id, 10),
      teacher_id: form.teacher_id ? parseInt(form.teacher_id, 10) : null,
    }
    try {
      if (editing) { await updateSubject(editing.id, payload) }
      else         { await createSubject(payload) }
      setShowModal(false)
      load()
    } catch { setError('Save failed - code may already exist') }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this subject?')) return
    await deleteSubject(id)
    load()
  }

  const className  = (id) => classes.find((c) => c.id === id)?.name || '-'
  const teacherName = (id) => { const t = teachers.find((t) => t.id === id); return t ? `${t.first_name} ${t.last_name}` : '-' }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">Subjects</h4>
        <button className="btn btn-info btn-sm text-white" onClick={openCreate}>
          <i className="bi bi-plus-lg me-1" /> Add Subject
        </button>
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      <div className="table-container">
        <table className="table table-hover mb-0">
          <thead className="table-light">
            <tr><th>#</th><th>Name</th><th>Code</th><th>Class</th><th>Teacher</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {subjects.length === 0 && (
              <tr><td colSpan={6} className="text-center text-muted py-4">No subjects found</td></tr>
            )}
            {subjects.map((s) => (
              <tr key={s.id}>
                <td>{s.id}</td><td>{s.name}</td><td><code>{s.code}</code></td>
                <td>{className(s.class_id)}</td><td>{teacherName(s.teacher_id)}</td>
                <td>
                  <button className="btn btn-sm btn-outline-secondary me-1" onClick={() => openEdit(s)}><i className="bi bi-pencil" /></button>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(s.id)}><i className="bi bi-trash" /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h5 className="fw-bold mb-4">{editing ? 'Edit Subject' : 'Add Subject'}</h5>
            <form onSubmit={handleSubmit}>
              <div className="row g-3">
                <div className="col-8">
                  <label className="form-label">Subject Name *</label>
                  <input className="form-control" required value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
                <div className="col-4">
                  <label className="form-label">Code *</label>
                  <input className="form-control" required value={form.code}
                    onChange={(e) => setForm({ ...form, code: e.target.value })} />
                </div>
                <div className="col-6">
                  <label className="form-label">Class *</label>
                  <select className="form-select" required value={form.class_id}
                    onChange={(e) => setForm({ ...form, class_id: e.target.value })}>
                    <option value="">Select class...</option>
                    {classes.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div className="col-6">
                  <label className="form-label">Teacher</label>
                  <select className="form-select" value={form.teacher_id || ''}
                    onChange={(e) => setForm({ ...form, teacher_id: e.target.value })}>
                    <option value="">None</option>
                    {teachers.map((t) => <option key={t.id} value={t.id}>{t.first_name} {t.last_name}</option>)}
                  </select>
                </div>
              </div>
              <div className="d-flex gap-2 justify-content-end mt-4">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-info text-white">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
