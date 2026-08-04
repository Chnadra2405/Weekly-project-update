import { useEffect, useState } from 'react'
import { useStudent } from '../../context/StudentContext'
import { getEnrollmentsByStudent } from '../../services/enrollmentService'
import { getClasses } from '../../services/classService'
import { getSubjectsByClass } from '../../services/subjectService'
import { getTeachers } from '../../services/teacherService'

export default function StudentClasses() {
  const { currentStudent } = useStudent()
  const [enrollments, setEnrollments] = useState([])
  const [classes, setClasses] = useState([])
  const [subjects, setSubjects] = useState([])
  const [teachers, setTeachers] = useState([])

  useEffect(() => {
    if (!currentStudent) return
    getEnrollmentsByStudent(currentStudent.id).then((r) => setEnrollments(r.data))
    getClasses().then((r) => setClasses(r.data))
    getTeachers().then((r) => setTeachers(r.data))
  }, [currentStudent])

  useEffect(() => {
    if (enrollments.length === 0) return
    const fetches = enrollments.map((e) => getSubjectsByClass(e.class_id))
    Promise.all(fetches).then((results) => {
      const all = results.flatMap((r) => r.data)
      setSubjects(all)
    })
  }, [enrollments])

  const classDetail  = (id) => classes.find((c) => c.id === id)
  const teacherName  = (id) => { const t = teachers.find((t) => t.id === id); return t ? `${t.first_name} ${t.last_name}` : '-' }

  return (
    <div>
      <h4 className="fw-bold mb-4">My Classes</h4>
      {enrollments.length === 0 ? (
        <div className="text-muted">You are not enrolled in any classes.</div>
      ) : (
        enrollments.map((e) => {
          const cls = classDetail(e.class_id)
          if (!cls) return null
          const classSubjects = subjects.filter((s) => s.class_id === cls.id)
          return (
            <div key={e.id} className="table-container mb-4">
              <div className="d-flex justify-content-between align-items-start mb-3">
                <div>
                  <h5 className="fw-bold mb-0">{cls.name}</h5>
                  <span className="text-muted" style={{ fontSize: '0.875rem' }}>
                    Grade {cls.grade_level} &bull; Section {cls.section} &bull; {cls.academic_year}
                  </span>
                </div>
                {cls.teacher_id && (
                  <span className="badge bg-success">
                    <i className="bi bi-person-badge me-1" />
                    Class Teacher: {teacherName(cls.teacher_id)}
                  </span>
                )}
              </div>

              <h6 className="fw-semibold mb-2">Subjects</h6>
              {classSubjects.length === 0 ? (
                <p className="text-muted">No subjects assigned yet</p>
              ) : (
                <table className="table table-bordered mb-0">
                  <thead className="table-light">
                    <tr><th>Subject Name</th><th>Code</th><th>Teacher</th></tr>
                  </thead>
                  <tbody>
                    {classSubjects.map((s) => (
                      <tr key={s.id}>
                        <td>{s.name}</td>
                        <td><code>{s.code}</code></td>
                        <td>{teacherName(s.teacher_id)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )
        })
      )}
    </div>
  )
}
