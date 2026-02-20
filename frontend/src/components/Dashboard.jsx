import { useState, useEffect } from 'react'
import { API_V1 } from '../config'
import { useAuth } from '../contexts/AuthContext'

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
  isGrowthPlan,
  onUpgradeClick
}) {
  const { token } = useAuth()
  const [tips, setTips] = useState(personalizedTips?.content || null)
  const [insights, setInsights] = useState(industryInsights?.content || null)
  const [loadingTips, setLoadingTips] = useState(false)
  const [loadingInsights, setLoadingInsights] = useState(false)
  const [testPost, setTestPost] = useState(
    localStorage.getItem('testPostContent') || null
  )
  const [testImageIdea, setTestImageIdea] = useState(
    localStorage.getItem('testImageIdea') || null
  )
  const [testReasoning, setTestReasoning] = useState(
    localStorage.getItem('testReasoning') || null
  )
  const [loadingTestPost, setLoadingTestPost] = useState(false)
  const [hasUsedTestPost, setHasUsedTestPost] = useState(
    localStorage.getItem('hasUsedTestPost') === 'true'
  )
  const [copied, setCopied] = useState(false)

  // Sync with saved insights/tips from props
  useEffect(() => {
    if (industryInsights?.content) setInsights(industryInsights.content)
    if (personalizedTips?.content) setTips(personalizedTips.content)
  }, [industryInsights, personalizedTips])

  const fetchTips = async () => {
    if (!companyProfile) return
    if (!isGrowthPlan) {
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
      onSaveTips({ content: data.tips, savedAt: new Date().toISOString() })
    } catch (err) {
      console.error('Error fetching tips:', err)
    } finally {
      setLoadingTips(false)
    }
  }

  const fetchInsights = async () => {
    if (!companyProfile) return
    if (!isGrowthPlan) {
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
      onSaveInsights({ content: data.insights, savedAt: new Date().toISOString() })
    } catch (err) {
      console.error('Error fetching insights:', err)
    } finally {
      setLoadingInsights(false)
    }
  }

  // Generate a single free post
  const generateTestPost = async () => {
    if (!companyProfile) return
    setLoadingTestPost(true)
    try {
      const response = await fetch(`${API_V1}/content/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...companyProfile,
          post_frequency: '3',
          content_themes: companyProfile.content_goals,
          post_topic: 'engaging post about your business',
          post_type: 'promotional',
          include_cta: true
        })
      })
      
      const data = await response.json()
      setTestPost(data.result)
      setTestImageIdea(data.image_idea || '')
      setTestReasoning(data.reasoning || '')
      setHasUsedTestPost(true)
      localStorage.setItem('hasUsedTestPost', 'true')
      localStorage.setItem('testPostContent', data.result)
      localStorage.setItem('testImageIdea', data.image_idea || '')
      localStorage.setItem('testReasoning', data.reasoning || '')
    } catch (err) {
      console.error('Error generating test post:', err)
    } finally {
      setLoadingTestPost(false)
    }
  }

  // Handle calendar generation - Growth only
  const handleGenerateCalendar = () => {
    if (!isGrowthPlan) {
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

  if (!companyProfile) {
    return (
      <div className="dashboard">
        <div className="welcome-card">
          <h2>Welcome to Gridly</h2>
          <p>Set up your company profile to get started. Gridly will help you:</p>
          <ul>
            <li>📋 Generate a full month of content in minutes</li>
            <li>🎯 Get image direction for each post</li>
            <li>📊 Research what's working in your industry</li>
            <li>💡 Receive personalized recommendations to grow your audience</li>
          </ul>
          <button className="primary-button" onClick={onSetupClick}>
            ☑️ Set Up Your Profile
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
          <h3>📋 Content Status</h3>
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

        {/* Free Post Generator - Only for non-subscribers */}
        {!isSubscribed && (
          <div className="action-card free-tier">
            <div className="free-badge">✨ Free</div>
            <h3>Try Gridly</h3>
            <p>
              Generate 1 AI-powered post to see the quality of Gridly's output.
              {hasUsedTestPost ? " You've used your free post." : " One free post included."}
            </p>
            
            {testPost ? (
              <div className="sample-post-showcase">
                <div className="sample-post-result">
                  <div className="sample-post-result-header">
                    <span className="result-badge">✨ Your Free Post</span>
                    <span className="result-platform">{companyProfile?.platform || 'Social Media'}</span>
                  </div>
                  
                  <div className="sample-post-content">
                    <p>{testPost}</p>
                  </div>

                  {testImageIdea && (
                    <div className="sample-post-image-idea">
                      <span className="image-idea-label">📸 Suggested Image</span>
                      <p>{testImageIdea}</p>
                    </div>
                  )}

                  {testReasoning && (
                    <div className="sample-post-reasoning">
                      <span className="reasoning-label">🎯 Why This Works</span>
                      <p>{testReasoning}</p>
                    </div>
                  )}
                  
                  <div className="sample-post-toolbar">
                    <button 
                      className={`copy-post-btn ${copied ? 'copied' : ''}`}
                      onClick={() => {
                        navigator.clipboard.writeText(testPost)
                        setCopied(true)
                        setTimeout(() => setCopied(false), 2000)
                      }}
                    >
                      {copied ? '✓ Copied!' : '📋 Copy Caption'}
                    </button>
                  </div>
                </div>
                
                <div className="sample-post-upsell">
                  <p>Like what you see? Unlock unlimited posts, full monthly calendars, and AI-powered insights.</p>
                  <button className="plan-button pro" onClick={onUpgradeClick}>
                    <span className="plan-name">⚡ Growth</span>
                    <span className="plan-price">$99/mo</span>
                    <span className="plan-desc">Unlimited content system</span>
                  </button>
                </div>
              </div>
            ) : (
              <button 
                className="primary-button free-post-button"
                onClick={generateTestPost}
                disabled={loadingTestPost}
              >
                {loadingTestPost ? '✨ Generating your post...' : '✦ Generate My Free Post'}
              </button>
            )}
          </div>
        )}

        {/* Generate Calendar - Growth Only */}
        <div className={`action-card ${!isGrowthPlan ? 'locked' : ''}`}>
          {!isGrowthPlan && <div className="pro-badge">⚡ Growth</div>}
          <h3>📅 {calendar ? `Plan ${currentMonth}` : `Build ${currentMonth} Calendar`}</h3>
          <p>
            {calendar 
              ? `Ready to plan content for ${currentMonth}? Set your goals, add upcoming events and promotions, and generate fresh content.`
              : `Create a full month of content for ${currentMonth} with AI-powered posts and image direction.`
            }
          </p>
          
          {isGrowthPlan && pastCalendarsCount > 0 && (
            <div className="history-note">
              ✨ Gridly references your {pastCalendarsCount} past month(s) to generate completely fresh ideas.
            </div>
          )}

          {isGrowthPlan && hasInsightsOrTips && (
            <div className="insights-included-note">
              🎯 Your {insights ? 'industry insights' : ''}{insights && tips ? ' and ' : ''}{tips ? 'personalized recommendations' : ''} will inform the content strategy.
            </div>
          )}

          {!isGrowthPlan ? (
            <div className="locked-feature">
              <p className="locked-text">🔒 Full monthly calendar requires Growth</p>
              <button className="upgrade-button" onClick={onUpgradeClick}>
                ⚡ Upgrade to Growth
              </button>
            </div>
          ) : (
            <button 
              className="primary-button"
              onClick={handleGenerateCalendar}
              disabled={loading}
            >
              {loading ? '✨ Generating...' : `📅 Build ${currentMonth} Plan`}
            </button>
          )}
        </div>

        {/* Industry Insights - Growth Only */}
        <div className={`insights-card ${!isGrowthPlan ? 'locked' : ''}`}>
          <div className="card-header-row">
            <h3>📊 Industry Insights</h3>
            {!isGrowthPlan && <span className="pro-badge-small">⚡ Growth</span>}
            {isGrowthPlan && insights && (
              <span className="saved-badge">✓ Saved — used in content generation</span>
            )}
          </div>
          {!isGrowthPlan ? (
            <div className="locked-content">
              <div className="locked-preview">
                <div className="blur-item">Trending content in your industry...</div>
                <div className="blur-item">What's working for competitors...</div>
                <div className="blur-item">Optimal posting times for engagement...</div>
              </div>
              <div className="locked-overlay">
                <p>🔒 Unlock AI-powered industry research</p>
                <button className="upgrade-button-small" onClick={onUpgradeClick}>
                  ⚡ Upgrade to Growth
                </button>
              </div>
            </div>
          ) : insights ? (
            <>
              <div className="parsed-content">
                {insightSections.length > 0 ? (
                  insightSections.map((section, idx) => (
                    <div key={idx} className="content-section">
                      <h4>{section.title}</h4>
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
                {loadingInsights ? '✨ Refreshing...' : '🔄 Refresh Insights'}
              </button>
            </>
          ) : (
            <div className="insights-empty">
              <p>Get AI-powered research on what's working in your industry. These insights will be used to improve your content.</p>
              <button 
                className="secondary-button"
                onClick={fetchInsights}
                disabled={loadingInsights}
              >
                {loadingInsights ? '✨ Researching...' : '📊 Get Insights'}
              </button>
            </div>
          )}
        </div>

        {/* Tips - Growth Only */}
        <div className={`tips-card ${!isGrowthPlan ? 'locked' : ''}`}>
          <div className="card-header-row">
            <h3>💡 Personalized Recommendations</h3>
            {!isGrowthPlan && <span className="pro-badge-small">⚡ Growth</span>}
            {isGrowthPlan && tips && (
              <span className="saved-badge">✓ Saved — used in content generation</span>
            )}
          </div>
          {!isGrowthPlan ? (
            <div className="locked-content">
              <div className="locked-preview">
                <div className="blur-item">Quick wins for immediate growth...</div>
                <div className="blur-item">Engagement strategies that work...</div>
                <div className="blur-item">Tailored advice for your niche...</div>
              </div>
              <div className="locked-overlay">
                <p>🔒 Unlock personalized AI recommendations</p>
                <button className="upgrade-button-small" onClick={onUpgradeClick}>
                  ⚡ Upgrade to Growth
                </button>
              </div>
            </div>
          ) : tips ? (
            <>
              <div className="parsed-content">
                {tipSections.length > 0 ? (
                  tipSections.map((section, idx) => (
                    <div key={idx} className="tip-section">
                      <h4>{section.title}</h4>
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
                {loadingTips ? '✨ Refreshing...' : '🔄 Refresh Recommendations'}
              </button>
            </>
          ) : (
            <div className="tips-empty">
              <p>Get personalized recommendations for your content strategy. These will inform how Gridly generates your posts.</p>
              <button 
                className="secondary-button"
                onClick={fetchTips}
                disabled={loadingTips}
              >
                {loadingTips ? '✨ Loading...' : '💡 Get Recommendations'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
