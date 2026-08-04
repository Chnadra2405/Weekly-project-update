import { useNavigate } from 'react-router-dom'

export default function Navbar() {
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
      <span style={{ fontWeight: 600, color: '#1a2942', fontSize: '1.4rem' }}>
        School Management System
      </span>
      <div className="d-flex align-items-center gap-3">
        <button
          className="btn btn-sm btn-outline-success"
          onClick={() => navigate('/student')}
          title="Switch to Student view"
        >
          <i className="bi bi-person-graduation me-1" />
          Student View
        </button>
        <span style={{ color: '#6c757d', fontSize: '0.875rem' }}>
          <i className="bi bi-shield-lock-fill me-1 text-primary" />
          Admin
        </span>
      </div>
    </div>
  )
}
