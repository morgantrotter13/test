import { useState } from 'react'

function NewMonthSetup({ companyProfile, onGenerate, onCancel, loading }) {
  const [keepGoals, setKeepGoals] = useState(true)
  const [newGoals, setNewGoals] = useState(companyProfile?.content_goals || '')
  const [promotions, setPromotions] = useState('')
  const [events, setEvents] = useState('')
  const [focuses, setFocuses] = useState('')
  const [postsPerWeek, setPostsPerWeek] = useState(3)

  const handleGenerate = () => {
    onGenerate({
      posts_per_week: postsPerWeek,
      content_goals: keepGoals ? companyProfile.content_goals : newGoals,
      monthly_promotions: promotions,
      monthly_events: events,
      monthly_focuses: focuses
    })
  }

  const nextMonth = new Date()
  nextMonth.setMonth(nextMonth.getMonth())
  const monthName = nextMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })

  return (
    <div className="new-month-overlay">
      <div className="new-month-modal">
        <h2>📋 Plan {monthName}</h2>
        <p className="modal-subtitle">Configure your content plan for the upcoming month.</p>

        <div className="month-form">
          {/* Goals Section */}
          <div className="form-section">
            <h3>🎯 Content Goals</h3>
            <div className="radio-group">
              <label className="radio-option">
                <input
                  type="radio"
                  checked={keepGoals}
                  onChange={() => setKeepGoals(true)}
                />
                <span>Keep same goals as before</span>
              </label>
              <label className="radio-option">
                <input
                  type="radio"
                  checked={!keepGoals}
                  onChange={() => setKeepGoals(false)}
                />
                <span>Set new goals for this month</span>
              </label>
            </div>
            
            {!keepGoals && (
              <textarea
                value={newGoals}
                onChange={(e) => setNewGoals(e.target.value)}
                placeholder="What do you want to achieve this month? (e.g., Launch new product, increase engagement, build community)"
                rows={3}
              />
            )}
            
            {keepGoals && (
              <div className="current-goals">
                <strong>Current goals:</strong> {companyProfile?.content_goals}
              </div>
            )}
          </div>

          {/* Promotions Section */}
          <div className="form-section">
            <h3>🏷️ Upcoming Promotions</h3>
            <p className="section-hint">Any sales, discounts, or special offers this month?</p>
            <textarea
              value={promotions}
              onChange={(e) => setPromotions(e.target.value)}
              placeholder="e.g., 20% off sale Jan 15-20, Free shipping weekend, New customer discount"
              rows={2}
            />
          </div>

          {/* Events Section */}
          <div className="form-section">
            <h3>🎉 Events and Milestones</h3>
            <p className="section-hint">Any events, launches, anniversaries, or holidays to highlight?</p>
            <textarea
              value={events}
              onChange={(e) => setEvents(e.target.value)}
              placeholder="e.g., Product launch Jan 10, Company anniversary, Valentine's Day promo"
              rows={2}
            />
          </div>

          {/* Focus Areas */}
          <div className="form-section">
            <h3>🔍 Special Focuses</h3>
            <p className="section-hint">Any specific topics or themes you want to emphasize?</p>
            <textarea
              value={focuses}
              onChange={(e) => setFocuses(e.target.value)}
              placeholder="e.g., Customer testimonials, Behind-the-scenes content, Educational series"
              rows={2}
            />
          </div>

          {/* Posting Frequency */}
          <div className="form-section">
            <h3>📆 Posting Frequency</h3>
            <div className="frequency-row">
              <select 
                value={postsPerWeek} 
                onChange={(e) => setPostsPerWeek(parseInt(e.target.value))}
              >
                <option value={1}>1 post/week</option>
                <option value={2}>2 posts/week</option>
                <option value={3}>3 posts/week</option>
                <option value={4}>4 posts/week</option>
                <option value={5}>5 posts/week</option>
                <option value={7}>Daily</option>
              </select>
              <span className="frequency-info">
                = {postsPerWeek * 4} posts for the month
              </span>
            </div>
          </div>
        </div>

        <div className="modal-actions">
          <button className="secondary-button" onClick={onCancel}>
            Cancel
          </button>
          <button 
            className="primary-button" 
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? '✨ Generating (~1-2 min)...' : '📅 Build My Plan'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default NewMonthSetup
