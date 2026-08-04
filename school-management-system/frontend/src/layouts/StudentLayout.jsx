import { Navigate, Outlet } from 'react-router-dom'
import { useStudent } from '../context/StudentContext'
import StudentSidebar from '../components/StudentSidebar'
import StudentNavbar from '../components/StudentNavbar'

export default function StudentLayout() {
  const { currentStudent } = useStudent()

  if (!currentStudent) {
    return <Navigate to="/student" replace />
  }

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <StudentSidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <StudentNavbar />
        <div className="main-content">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
