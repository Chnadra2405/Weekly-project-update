import api from './api'

const BASE = '/attendance'

export const getAttendanceByClass   = (classId, date) =>
  api.get(`${BASE}/class/${classId}`, { params: { date } })
export const getAttendanceByStudent = (studentId)     =>
  api.get(`${BASE}/student/${studentId}`)
export const upsertAttendance       = (data)          => api.post(BASE, data)
export const deleteAttendance       = (id)            => api.delete(`${BASE}/${id}`)
