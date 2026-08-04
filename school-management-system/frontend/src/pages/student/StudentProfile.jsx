import { useStudent } from '../../context/StudentContext'

export default function StudentProfile() {
  const { currentStudent } = useStudent()

  if (!currentStudent) return null

  const fields = [
    { label: 'First Name',    value: currentStudent.first_name },
    { label: 'Last Name',     value: currentStudent.last_name },
    { label: 'Date of Birth', value: currentStudent.date_of_birth || 'N/A' },
    { label: 'Gender',        value: currentStudent.gender || 'N/A' },
    { label: 'Email',         value: currentStudent.email || 'N/A' },
    { label: 'Phone',         value: currentStudent.phone || 'N/A' },
    { label: 'Address',       value: currentStudent.address || 'N/A' },
  ]

  return (
    <div>
      <h4 className="fw-bold mb-4">My Profile</h4>
      <div className="table-container" style={{ maxWidth: 600 }}>
        <div className="d-flex align-items-center gap-4 mb-4">
          <div
            style={{
              width: 72,
              height: 72,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #2d6a4f, #52b788)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.8rem',
              color: '#fff',
              fontWeight: 700,
              flexShrink: 0,
            }}
          >
            {currentStudent.first_name[0]}{currentStudent.last_name[0]}
          </div>
          <div>
            <h5 className="fw-bold mb-0">
              {currentStudent.first_name} {currentStudent.last_name}
            </h5>
            <span className="badge" style={{ background: '#e8f5e9', color: '#2d6a4f' }}>
              Student ID: {currentStudent.id}
            </span>
          </div>
        </div>

        <table className="table table-bordered mb-0">
          <tbody>
            {fields.map(({ label, value }) => (
              <tr key={label}>
                <th style={{ width: '40%', background: '#f8f9fa' }}>{label}</th>
                <td>{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
