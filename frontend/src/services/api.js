/**
 * AirGuard API service layer.
 * All backend communication goes through this module.
 * The Vite dev-server proxies /api → http://localhost:8000
 */

import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

// ── Interceptor: attach session_id from localStorage if available ──────────
client.interceptors.request.use((config) => {
  const sessionId = sessionStorage.getItem('airguard_session')
  if (sessionId && config.method === 'get' && !config.params?.session_id) {
    config.params = { ...config.params, session_id: sessionId }
  }
  return config
})

// ── Health ────────────────────────────────────────────────────────────────
export const checkHealth = () => client.get('/health')

// ── Upload & Analyze ──────────────────────────────────────────────────────
/**
 * Upload a CSV file. Returns { session_id, rows, columns, preview, _csv_b64 }
 */
export const uploadCSV = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await client.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

/**
 * Run AI analysis on uploaded CSV data.
 * @param {string} sessionId
 * @param {string} csvText  – raw CSV text from upload response
 * @param {number} contamination – 0.01..0.20
 */
export const analyzeData = async (sessionId, csvText, contamination = 0.05) => {
  const { data } = await client.post('/analyze', {
    session_id:    sessionId,
    _csv_b64:      csvText,
    contamination,
  })
  return data
}

// ── Dashboard ─────────────────────────────────────────────────────────────
export const getDashboard = (sessionId) =>
  client.get('/dashboard', { params: { session_id: sessionId } }).then((r) => r.data)

// ── Events ────────────────────────────────────────────────────────────────
export const getEvents = (sessionId, severity = null) => {
  const params = { session_id: sessionId }
  if (severity) params.severity = severity
  return client.get('/events', { params }).then((r) => r.data)
}

export const getEventById = (eventId, sessionId) =>
  client.get(`/events/${eventId}`, { params: { session_id: sessionId } }).then((r) => r.data)

// ── Air Quality ───────────────────────────────────────────────────────────
export const getAirQualityRecords = (sessionId, options = {}) => {
  const params = { session_id: sessionId, ...options }
  return client.get('/air-quality', { params }).then((r) => r.data)
}

export const getTrends = (sessionId, pollutant = 'pm25') =>
  client.get('/air-quality/trends', { params: { session_id: sessionId, pollutant } }).then((r) => r.data)

// ── Chatbot ───────────────────────────────────────────────────────────────
export const askChatbot = (question) =>
  client.post('/chat', { question }).then((r) => r.data)

// ── Demo ──────────────────────────────────────────────────────────────────
/**
 * Load the bundled synthetic demo dataset through the full backend pipeline.
 * Returns the same shape as analyzeData() so callers can treat both alike.
 */
export const loadDemo = () =>
  client.post('/demo').then((r) => r.data)

// ── Error helper ──────────────────────────────────────────────────────────
export const extractError = (err) => {
  if (err?.response?.data?.detail) return err.response.data.detail
  if (err?.message) return err.message
  return 'An unexpected error occurred.'
}
