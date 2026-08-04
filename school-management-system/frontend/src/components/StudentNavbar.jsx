import { useNavigate } from 'react-router-dom'
import { useStudent } from '../context/StudentContext'

export default function StudentNavbar() {
  const { currentStudent } = useStudent()
  const navigate = useNavigate()

  return (
    <div
      style={{
        background: '#fff',
        borderBottom: '1px solid #e9ecef',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      <span style={{ fontWeight: 600, color: '#1a3d2b', fontSize: '1rem' }}>
        Student Portal
      </span>
      <div className="d-flex align-items-center gap-3">
        <span
          className="badge"
          style={{ background: '#e8f5e9', color: '#1a3d2b', fontSize: '0.8rem', padding: '6px 12px' }}
        >
          <i className="bi bi-person-fill me-1" />
          {currentStudent ? `${currentStudent.first_name} ${currentStudent.last_name}` : 'Student View'}
        </span>
        <button
          className="btn btn-sm btn-outline-secondary"
          onClick={() => navigate('/dashboard')}
          title="Switch to Admin view"
        >
          <i className="bi bi-shield-lock me-1" />
          Admin View
        </button>
      </div>
    </div>
  )
}
