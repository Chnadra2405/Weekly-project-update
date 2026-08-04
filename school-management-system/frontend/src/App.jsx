import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { StudentProvider } from './context/StudentContext'
import Sidebar from './components/Sidebar'
import Navbar from './components/Navbar'
import StudentLayout from './layouts/StudentLayout'
import Dashboard from './pages/Dashboard'
import Students from './pages/Students'
import Teachers from './pages/Teachers'
import Classes from './pages/Classes'
import Subjects from './pages/Subjects'
import Enrollments from './pages/Enrollments'
import Grades from './pages/Grades'
import Attendance from './pages/Attendance'
import StudentSelectPage from './pages/student/StudentSelectPage'
import StudentDashboard from './pages/student/StudentDashboard'
import StudentClasses from './pages/student/StudentClasses'
import StudentGrades from './pages/student/StudentGrades'
import StudentAttendance from './pages/student/StudentAttendance'
import StudentProfile from './pages/student/StudentProfile'

function AdminLayout({ children }) {
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Navbar />
        <div className="main-content">{children}</div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <StudentProvider>
      <BrowserRouter>
        <Routes>
          {/* Admin routes */}
          <Route
            path="/"
            element={
              <AdminLayout>
                <Navigate to="/dashboard" replace />
              </AdminLayout>
            }
          />
          <Route path="/dashboard"   element={<AdminLayout><Dashboard /></AdminLayout>} />
          <Route path="/students"    element={<AdminLayout><Students /></AdminLayout>} />
          <Route path="/teachers"    element={<AdminLayout><Teachers /></AdminLayout>} />
          <Route path="/classes"     element={<AdminLayout><Classes /></AdminLayout>} />
          <Route path="/subjects"    element={<AdminLayout><Subjects /></AdminLayout>} />
          <Route path="/enrollments" element={<AdminLayout><Enrollments /></AdminLayout>} />
          <Route path="/grades"      element={<AdminLayout><Grades /></AdminLayout>} />
          <Route path="/attendance"  element={<AdminLayout><Attendance /></AdminLayout>} />

          {/* Student portal: selection screen (no layout) */}
          <Route path="/student" element={<StudentSelectPage />} />

          {/* Student portal: protected routes with student layout */}
          <Route path="/student" element={<StudentLayout />}>
            <Route path="dashboard"  element={<StudentDashboard />} />
            <Route path="classes"    element={<StudentClasses />} />
            <Route path="grades"     element={<StudentGrades />} />
            <Route path="attendance" element={<StudentAttendance />} />
            <Route path="profile"    element={<StudentProfile />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </StudentProvider>
  )
}
