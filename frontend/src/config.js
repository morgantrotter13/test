// API Configuration
// Uses environment variable in production, localhost in development
export const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
export const API_V1 = `${API_BASE}/api/v1`
