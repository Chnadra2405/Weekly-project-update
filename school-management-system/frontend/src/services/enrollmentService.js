import api from './api'

const BASE = '/enrollments'

export const getEnrollments         = ()            => api.get(BASE)
export const getEnrollmentsByStudent = (studentId)  => api.get(`${BASE}/student/${studentId}`)
export const getEnrollmentsByClass   = (classId)    => api.get(`${BASE}/class/${classId}`)
export const createEnrollment        = (data)       => api.post(BASE, data)
export const deleteEnrollment        = (id)         => api.delete(`${BASE}/${id}`)
