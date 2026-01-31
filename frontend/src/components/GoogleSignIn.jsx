import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

function GoogleSignIn({ onSuccess }) {
  const { loginWithGoogle } = useAuth()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleReady, setGoogleReady] = useState(false)

  useEffect(() => {
    // Load Google Sign-In script
    if (window.google) {
      setGoogleReady(true)
      return
    }

    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.onload = () => {
      console.log('Google script loaded')
      setGoogleReady(true)
    }
    script.onerror = () => {
      setError('Failed to load Google Sign-In')
    }
    document.body.appendChild(script)
  }, [])

  const handleSignIn = () => {
    if (!GOOGLE_CLIENT_ID) {
      setError('Google Client ID not configured')
      return
    }

    if (!window.google) {
      setError('Google Sign-In not loaded yet. Please wait...')
      return
    }

    setLoading(true)
    setError('')
    console.log('Starting Google sign-in...')

    try {
      const tokenClient = window.google.accounts.oauth2.initTokenClient({
        client_id: GOOGLE_CLIENT_ID,
        scope: 'email profile openid',
        callback: async (tokenResponse) => {
          console.log('Got token response:', tokenResponse)
          
          if (tokenResponse.error) {
            console.error('Token error:', tokenResponse.error)
            setError(tokenResponse.error_description || 'Google sign-in failed')
            setLoading(false)
            return
          }

          if (tokenResponse.access_token) {
            console.log('Sending token to backend...')
            const result = await loginWithGoogle(tokenResponse.access_token)
            console.log('Backend result:', result)
            
            if (result.success) {
              onSuccess?.()
            } else {
              setError(result.error || 'Login failed')
            }
          } else {
            setError('No access token received')
          }
          setLoading(false)
        },
        error_callback: (err) => {
          console.error('OAuth error:', err)
          setError('Google sign-in was cancelled or failed')
          setLoading(false)
        }
      })

      tokenClient.requestAccessToken({ prompt: 'select_account' })
    } catch (err) {
      console.error('Sign-in error:', err)
      setError('Failed to start Google sign-in')
      setLoading(false)
    }
  }

  if (!GOOGLE_CLIENT_ID) {
    return (
      <div className="google-signin-container">
        <div className="google-signin-fallback">
          <p className="signin-note">Google Sign-In not configured.</p>
          <p>Add VITE_GOOGLE_CLIENT_ID to frontend/.env</p>
        </div>
      </div>
    )
  }

  return (
    <div className="google-signin-container">
      {error && (
        <div className="signin-error">
          ⚠️ {error}
        </div>
      )}

      <button 
        className="google-signin-button-manual"
        onClick={handleSignIn}
        disabled={loading || !googleReady}
      >
        {loading ? (
          <>
            <span className="spinner"></span>
            Signing in...
          </>
        ) : (
          <>
            <svg className="google-icon" viewBox="0 0 24 24" width="20" height="20">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
          </>
        )}
      </button>

      {!googleReady && (
        <p className="loading-note">Loading Google Sign-In...</p>
      )}
    </div>
  )
}

export default GoogleSignIn
