function Header({ user, onLogout }) {
  return (
    <header className="header">
      <div className="container">
        <div className="header-left">
          <img src="/gridly-logo.svg" alt="Gridly" className="header-logo" />
        </div>
        
        {user && (
          <div className="header-user">
            <div className="user-info">
              <span className="user-name">{user.name || 'Welcome'}</span>
              <span className="user-email">{user.email}</span>
            </div>
            <button className="logout-button" onClick={onLogout}>
              Sign Out
            </button>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header
