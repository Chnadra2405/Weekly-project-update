import { createContext, useContext, useState } from 'react'

const StudentContext = createContext(null)

export function StudentProvider({ children }) {
  const [currentStudent, setCurrentStudent] = useState(null)

  return (
    <StudentContext.Provider value={{ currentStudent, setCurrentStudent }}>
      {children}
    </StudentContext.Provider>
  )
}

export function useStudent() {
  return useContext(StudentContext)
}
