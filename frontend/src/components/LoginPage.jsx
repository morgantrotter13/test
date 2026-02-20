import GoogleSignIn from './GoogleSignIn'

function LoginPage({ onLoginSuccess }) {
  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <img src="/gridly-logo-dark.svg" alt="Gridly" className="login-logo" />
          <p>The AI content planning system for small businesses.</p>
        </div>

        <div className="login-features">
          <div className="feature">
            <span className="feature-icon">📋</span>
            <span>A full month of content in minutes</span>
          </div>
          <div className="feature">
            <span className="feature-icon">📊</span>
            <span>Industry insights that sharpen your strategy</span>
          </div>
          <div className="feature">
            <span className="feature-icon">🎯</span>
            <span>Personalized recommendations for your brand</span>
          </div>
        </div>

        <div className="login-divider">
          <span>Sign in to get started</span>
        </div>

        <GoogleSignIn onSuccess={onLoginSuccess} />

        <p className="login-terms">
          By signing in, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  )
}

export default LoginPage
