import { useState } from 'react'
import { API_V1 } from '../config'

function ContentCalendar({ calendar, onRegenerate, onSaveAndNext, onSave, onUpdatePost, loading, isSaved, companyProfile }) {
  const [selectedPost, setSelectedPost] = useState(null)
  const [copiedIndex, setCopiedIndex] = useState(null)
  const [showStrategy, setShowStrategy] = useState(false)
  const [showAnalysis, setShowAnalysis] = useState(false)
  const [showFeedback, setShowFeedback] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [regeneratingPost, setRegeneratingPost] = useState(null)
  const [postFeedback, setPostFeedback] = useState('')

  const togglePostStatus = (index, e) => {
    e.stopPropagation()
    const post = calendar.posts[index]
    const newStatus = post.status === 'posted' ? 'scheduled' : 'posted'
    onUpdatePost(index, { ...post, status: newStatus })
  }

  const getPostedCount = () => {
    return calendar?.posts?.filter(p => p.status === 'posted').length || 0
  }

  if (!calendar) {
    return (
      <div className="calendar-empty">
        <h2>📅 Content Calendar</h2>
        <p>No calendar generated yet. Go to the Dashboard to create your content calendar.</p>
      </div>
    )
  }

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  const getDayColor = (dayOfWeek) => {
    const colors = {
      'Monday': '#FF6B6B',
      'Tuesday': '#4ECDC4',
      'Wednesday': '#45B7D1',
      'Thursday': '#96CEB4',
      'Friday': '#FFEAA7',
      'Saturday': '#DDA0DD',
      'Sunday': '#98D8C8'
    }
    return colors[dayOfWeek] || '#6366f1'
  }

  const formatText = (text) => {
    if (!text) return ''
    return text.split('\n').map((line, i) => (
      <span key={i}>
        {line}
        {i < text.split('\n').length - 1 && <br />}
      </span>
    ))
  }

  const getNextMonth = () => {
    const next = new Date()
    next.setMonth(next.getMonth() + 1)
    return next.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  }

  const handleRegenerateWithFeedback = () => {
    onRegenerate(feedback)
    setShowFeedback(false)
    setFeedback('')
  }

  const handleRegeneratePost = async (index, post) => {
    setRegeneratingPost(index)
    
    try {
      const response = await fetch(`${API_V1}/content/regenerate-post`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...companyProfile,
          post_date: post.date,
          post_theme: post.theme,
          brand_analysis: calendar.brand_analysis || '',
          strategy: calendar.strategy || '',
          feedback: postFeedback
        })
      })

      if (response.ok) {
        const newPost = await response.json()
        onUpdatePost(index, newPost)
        setPostFeedback('')
      }
    } catch (err) {
      console.error('Error regenerating post:', err)
    } finally {
      setRegeneratingPost(null)
    }
  }

  return (
    <div className="calendar-container">
      <div className="calendar-header">
        <div>
          <h2>📅 {calendar.month}</h2>
          <p className="calendar-subtitle">
            {calendar.total_posts} posts • {calendar.posts_per_week}x per week • {calendar.platform}
          </p>
        </div>
        <div className="progress-tracker">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${(getPostedCount() / calendar.total_posts) * 100}%` }}
            />
          </div>
          <span className="progress-text">
            {getPostedCount()} / {calendar.total_posts} posted
          </span>
        </div>
      </div>

      {/* Action Bar */}
      <div className="calendar-actions">
        {!isSaved ? (
          <>
            <div className="action-group">
              <span className="action-label">Happy with this calendar?</span>
              <button 
                className="save-button"
                onClick={onSave}
              >
                ✓ Save {calendar.month}
              </button>
              <button 
                className="next-month-button"
                onClick={onSaveAndNext}
              >
                Save & Plan {getNextMonth()} →
              </button>
            </div>
            <div className="action-group">
              <span className="action-label">Want changes?</span>
              <button 
                className="regenerate-button"
                onClick={() => setShowFeedback(true)}
                disabled={loading}
              >
                🔄 Regenerate All
              </button>
            </div>
          </>
        ) : (
          <div className="saved-banner">
            <span>✓ Calendar saved!</span>
            <button 
              className="next-month-button"
              onClick={onSaveAndNext}
            >
              Plan {getNextMonth()} →
            </button>
          </div>
        )}
      </div>

      {/* Feedback Modal for Full Regeneration */}
      {showFeedback && (
        <div className="feedback-panel">
          <h4>What would you like different?</h4>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="e.g., More promotional content, less formal tone, focus more on customer stories..."
            rows={3}
          />
          <div className="feedback-actions">
            <button 
              className="secondary-button"
              onClick={() => setShowFeedback(false)}
            >
              Cancel
            </button>
            <button 
              className="primary-button"
              onClick={handleRegenerateWithFeedback}
              disabled={loading}
            >
              {loading ? '⏳ Regenerating...' : '🔄 Regenerate All Posts'}
            </button>
          </div>
        </div>
      )}

      {/* Strategy & Analysis Toggle Buttons */}
      <div className="workflow-toggles">
        {calendar.brand_analysis && (
          <button 
            className={`toggle-button ${showAnalysis ? 'active' : ''}`}
            onClick={() => { setShowAnalysis(!showAnalysis); setShowStrategy(false); }}
          >
            🔍 Brand Analysis
          </button>
        )}
        {calendar.strategy && (
          <button 
            className={`toggle-button ${showStrategy ? 'active' : ''}`}
            onClick={() => { setShowStrategy(!showStrategy); setShowAnalysis(false); }}
          >
            📋 Content Strategy
          </button>
        )}
      </div>

      {/* Brand Analysis Panel */}
      {showAnalysis && calendar.brand_analysis && (
        <div className="workflow-panel">
          <h3>🔍 Brand Analysis</h3>
          <p className="panel-description">AI-generated analysis of your brand identity and positioning</p>
          <div className="workflow-content">
            {formatText(calendar.brand_analysis)}
          </div>
        </div>
      )}

      {/* Strategy Panel */}
      {showStrategy && calendar.strategy && (
        <div className="workflow-panel">
          <h3>📋 Content Strategy</h3>
          <p className="panel-description">AI-generated content strategy based on your brand analysis</p>
          <div className="workflow-content">
            {formatText(calendar.strategy)}
          </div>
        </div>
      )}

      {/* Posts Grid */}
      <div className="calendar-grid">
        {calendar.posts.map((post, index) => (
          <div 
            key={index} 
            className={`calendar-card ${selectedPost === index ? 'expanded' : ''} ${post.status === 'posted' ? 'posted' : ''}`}
            onClick={() => setSelectedPost(selectedPost === index ? null : index)}
          >
            <div className="card-header" style={{ borderLeftColor: post.status === 'posted' ? '#10B981' : getDayColor(post.day_of_week) }}>
              <div className="card-date">
                <span className="day">{post.day_of_week}</span>
                <span className="date">{new Date(post.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
              </div>
              <div className="card-header-right">
                <button 
                  className={`check-button ${post.status === 'posted' ? 'checked' : ''}`}
                  onClick={(e) => togglePostStatus(index, e)}
                  title={post.status === 'posted' ? 'Mark as not posted' : 'Mark as posted'}
                >
                  {post.status === 'posted' ? '✓' : '○'}
                </button>
                <span className="post-number">#{index + 1}</span>
              </div>
            </div>

            <div className="card-theme">
              <strong>Theme:</strong> {post.theme}
            </div>

            {selectedPost === index && (
              <div className="card-details">
                <div className="post-content-section">
                  <h4>📝 Post Content</h4>
                  <div className="post-text">
                    {formatText(post.post_content)}
                  </div>
                  <div className="post-actions">
                    <button 
                      className="copy-button"
                      onClick={(e) => {
                        e.stopPropagation()
                        copyToClipboard(post.post_content, index)
                      }}
                    >
                      {copiedIndex === index ? '✓ Copied!' : '📋 Copy'}
                    </button>
                    <button 
                      className="regen-post-button"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleRegeneratePost(index, post)
                      }}
                      disabled={regeneratingPost === index}
                    >
                      {regeneratingPost === index ? '⏳ Regenerating...' : '🔄 Regenerate This Post'}
                    </button>
                  </div>
                </div>

                {/* Quick feedback for post regeneration */}
                <div className="post-feedback-section">
                  <input
                    type="text"
                    placeholder="Optional: What would you like different? (e.g., more casual, add humor)"
                    value={postFeedback}
                    onChange={(e) => setPostFeedback(e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>

                <div className="image-section">
                  <h4>📸 Image Idea</h4>
                  <p>{post.image_idea}</p>
                </div>

                <div className="timing-section">
                  <h4>⏰ Best Time</h4>
                  <p>{post.best_time}</p>
                </div>
              </div>
            )}

            {selectedPost !== index && (
              <div className="card-preview">
                <p>{post.post_content?.substring(0, 120)}...</p>
                <span className="expand-hint">Click to expand</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default ContentCalendar
