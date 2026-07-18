export default function Navbar() {
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
      <span style={{ fontWeight: 600, color: '#1a2942', fontSize: '1rem' }}>
        School Management System
      </span>
      <span style={{ color: '#6c757d', fontSize: '0.875rem' }}>
        <i className="bi bi-person-circle me-1" />
        Admin
      </span>
    </div>
  )
}
