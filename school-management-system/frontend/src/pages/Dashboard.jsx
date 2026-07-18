import { useEffect, useState } from 'react'
import { getDashboardStats } from '../services/dashboardService'

const StatCard = ({ title, value, icon, color }) => (
  <div className="col-md-3">
    <div className={`card stat-card text-white bg-${color} h-100`}>
      <div className="card-body d-flex align-items-center gap-3">
        <i className={`bi ${icon}`} style={{ fontSize: '2.4rem', opacity: 0.85 }} />
        <div>
          <div style={{ fontSize: '2rem', fontWeight: 700, lineHeight: 1 }}>{value}</div>
          <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>{title}</div>
        </div>
      </div>
    </div>
  </div>
)

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getDashboardStats()
      .then((res) => setStats(res.data))
      .catch(() => setError('Could not load statistics. Ensure the backend is running.'))
  }, [])

  return (
    <div>
      <h4 className="mb-4 fw-bold">Dashboard</h4>
      {error && <div className="alert alert-warning">{error}</div>}
      {stats ? (
        <div className="row g-4">
          <StatCard title="Total Students" value={stats.total_students} icon="bi-people-fill"    color="primary" />
          <StatCard title="Total Teachers" value={stats.total_teachers} icon="bi-person-badge-fill" color="success" />
          <StatCard title="Total Classes"  value={stats.total_classes}  icon="bi-building"       color="warning" />
          <StatCard title="Total Subjects" value={stats.total_subjects} icon="bi-book-fill"      color="danger"  />
        </div>
      ) : (
        !error && <div className="text-muted">Loading...</div>
      )}

      <div className="mt-5 table-container">
        <h6 className="fw-semibold mb-3">Quick Navigation</h6>
        <p className="text-muted">
          Use the sidebar to navigate between Students, Teachers, Classes, Subjects, Enrollments,
          Grades, and Attendance management sections.
        </p>
      </div>
    </div>
  )
}
