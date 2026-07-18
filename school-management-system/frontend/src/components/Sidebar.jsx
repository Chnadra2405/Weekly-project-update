import { NavLink } from 'react-router-dom'

const links = [
  { to: '/dashboard',   icon: 'bi-speedometer2',   label: 'Dashboard' },
  { to: '/students',    icon: 'bi-people',          label: 'Students' },
  { to: '/teachers',    icon: 'bi-person-badge',    label: 'Teachers' },
  { to: '/classes',     icon: 'bi-building',        label: 'Classes' },
  { to: '/subjects',    icon: 'bi-book',            label: 'Subjects' },
  { to: '/enrollments', icon: 'bi-journal-check',   label: 'Enrollments' },
  { to: '/grades',      icon: 'bi-bar-chart',       label: 'Grades' },
  { to: '/attendance',  icon: 'bi-calendar3',       label: 'Attendance' },
]

export default function Sidebar() {
  return (
    <div className="sidebar d-flex flex-column p-3">
      <div className="mb-4 px-2">
        <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
          <i className="bi bi-mortarboard-fill me-2" style={{ color: '#4dabf7' }} />
          SchoolMS
        </span>
      </div>
      <nav className="d-flex flex-column gap-1">
        {links.map(({ to, icon, label }) => (
          <NavLink key={to} to={to} className={({ isActive }) => isActive ? 'active' : ''}>
            <i className={`bi ${icon}`} />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
