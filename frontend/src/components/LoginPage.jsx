import GoogleSignIn from './GoogleSignIn'

function LoginPage({ onLoginSuccess }) {
  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <div className="login-icon">📅</div>
          <h1>Social Media Planner</h1>
          <p>AI-powered content planning for your business</p>
        </div>

        <div className="login-features">
          <div className="feature">
            <span className="feature-icon">🎯</span>
            <span>Generate a month of content in minutes</span>
          </div>
          <div className="feature">
            <span className="feature-icon">📊</span>
            <span>Get industry insights & personalized tips</span>
          </div>
          <div className="feature">
            <span className="feature-icon">💾</span>
            <span>Save calendars & track your progress</span>
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
