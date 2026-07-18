import api from './api'

const BASE = '/teachers'

export const getTeachers    = ()          => api.get(BASE)
export const getTeacher     = (id)        => api.get(`${BASE}/${id}`)
export const createTeacher  = (data)      => api.post(BASE, data)
export const updateTeacher  = (id, data)  => api.put(`${BASE}/${id}`, data)
export const deleteTeacher  = (id)        => api.delete(`${BASE}/${id}`)
