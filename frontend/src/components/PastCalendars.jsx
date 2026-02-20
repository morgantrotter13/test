function PastCalendars({ calendars, onSelectCalendar, onDeleteCalendar }) {
  if (!calendars || calendars.length === 0) {
    return (
      <div className="past-calendars-empty">
        <h2>📚 Past Plans</h2>
        <p>No past calendars saved yet. Build your first plan from the Dashboard.</p>
      </div>
    )
  }

  return (
    <div className="past-calendars">
      <h2>📚 Past Plans</h2>
      <p className="subtitle">Review previous months. Gridly uses this history to generate fresh, non-repetitive content.</p>
      
      <div className="calendars-list">
        {calendars.map((cal, index) => (
          <div key={index} className="calendar-history-card">
            <div className="history-card-header">
              <div>
                <h3>{cal.month}</h3>
                <span className="history-meta">
                  {cal.total_posts} posts · {cal.posts_per_week}x per week · {cal.platform}
                </span>
              </div>
              <div className="history-actions">
                <button 
                  className="view-button"
                  onClick={() => onSelectCalendar(cal)}
                >
                  View
                </button>
                <button 
                  className="delete-button"
                  onClick={() => onDeleteCalendar(index)}
                >
                  Remove
                </button>
              </div>
            </div>
            
            {cal.monthly_context && (
              <div className="history-context">
                {cal.monthly_context.promotions && (
                  <span className="context-tag">🏷️ Promotions</span>
                )}
                {cal.monthly_context.events && (
                  <span className="context-tag">🎉 Events</span>
                )}
                {cal.monthly_context.focuses && (
                  <span className="context-tag">🔍 Special Focus</span>
                )}
              </div>
            )}
            
            <div className="history-themes">
              <strong>Topics covered:</strong>
              <div className="theme-tags">
                {cal.posts.slice(0, 5).map((post, i) => (
                  <span key={i} className="theme-tag">
                    {post.theme.length > 30 ? post.theme.substring(0, 30) + '...' : post.theme}
                  </span>
                ))}
                {cal.posts.length > 5 && (
                  <span className="theme-tag more">+{cal.posts.length - 5} more</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default PastCalendars
