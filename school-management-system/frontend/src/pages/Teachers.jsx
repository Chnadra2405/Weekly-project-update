import { useEffect, useState } from 'react'
import { getTeachers, createTeacher, updateTeacher, deleteTeacher } from '../services/teacherService'

const EMPTY = { first_name: '', last_name: '', email: '', phone: '', specialization: '' }

export default function Teachers() {
  const [teachers, setTeachers] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState(null)

  const load = () => getTeachers().then((r) => setTeachers(r.data)).catch(() => setError('Failed to load teachers'))

  useEffect(() => { load() }, [])

  const openCreate = () => { setEditing(null); setForm(EMPTY); setShowModal(true) }
  const openEdit   = (t)  => { setEditing(t); setForm({ ...t }); setShowModal(true) }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editing) { await updateTeacher(editing.id, form) }
      else         { await createTeacher(form) }
      setShowModal(false)
      load()
    } catch { setError('Save failed') }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this teacher?')) return
    await deleteTeacher(id)
    load()
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">Teachers</h4>
        <button className="btn btn-success btn-sm" onClick={openCreate}>
          <i className="bi bi-plus-lg me-1" /> Add Teacher
        </button>
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      <div className="table-container">
        <table className="table table-hover mb-0">
          <thead className="table-light">
            <tr>
              <th>#</th><th>First Name</th><th>Last Name</th>
              <th>Email</th><th>Phone</th><th>Specialization</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {teachers.length === 0 && (
              <tr><td colSpan={7} className="text-center text-muted py-4">No teachers found</td></tr>
            )}
            {teachers.map((t) => (
              <tr key={t.id}>
                <td>{t.id}</td>
                <td>{t.first_name}</td>
                <td>{t.last_name}</td>
                <td>{t.email}</td>
                <td>{t.phone || '-'}</td>
                <td>{t.specialization || '-'}</td>
                <td>
                  <button className="btn btn-sm btn-outline-secondary me-1" onClick={() => openEdit(t)}>
                    <i className="bi bi-pencil" />
                  </button>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(t.id)}>
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
            <h5 className="fw-bold mb-4">{editing ? 'Edit Teacher' : 'Add Teacher'}</h5>
            <form onSubmit={handleSubmit}>
              <div className="row g-3">
                <div className="col-6">
                  <label className="form-label">First Name *</label>
                  <input className="form-control" required value={form.first_name}
                    onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
                </div>
                <div className="col-6">
                  <label className="form-label">Last Name *</label>
                  <input className="form-control" required value={form.last_name}
                    onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
                </div>
                <div className="col-12">
                  <label className="form-label">Email *</label>
                  <input type="email" className="form-control" required value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })} />
                </div>
                <div className="col-6">
                  <label className="form-label">Phone</label>
                  <input className="form-control" value={form.phone || ''}
                    onChange={(e) => setForm({ ...form, phone: e.target.value })} />
                </div>
                <div className="col-6">
                  <label className="form-label">Specialization</label>
                  <input className="form-control" value={form.specialization || ''}
                    onChange={(e) => setForm({ ...form, specialization: e.target.value })} />
                </div>
              </div>
              <div className="d-flex gap-2 justify-content-end mt-4">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-success">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
