import { NavLink } from 'react-router-dom'
import { useStudent } from '../context/StudentContext'

const links = [
  { to: '/student/dashboard', icon: 'bi-speedometer2', label: 'My Dashboard' },
  { to: '/student/classes',   icon: 'bi-building',     label: 'My Classes' },
  { to: '/student/grades',    icon: 'bi-bar-chart',    label: 'My Grades' },
  { to: '/student/attendance',icon: 'bi-calendar3',    label: 'My Attendance' },
  { to: '/student/profile',   icon: 'bi-person-circle',label: 'My Profile' },
]

export default function StudentSidebar() {
  const { currentStudent } = useStudent()

  return (
    <div className="sidebar d-flex flex-column p-3" style={{ background: '#1a3d2b' }}>
      <div className="mb-4 px-2">
        <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
          <i className="bi bi-mortarboard-fill me-2" style={{ color: '#69db7c' }} />
          SchoolMS
        </span>
        <div style={{ fontSize: '0.75rem', color: '#69db7c', marginTop: 4 }}>Student Portal</div>
      </div>

      {currentStudent && (
        <div
          style={{
            background: 'rgba(105,219,124,0.12)',
            borderRadius: 8,
            padding: '10px 12px',
            marginBottom: 16,
          }}
        >
          <div style={{ fontSize: '0.75rem', color: '#adb5bd' }}>Logged in as</div>
          <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.9rem' }}>
            {currentStudent.first_name} {currentStudent.last_name}
          </div>
        </div>
      )}

      <nav className="d-flex flex-column gap-1">
        {links.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => isActive ? 'active' : ''}
            style={{ '--bs-link-color': '#69db7c' }}
          >
            <i className={`bi ${icon}`} />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
