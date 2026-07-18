import api from './api'

const BASE = '/subjects'

export const getSubjects        = ()          => api.get(BASE)
export const getSubjectsByClass = (classId)   => api.get(`${BASE}/class/${classId}`)
export const createSubject      = (data)      => api.post(BASE, data)
export const updateSubject      = (id, data)  => api.put(`${BASE}/${id}`, data)
export const deleteSubject      = (id)        => api.delete(`${BASE}/${id}`)
