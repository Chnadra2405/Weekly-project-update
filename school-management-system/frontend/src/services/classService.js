import api from './api'

const BASE = '/classes'

export const getClasses    = ()          => api.get(BASE)
export const getClass      = (id)        => api.get(`${BASE}/${id}`)
export const createClass   = (data)      => api.post(BASE, data)
export const updateClass   = (id, data)  => api.put(`${BASE}/${id}`, data)
export const deleteClass   = (id)        => api.delete(`${BASE}/${id}`)
