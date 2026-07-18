import api from './api'

const BASE = '/grades'

export const getGradesByStudent = (studentId)  => api.get(`${BASE}/student/${studentId}`)
export const getGradesBySubject = (subjectId)  => api.get(`${BASE}/subject/${subjectId}`)
export const createGrade        = (data)       => api.post(BASE, data)
export const updateGrade        = (id, data)   => api.put(`${BASE}/${id}`, data)
export const deleteGrade        = (id)         => api.delete(`${BASE}/${id}`)
