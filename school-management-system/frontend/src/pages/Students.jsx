import { useEffect, useState } from 'react'
import { getStudents, createStudent, updateStudent, deleteStudent } from '../services/studentService'

const EMPTY = { first_name: '', last_name: '', date_of_birth: '', gender: '', email: '', phone: '', address: '' }

export default function Students() {
  const [students, setStudents] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState(null)

  const load = () => getStudents().then((r) => setStudents(r.data)).catch(() => setError('Failed to load students'))

  useEffect(() => { load() }, [])

  const openCreate = () => { setEditing(null); setForm(EMPTY); setShowModal(true) }
  const openEdit   = (s)  => { setEditing(s); setForm({ ...s, date_of_birth: s.date_of_birth || '' }); setShowModal(true) }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const payload = { ...form, date_of_birth: form.date_of_birth || null }
    try {
      if (editing) { await updateStudent(editing.id, payload) }
      else         { await createStudent(payload) }
      setShowModal(false)
      load()
    } catch { setError('Save failed') }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this student?')) return
    await deleteStudent(id)
    load()
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">Students</h4>
        <button className="btn btn-primary btn-sm" onClick={openCreate}>
          <i className="bi bi-plus-lg me-1" /> Add Student
        </button>
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      <div className="table-container">
        <table className="table table-hover mb-0">
          <thead className="table-light">
            <tr>
              <th>#</th><th>First Name</th><th>Last Name</th><th>DOB</th>
              <th>Gender</th><th>Email</th><th>Phone</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {students.length === 0 && (
              <tr><td colSpan={8} className="text-center text-muted py-4">No students found</td></tr>
            )}
            {students.map((s) => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.first_name}</td>
                <td>{s.last_name}</td>
                <td>{s.date_of_birth || '-'}</td>
                <td>{s.gender || '-'}</td>
                <td>{s.email || '-'}</td>
                <td>{s.phone || '-'}</td>
                <td>
                  <button className="btn btn-sm btn-outline-secondary me-1" onClick={() => openEdit(s)}>
                    <i className="bi bi-pencil" />
                  </button>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(s.id)}>
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
            <h5 className="fw-bold mb-4">{editing ? 'Edit Student' : 'Add Student'}</h5>
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
                <div className="col-6">
                  <label className="form-label">Date of Birth</label>
                  <input type="date" className="form-control" value={form.date_of_birth || ''}
                    onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })} />
                </div>
                <div className="col-6">
                  <label className="form-label">Gender</label>
                  <select className="form-select" value={form.gender || ''}
                    onChange={(e) => setForm({ ...form, gender: e.target.value })}>
                    <option value="">Select...</option>
                    <option>Male</option><option>Female</option><option>Other</option>
                  </select>
                </div>
                <div className="col-6">
                  <label className="form-label">Email</label>
                  <input type="email" className="form-control" value={form.email || ''}
                    onChange={(e) => setForm({ ...form, email: e.target.value })} />
                </div>
                <div className="col-6">
                  <label className="form-label">Phone</label>
                  <input className="form-control" value={form.phone || ''}
                    onChange={(e) => setForm({ ...form, phone: e.target.value })} />
                </div>
                <div className="col-12">
                  <label className="form-label">Address</label>
                  <textarea className="form-control" rows={2} value={form.address || ''}
                    onChange={(e) => setForm({ ...form, address: e.target.value })} />
                </div>
              </div>
              <div className="d-flex gap-2 justify-content-end mt-4">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
