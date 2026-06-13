import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  timeout: 15000,
})

export const getJobs = async (status) => {
  const params = status ? { status } : undefined
  const { data } = await api.get('/api/jobs', { params })
  return data
}

export const createJob = async (payload) => {
  const { data } = await api.post('/api/jobs', payload)
  return data
}

export const submitWork = async (id, submission) => {
  const { data } = await api.post(`/api/jobs/${id}/submit`, { submission })
  return data
}

export const decide = async (id, decision) => {
  const { data } = await api.post(`/api/jobs/${id}/decide`, { decision })
  return data
}
