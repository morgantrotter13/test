import { createContext, useContext, useState, useEffect } from 'react'
import { API_V1 } from '../config'

const AuthContext = createContext(null)

const API_BASE = API_V1

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('auth_token'))
  const [loading, setLoading] = useState(true)

  // Check if user is authenticated on mount
  useEffect(() => {
    if (token) {
      fetchCurrentUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchCurrentUser = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        // Token invalid, clear it
        localStorage.removeItem('auth_token')
        setToken(null)
      }
    } catch (err) {
      console.error('Error fetching user:', err)
    } finally {
      setLoading(false)
    }
  }

  const loginWithGoogle = async (googleAccessToken) => {
    console.log('AuthContext: Attempting login with token:', googleAccessToken?.substring(0, 20) + '...')
    console.log('AuthContext: Calling:', `${API_BASE}/auth/google`)
    
    try {
      const response = await fetch(`${API_BASE}/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ access_token: googleAccessToken })
      })

      console.log('AuthContext: Response status:', response.status)

      if (response.ok) {
        const data = await response.json()
        console.log('AuthContext: Login successful!', data.user)
        localStorage.setItem('auth_token', data.token)
        setToken(data.token)
        setUser(data.user)
        return { success: true }
      } else {
        const error = await response.json()
        console.log('AuthContext: Login failed:', error)
        return { success: false, error: error.detail || 'Login failed' }
      }
    } catch (err) {
      console.error('AuthContext: Network error:', err.message)
      console.error('AuthContext: Full error:', err)
      return { success: false, error: `Could not connect to server: ${err.message}` }
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    setToken(null)
    setUser(null)
  }

  // Authenticated fetch helper
  const authFetch = async (url, options = {}) => {
    const headers = {
      ...options.headers,
      'Content-Type': 'application/json'
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    return fetch(url, { ...options, headers })
  }

  // API helpers for user data
  const api = {
    // Company Profile
    getProfile: async () => {
      const res = await authFetch(`${API_BASE}/auth/profile`)
      return res.ok ? res.json() : null
    },
    
    saveProfile: async (profile) => {
      const res = await authFetch(`${API_BASE}/auth/profile`, {
        method: 'POST',
        body: JSON.stringify(profile)
      })
      return res.ok
    },

    // Calendars
    getCalendars: async () => {
      const res = await authFetch(`${API_BASE}/auth/calendars`)
      return res.ok ? res.json() : []
    },

    getCurrentCalendar: async () => {
      const res = await authFetch(`${API_BASE}/auth/calendars/current`)
      return res.ok ? res.json() : null
    },

    saveCalendar: async (calendar) => {
      const res = await authFetch(`${API_BASE}/auth/calendars`, {
        method: 'POST',
        body: JSON.stringify(calendar)
      })
      return res.ok
    },

    updateCalendar: async (calendarId, calendar) => {
      const res = await authFetch(`${API_BASE}/auth/calendars/${calendarId}`, {
        method: 'PUT',
        body: JSON.stringify(calendar)
      })
      return res.ok
    },

    // Insights
    getInsights: async () => {
      const res = await authFetch(`${API_BASE}/auth/insights`)
      return res.ok ? res.json() : { industry_insights: null, personalized_tips: null }
    },

    saveInsights: async (insights) => {
      const res = await authFetch(`${API_BASE}/auth/insights`, {
        method: 'POST',
        body: JSON.stringify(insights)
      })
      return res.ok
    }
  }

  // Check subscription status
  const isSubscribed = user?.is_subscribed || false
  const subscriptionPlan = user?.subscription_plan || null  // 'growth' (or legacy 'pro')
  const isGrowthPlan = subscriptionPlan === 'growth' || subscriptionPlan === 'pro'  // backward compat

  // Refresh subscription status
  const refreshSubscription = async () => {
    if (!token) return
    try {
      const response = await fetch(`${API_BASE}/payments/subscription-status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setUser(prev => prev ? { 
          ...prev, 
          is_subscribed: data.is_subscribed,
          subscription_plan: data.plan 
        } : null)
      }
    } catch (err) {
      console.error('Error checking subscription:', err)
    }
  }

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      isAuthenticated: !!user,
      isSubscribed,
      subscriptionPlan,
      isGrowthPlan,
      loginWithGoogle,
      logout,
      authFetch,
      api,
      refreshSubscription
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
