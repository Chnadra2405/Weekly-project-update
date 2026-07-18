import api from './api'

const BASE = '/students'

export const getStudents    = ()          => api.get(BASE)
export const getStudent     = (id)        => api.get(`${BASE}/${id}`)
export const createStudent  = (data)      => api.post(BASE, data)
export const updateStudent  = (id, data)  => api.put(`${BASE}/${id}`, data)
export const deleteStudent  = (id)        => api.delete(`${BASE}/${id}`)
