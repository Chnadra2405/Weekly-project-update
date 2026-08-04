import { useEffect, useState } from 'react'
import { useStudent } from '../../context/StudentContext'
import { getGradesByStudent } from '../../services/gradeService'
import { getSubjects } from '../../services/subjectService'

export default function StudentGrades() {
  const { currentStudent } = useStudent()
  const [grades, setGrades] = useState([])
  const [subjects, setSubjects] = useState([])
  const [filter, setFilter] = useState('All')

  useEffect(() => {
    if (!currentStudent) return
    getGradesByStudent(currentStudent.id).then((r) => setGrades(r.data))
    getSubjects().then((r) => setSubjects(r.data))
  }, [currentStudent])

  const examTypes = ['All', ...new Set(grades.map((g) => g.exam_type))]

  const filtered = filter === 'All' ? grades : grades.filter((g) => g.exam_type === filter)

  const subjectName = (id) => subjects.find((s) => s.id === id)?.name || id

  const gradeLabel = (pct) => {
    if (pct >= 90) return { letter: 'A+', color: '#2d6a4f' }
    if (pct >= 80) return { letter: 'A',  color: '#52b788' }
    if (pct >= 70) return { letter: 'B',  color: '#1a6091' }
    if (pct >= 60) return { letter: 'C',  color: '#e67e22' }
    if (pct >= 50) return { letter: 'D',  color: '#d35400' }
    return                { letter: 'F',  color: '#c0392b' }
  }

  const overall =
    grades.length
      ? Math.round(
          (grades.reduce((a, g) => a + parseFloat(g.marks_obtained) / parseFloat(g.max_marks), 0) /
            grades.length) *
            100
        )
      : null

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">My Grades</h4>
        {overall !== null && (
          <span
            className="badge fs-6"
            style={{ background: gradeLabel(overall).color, padding: '8px 16px' }}
          >
            Overall: {overall}% ({gradeLabel(overall).letter})
          </span>
        )}
      </div>

      <div className="mb-3 d-flex gap-2 flex-wrap">
        {examTypes.map((t) => (
          <button
            key={t}
            className={`btn btn-sm ${filter === t ? 'btn-dark' : 'btn-outline-secondary'}`}
            onClick={() => setFilter(t)}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="table-container">
        <table className="table table-hover mb-0">
          <thead className="table-light">
            <tr>
              <th>Subject</th>
              <th>Exam Type</th>
              <th>Date</th>
              <th>Marks</th>
              <th>Score</th>
              <th>Grade</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center text-muted py-4">
                  No grades recorded yet
                </td>
              </tr>
            )}
            {filtered.map((g) => {
              const pct = Math.round((parseFloat(g.marks_obtained) / parseFloat(g.max_marks)) * 100)
              const { letter, color } = gradeLabel(pct)
              return (
                <tr key={g.id}>
                  <td className="fw-semibold">{subjectName(g.subject_id)}</td>
                  <td>
                    <span className="badge bg-secondary">{g.exam_type}</span>
                  </td>
                  <td>{g.exam_date}</td>
                  <td>
                    {g.marks_obtained} / {g.max_marks}
                  </td>
                  <td>
                    <div className="d-flex align-items-center gap-2">
                      <div
                        className="progress flex-grow-1"
                        style={{ height: 8, minWidth: 80 }}
                      >
                        <div
                          className="progress-bar"
                          style={{ width: `${pct}%`, background: color }}
                        />
                      </div>
                      <span style={{ fontSize: '0.85rem', minWidth: 36 }}>{pct}%</span>
                    </div>
                  </td>
                  <td>
                    <span
                      className="badge fw-bold"
                      style={{ background: color, minWidth: 36 }}
                    >
                      {letter}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
