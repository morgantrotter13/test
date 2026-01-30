import { useState, useEffect } from 'react'
import { API_V1 } from '../config'

function Dashboard({ 
  companyProfile, 
  calendar, 
  pastCalendarsCount, 
  onGenerateCalendar, 
  onSetupClick, 
  loading, 
  currentMonth,
  industryInsights,
  personalizedTips,
  onSaveInsights,
  onSaveTips,
  isSubscribed,
  isProPlan,
  isStarterPlan,
  onUpgradeClick,
  onGenerateTestPost
}) {
  const [tips, setTips] = useState(personalizedTips?.content || null)
  const [insights, setInsights] = useState(industryInsights?.content || null)
  const [loadingTips, setLoadingTips] = useState(false)
  const [loadingInsights, setLoadingInsights] = useState(false)
  const [testPost, setTestPost] = useState(null)
  const [loadingTestPost, setLoadingTestPost] = useState(false)
  const [hasUsedTestPost, setHasUsedTestPost] = useState(
    localStorage.getItem('hasUsedTestPost') === 'true'
  )

  // Sync with saved insights/tips from props
  useEffect(() => {
    if (industryInsights?.content) setInsights(industryInsights.content)
    if (personalizedTips?.content) setTips(personalizedTips.content)
  }, [industryInsights, personalizedTips])

  const fetchTips = async () => {
    if (!companyProfile) return
    if (!isProPlan) {
      onUpgradeClick()
      return
    }
    setLoadingTips(true)
    try {
      const response = await fetch(`${API_V1}/content/tips`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(companyProfile)
      })
      const data = await response.json()
      setTips(data.tips)
      // Save to parent for persistence
      onSaveTips({ content: data.tips, savedAt: new Date().toISOString() })
    } catch (err) {
      console.error('Error fetching tips:', err)
    } finally {
      setLoadingTips(false)
    }
  }

  const fetchInsights = async () => {
    if (!companyProfile) return
    if (!isProPlan) {
      onUpgradeClick()
      return
    }
    setLoadingInsights(true)
    try {
      const response = await fetch(`${API_V1}/content/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(companyProfile)
      })
      const data = await response.json()
      setInsights(data.insights)
      // Save to parent for persistence
      onSaveInsights({ content: data.insights, savedAt: new Date().toISOString() })
    } catch (err) {
      console.error('Error fetching insights:', err)
    } finally {
      setLoadingInsights(false)
    }
  }

  // Generate a single test post (free feature)
  const generateTestPost = async () => {
    if (!companyProfile) return
    setLoadingTestPost(true)
    try {
      const response = await fetch(`${API_V1}/content/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...companyProfile,
          post_topic: 'engaging post about your business',
          post_type: 'promotional',
          include_cta: true
        })
      })
      const data = await response.json()
      setTestPost(data.result)
      setHasUsedTestPost(true)
      localStorage.setItem('hasUsedTestPost', 'true')
    } catch (err) {
      console.error('Error generating test post:', err)
    } finally {
      setLoadingTestPost(false)
    }
  }

  // Handle calendar generation - Pro only
  const handleGenerateCalendar = () => {
    if (!isProPlan) {
      onUpgradeClick()
      return
    }
    onGenerateCalendar()
  }

  // Parse sections from the AI response
  const parseSections = (text) => {
    if (!text) return []
    
    const sections = []
    const lines = text.split('\n')
    let currentSection = null
    let currentContent = []

    for (const line of lines) {
      const trimmed = line.trim()
      
      const isHeader = /^[A-Z][A-Z\s\-–—]+$/.test(trimmed) || 
                       /^[A-Z][A-Z\s]+ - [A-Z\s]+$/.test(trimmed) ||
                       trimmed.endsWith(':') && trimmed === trimmed.toUpperCase()
      
      if (isHeader && trimmed.length > 3) {
        if (currentSection) {
          sections.push({ title: currentSection, content: currentContent })
        }
        currentSection = trimmed.replace(/:$/, '')
        currentContent = []
      } else if (trimmed.startsWith('•') || trimmed.startsWith('-') || trimmed.startsWith('*')) {
        currentContent.push(trimmed.replace(/^[•\-\*]\s*/, ''))
      } else if (trimmed && currentSection) {
        if (currentContent.length === 0 || !trimmed.startsWith('[')) {
          currentContent.push(trimmed)
        }
      }
    }
    
    if (currentSection) {
      sections.push({ title: currentSection, content: currentContent })
    }
    
    return sections
  }

  const getSectionIcon = (title) => {
    const lower = title.toLowerCase()
    if (lower.includes('quick win') || lower.includes('today')) return '⚡'
    if (lower.includes('engagement')) return '💬'
    if (lower.includes('content')) return '📝'
    if (lower.includes('growth')) return '📈'
    if (lower.includes('avoid') || lower.includes('mistake')) return '⚠️'
    if (lower.includes('pro tip') || lower.includes('advanced')) return '🎯'
    if (lower.includes('time')) return '⏰'
    if (lower.includes('hashtag')) return '#️⃣'
    if (lower.includes('trending') || lower.includes('trend')) return '🔥'
    if (lower.includes('competitor')) return '🔍'
    if (lower.includes('performing') || lower.includes('type')) return '📊'
    return '💡'
  }

  if (!companyProfile) {
    return (
      <div className="dashboard">
        <div className="welcome-card">
          <h2>👋 Welcome to Social Media Planner</h2>
          <p>Get started by setting up your company profile. We'll help you:</p>
          <ul>
            <li>📅 Generate a month's worth of content</li>
            <li>🎨 Get image ideas for each post</li>
            <li>📊 Research what's working in your industry</li>
            <li>💡 Get personalized tips to grow your audience</li>
          </ul>
          <button className="primary-button" onClick={onSetupClick}>
            Set Up Your Company Profile →
          </button>
        </div>
      </div>
    )
  }

  const insightSections = parseSections(insights)
  const tipSections = parseSections(tips)
  const hasInsightsOrTips = insights || tips

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="company-badge">
          <h2>{companyProfile.brand_name}</h2>
          <span className="platform-tag">{companyProfile.platform}</span>
        </div>
        <button className="edit-button" onClick={onSetupClick}>Edit Profile</button>
      </div>

      <div className="dashboard-grid">
        {/* Quick Stats */}
        <div className="stat-card">
          <h3>📅 Content Status</h3>
          {calendar ? (
            <div className="stat-content">
              <div className="stat-number">{calendar.total_posts}</div>
              <div className="stat-label">Posts for {calendar.month}</div>
              {pastCalendarsCount > 0 && (
                <div className="stat-detail">{pastCalendarsCount} past month(s) saved</div>
              )}
            </div>
          ) : (
            <div className="stat-content">
              <div className="stat-label">No calendar generated yet</div>
              {pastCalendarsCount > 0 && (
                <div className="stat-detail">{pastCalendarsCount} past month(s) saved</div>
              )}
            </div>
          )}
        </div>

        {/* Free Test Post Generator - Only for non-subscribers */}
        {!isSubscribed && (
          <div className="action-card free-tier">
            <div className="free-badge">✨ Free Preview</div>
            <h3>🎁 Try a Sample Post</h3>
            <p>
              Generate a single AI-powered post to see the quality of our content. 
              {hasUsedTestPost ? " You've used your free preview!" : " One free preview available!"}
            </p>
            
            {testPost ? (
              <div className="test-post-result">
                <div className="test-post-content">
                  <strong>Your Sample Post:</strong>
                  <p>{testPost}</p>
                </div>
                <div className="upgrade-prompt">
                  <p>🔥 Like what you see? Get started with a plan!</p>
                  <button className="upgrade-button" onClick={onUpgradeClick}>
                    View Plans →
                  </button>
                </div>
              </div>
            ) : (
              <button 
                className="secondary-button"
                onClick={generateTestPost}
                disabled={loadingTestPost || hasUsedTestPost}
              >
                {loadingTestPost ? '⏳ Generating...' : hasUsedTestPost ? '✓ Preview Used' : '🎯 Generate Free Sample'}
              </button>
            )}
          </div>
        )}

        {/* Starter Plan - 4 Posts Generator */}
        {isStarterPlan && (
          <div className="action-card starter-tier">
            <div className="starter-badge">🌱 Starter</div>
            <h3>📝 Generate Posts</h3>
            <p>You have 4 AI-generated posts per month with your Starter plan.</p>
            
            <button 
              className="primary-button"
              onClick={generateTestPost}
              disabled={loadingTestPost}
            >
              {loadingTestPost ? '⏳ Generating...' : '✨ Generate a Post'}
            </button>

            {testPost && (
              <div className="test-post-result">
                <div className="test-post-content">
                  <strong>Your Post:</strong>
                  <p>{testPost}</p>
                </div>
              </div>
            )}

            <div className="upgrade-prompt" style={{marginTop: '1rem'}}>
              <p>Want unlimited posts + full monthly calendars?</p>
              <button className="upgrade-button-small" onClick={onUpgradeClick}>
                Upgrade to Pro →
              </button>
            </div>
          </div>
        )}

        {/* Generate Calendar - Pro Feature Only */}
        <div className={`action-card ${!isProPlan ? 'locked' : ''}`}>
          {!isProPlan && <div className="pro-badge">⚡ Pro</div>}
          <h3>🚀 {calendar ? `Plan ${currentMonth}` : `Generate ${currentMonth} Calendar`}</h3>
          <p>
            {calendar 
              ? `Ready to plan content for ${currentMonth}? Set your goals, add upcoming events and promotions, and generate fresh content!`
              : `Create a full month of social media posts for ${currentMonth} with AI-powered content and image ideas.`
            }
          </p>
          
          {isProPlan && pastCalendarsCount > 0 && (
            <div className="history-note">
              ✨ AI remembers your {pastCalendarsCount} past month(s) and will generate completely fresh ideas
            </div>
          )}

          {isProPlan && hasInsightsOrTips && (
            <div className="insights-included-note">
              🧠 Your {insights ? 'industry insights' : ''}{insights && tips ? ' and ' : ''}{tips ? 'personalized tips' : ''} will be used to create better posts!
            </div>
          )}

          {!isProPlan ? (
            <div className="locked-feature">
              <p className="locked-text">🔒 Full monthly calendar requires Pro</p>
              <button className="upgrade-button" onClick={onUpgradeClick}>
                {isStarterPlan ? 'Upgrade to Pro →' : 'View Plans →'}
              </button>
            </div>
          ) : (
            <button 
              className="primary-button"
              onClick={handleGenerateCalendar}
              disabled={loading}
            >
              {loading ? '⏳ Generating...' : `📅 Plan ${currentMonth}`}
            </button>
          )}
        </div>

        {/* Industry Insights - Pro Only */}
        <div className={`insights-card ${!isProPlan ? 'locked' : ''}`}>
          <div className="card-header-row">
            <h3>📊 Industry Insights</h3>
            {!isProPlan && <span className="pro-badge-small">⚡ Pro</span>}
            {isProPlan && insights && (
              <span className="saved-badge">✓ Saved & will be used in posts</span>
            )}
          </div>
          {!isProPlan ? (
            <div className="locked-content">
              <div className="locked-preview">
                <div className="blur-item">🔥 Trending content in your industry...</div>
                <div className="blur-item">📈 What's working for competitors...</div>
                <div className="blur-item">⏰ Best posting times for engagement...</div>
              </div>
              <div className="locked-overlay">
                <p>🔒 Unlock AI-powered industry research</p>
                <button className="upgrade-button-small" onClick={onUpgradeClick}>
                  Upgrade to Pro
                </button>
              </div>
            </div>
          ) : insights ? (
            <>
              <div className="parsed-content">
                {insightSections.length > 0 ? (
                  insightSections.map((section, idx) => (
                    <div key={idx} className="content-section">
                      <h4>{getSectionIcon(section.title)} {section.title}</h4>
                      <ul>
                        {section.content.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  ))
                ) : (
                  <div className="raw-content">{insights}</div>
                )}
              </div>
              <button 
                className="refresh-button"
                onClick={fetchInsights}
                disabled={loadingInsights}
              >
                {loadingInsights ? '⏳ Refreshing...' : '🔄 Refresh Insights'}
              </button>
            </>
          ) : (
            <div className="insights-empty">
              <p>Get AI-powered research on what's working in your industry. These insights will be used to make your posts more effective!</p>
              <button 
                className="secondary-button"
                onClick={fetchInsights}
                disabled={loadingInsights}
              >
                {loadingInsights ? '⏳ Researching...' : 'Get Insights'}
              </button>
            </div>
          )}
        </div>

        {/* Tips - Pro Only */}
        <div className={`tips-card ${!isProPlan ? 'locked' : ''}`}>
          <div className="card-header-row">
            <h3>💡 Personalized Tips</h3>
            {!isProPlan && <span className="pro-badge-small">⚡ Pro</span>}
            {isProPlan && tips && (
              <span className="saved-badge">✓ Saved & will be used in posts</span>
            )}
          </div>
          {!isProPlan ? (
            <div className="locked-content">
              <div className="locked-preview">
                <div className="blur-item">⚡ Quick wins for immediate growth...</div>
                <div className="blur-item">💬 Engagement strategies that work...</div>
                <div className="blur-item">🎯 Pro tips for your niche...</div>
              </div>
              <div className="locked-overlay">
                <p>🔒 Unlock personalized AI recommendations</p>
                <button className="upgrade-button-small" onClick={onUpgradeClick}>
                  Upgrade to Pro
                </button>
              </div>
            </div>
          ) : tips ? (
            <>
              <div className="parsed-content">
                {tipSections.length > 0 ? (
                  tipSections.map((section, idx) => (
                    <div key={idx} className="tip-section">
                      <h4>{getSectionIcon(section.title)} {section.title}</h4>
                      <p>{section.content.join(' ')}</p>
                    </div>
                  ))
                ) : (
                  <div className="raw-content">{tips}</div>
                )}
              </div>
              <button 
                className="refresh-button"
                onClick={fetchTips}
                disabled={loadingTips}
              >
                {loadingTips ? '⏳ Refreshing...' : '🔄 Refresh Tips'}
              </button>
            </>
          ) : (
            <div className="tips-empty">
              <p>Get personalized recommendations for your social media. These tips will inform your content strategy!</p>
              <button 
                className="secondary-button"
                onClick={fetchTips}
                disabled={loadingTips}
              >
                {loadingTips ? '⏳ Loading...' : 'Get Tips'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
