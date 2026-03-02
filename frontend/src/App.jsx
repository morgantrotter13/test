import { useState, useEffect } from 'react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { API_V1 } from './config'
import Header from './components/Header'
import CompanySetup from './components/CompanySetup'
import ContentCalendar from './components/ContentCalendar'
import Dashboard from './components/Dashboard'
import NewMonthSetup from './components/NewMonthSetup'
import PastCalendars from './components/PastCalendars'
import GeneratingProgress from './components/GeneratingProgress'
import LoginPage from './components/LoginPage'
import PricingPage from './components/PricingPage'
import './App.css'

function AppContent() {
  const { isAuthenticated, user, loading: authLoading, logout, api, isSubscribed, isGrowthPlan, refreshSubscription } = useAuth()
  
  const [activeTab, setActiveTab] = useState('dashboard')
  const [companyProfile, setCompanyProfile] = useState(null)
  const [currentCalendar, setCurrentCalendar] = useState(null)
  const [pastCalendars, setPastCalendars] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showNewMonthSetup, setShowNewMonthSetup] = useState(false)
  const [isCurrentSaved, setIsCurrentSaved] = useState(false)
  const [generatingPostsPerWeek, setGeneratingPostsPerWeek] = useState(3)
  const [industryInsights, setIndustryInsights] = useState(null)
  const [personalizedTips, setPersonalizedTips] = useState(null)
  const [currentCalendarId, setCurrentCalendarId] = useState(null)
  const [dataLoaded, setDataLoaded] = useState(false)

  // Load user data from database when authenticated
  useEffect(() => {
    if (isAuthenticated && !dataLoaded) {
      loadUserData()
    }
  }, [isAuthenticated])

  // Verify subscription after Stripe checkout redirect
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    if (params.get('subscribed') === 'true' && isAuthenticated) {
      const sessionId = params.get('session_id')
      
      const verifyAndRefresh = async () => {
        // If we have a session ID, verify directly with Stripe (doesn't depend on webhook)
        if (sessionId) {
          try {
            const token = localStorage.getItem('auth_token')
            const res = await fetch(`${API_V1}/payments/verify-session`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({ session_id: sessionId })
            })
            if (res.ok) {
              const data = await res.json()
              console.log('Session verified:', data)
            }
          } catch (err) {
            console.error('Session verification error:', err)
          }
        }
        
        // Always refresh subscription status from DB
        await refreshSubscription()
      }
      
      verifyAndRefresh()
      
      // Clean up the URL
      window.history.replaceState({}, '', window.location.pathname)
    }
  }, [isAuthenticated])

  const loadUserData = async () => {
    try {
      // Load company profile
      const profile = await api.getProfile()
      if (profile) {
        setCompanyProfile(profile)
      }

      // Load current calendar
      const current = await api.getCurrentCalendar()
      if (current) {
        setCurrentCalendar(current)
        setCurrentCalendarId(current.id)
        setIsCurrentSaved(true)
      }

      // Load past calendars
      const calendars = await api.getCalendars()
      if (calendars && calendars.length > 0) {
        // Filter out current if it exists
        const past = current 
          ? calendars.filter(c => c.id !== current.id)
          : calendars
        setPastCalendars(past)
      }

      // Load insights
      const insights = await api.getInsights()
      if (insights.industry_insights) {
        setIndustryInsights({ content: insights.industry_insights })
      }
      if (insights.personalized_tips) {
        setPersonalizedTips({ content: insights.personalized_tips })
      }

      setDataLoaded(true)
    } catch (err) {
      console.error('Error loading user data:', err)
    }
  }

  // Save company profile
  const saveCompanyProfile = async (profile) => {
    setCompanyProfile(profile)
    
    if (isAuthenticated) {
      await api.saveProfile(profile)
    } else {
      localStorage.setItem('companyProfile', JSON.stringify(profile))
    }
    
    setActiveTab('dashboard')
  }

  // Generate content calendar with monthly context
  const generateCalendar = async (monthlySettings, feedback = '') => {
    if (!companyProfile) {
      setError('Please set up your company profile first')
      return
    }

    setLoading(true)
    setError(null)
    setGeneratingPostsPerWeek(monthlySettings.posts_per_week || 3)

    // Get past themes to avoid
    const pastThemes = pastCalendars.flatMap(cal => 
      (cal.posts || []).map(post => post.theme)
    ).slice(0, 30)

    try {
      const response = await fetch(`${API_V1}/content/calendar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...companyProfile,
          content_goals: monthlySettings.content_goals,
          posts_per_week: monthlySettings.posts_per_week,
          monthly_promotions: monthlySettings.monthly_promotions,
          monthly_events: monthlySettings.monthly_events,
          monthly_focuses: monthlySettings.monthly_focuses,
          past_themes: pastThemes,
          feedback: feedback,
          industry_insights: industryInsights?.content || '',
          personalized_tips: personalizedTips?.content || ''
        })
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data = await response.json()
      
      data.monthly_context = {
        promotions: monthlySettings.monthly_promotions,
        events: monthlySettings.monthly_events,
        focuses: monthlySettings.monthly_focuses
      }
      data.saved = false

      setCurrentCalendar(data)
      setIsCurrentSaved(false)
      setCurrentCalendarId(null)
      
      if (!isAuthenticated) {
        localStorage.setItem('currentCalendar', JSON.stringify(data))
      }
      
      setShowNewMonthSetup(false)
      setActiveTab('calendar')
    } catch (err) {
      console.error('Error generating calendar:', err)
      setError(err.message || 'Failed to generate calendar')
    } finally {
      setLoading(false)
    }
  }

  // Save current calendar to history
  const saveCurrentCalendar = async () => {
    if (!currentCalendar) return

    const savedCalendar = { ...currentCalendar, saved: true }
    setCurrentCalendar(savedCalendar)
    setIsCurrentSaved(true)

    if (isAuthenticated) {
      // Save to database
      const calendarData = {
        month: currentCalendar.month,
        platform: currentCalendar.platform,
        posts_per_week: currentCalendar.posts_per_week,
        total_posts: currentCalendar.total_posts,
        brand_analysis: currentCalendar.brand_analysis || '',
        strategy: currentCalendar.strategy || '',
        posts: currentCalendar.posts
      }

      if (currentCalendarId) {
        await api.updateCalendar(currentCalendarId, calendarData)
      } else {
        await api.saveCalendar(calendarData)
        // Reload to get the new calendar ID
        const current = await api.getCurrentCalendar()
        if (current) {
          setCurrentCalendarId(current.id)
        }
      }

      // Reload past calendars
      const calendars = await api.getCalendars()
      const past = calendars.filter(c => c.id !== currentCalendarId)
      setPastCalendars(past)
    } else {
      localStorage.setItem('currentCalendar', JSON.stringify(savedCalendar))
      
      // Add to past calendars if not already there
      const exists = pastCalendars.some(cal => cal.month === currentCalendar.month)
      if (!exists) {
        const updatedPast = [savedCalendar, ...pastCalendars].slice(0, 12)
        setPastCalendars(updatedPast)
        localStorage.setItem('pastCalendars', JSON.stringify(updatedPast))
      }
    }
  }

  // Update a single post
  const updatePost = async (index, newPost) => {
    const updatedCalendar = { ...currentCalendar }
    updatedCalendar.posts[index] = newPost
    setCurrentCalendar(updatedCalendar)

    if (isAuthenticated && currentCalendarId) {
      await api.updateCalendar(currentCalendarId, {
        month: updatedCalendar.month,
        platform: updatedCalendar.platform,
        posts_per_week: updatedCalendar.posts_per_week,
        total_posts: updatedCalendar.total_posts,
        brand_analysis: updatedCalendar.brand_analysis || '',
        strategy: updatedCalendar.strategy || '',
        posts: updatedCalendar.posts
      })
    } else {
      localStorage.setItem('currentCalendar', JSON.stringify(updatedCalendar))
    }
  }

  // Save and immediately start planning next month
  const saveAndPlanNext = () => {
    saveCurrentCalendar()
    setShowNewMonthSetup(true)
  }

  // Regenerate with optional feedback
  const regenerateCalendar = (feedback = '') => {
    const settings = {
      content_goals: companyProfile.content_goals,
      posts_per_week: currentCalendar?.posts_per_week || 3,
      monthly_promotions: currentCalendar?.monthly_context?.promotions || '',
      monthly_events: currentCalendar?.monthly_context?.events || '',
      monthly_focuses: currentCalendar?.monthly_context?.focuses || (feedback ? feedback : '')
    }
    generateCalendar(settings, feedback)
  }

  // Delete a past calendar
  const deletePastCalendar = (index) => {
    const updated = pastCalendars.filter((_, i) => i !== index)
    setPastCalendars(updated)
    if (!isAuthenticated) {
      localStorage.setItem('pastCalendars', JSON.stringify(updated))
    }
  }

  // View a past calendar
  const viewPastCalendar = (calendar) => {
    setCurrentCalendar(calendar)
    setCurrentCalendarId(calendar.id || null)
    setIsCurrentSaved(true)
    setActiveTab('calendar')
  }

  // Save insights
  const handleSaveInsights = async (insights) => {
    setIndustryInsights(insights)
    if (isAuthenticated) {
      await api.saveInsights({ industry_insights: insights.content })
    } else {
      localStorage.setItem('industryInsights', JSON.stringify(insights))
    }
  }

  // Save tips
  const handleSaveTips = async (tips) => {
    setPersonalizedTips(tips)
    if (isAuthenticated) {
      await api.saveInsights({ personalized_tips: tips.content })
    } else {
      localStorage.setItem('personalizedTips', JSON.stringify(tips))
    }
  }

  // Get current month display
  const getCurrentMonthDisplay = () => {
    return new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  }

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="app loading-screen">
        <div className="loading-content">
          <div className="spinner large"></div>
          <p>Loading Gridly ✨</p>
        </div>
      </div>
    )
  }

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <LoginPage onLoginSuccess={loadUserData} />
  }

  return (
    <div className="app">
      <Header user={user} onLogout={logout} />
      
      <nav className="tab-nav">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''} 
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={activeTab === 'calendar' ? 'active' : ''} 
          onClick={() => setActiveTab('calendar')}
        >
          {currentCalendar ? currentCalendar.month : 'Calendar'}
        </button>
        {pastCalendars.length > 0 && (
          <button 
            className={activeTab === 'history' ? 'active' : ''} 
            onClick={() => setActiveTab('history')}
          >
            Past Plans ({pastCalendars.length})
          </button>
        )}
        <button 
          className={activeTab === 'setup' ? 'active' : ''} 
          onClick={() => setActiveTab('setup')}
        >
          Settings
        </button>
        {!isSubscribed ? (
          <button 
            className={`upgrade-btn ${activeTab === 'pricing' ? 'active' : ''}`}
            onClick={() => setActiveTab('pricing')}
          >
            ⚡ Upgrade to Growth
          </button>
        ) : (
          <span className="pro-status">⚡ Growth Member</span>
        )}
      </nav>

      <main className="main-content">
        {error && (
          <div className="error-banner">
            <p>{error}</p>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {activeTab === 'dashboard' && (
          <Dashboard 
            companyProfile={companyProfile}
            calendar={currentCalendar}
            pastCalendarsCount={pastCalendars.length}
            onGenerateCalendar={() => setShowNewMonthSetup(true)}
            onSetupClick={() => setActiveTab('setup')}
            loading={loading}
            currentMonth={getCurrentMonthDisplay()}
            industryInsights={industryInsights}
            personalizedTips={personalizedTips}
            onSaveInsights={handleSaveInsights}
            onSaveTips={handleSaveTips}
            isSubscribed={isSubscribed}
            isGrowthPlan={isGrowthPlan}
            onUpgradeClick={() => setActiveTab('pricing')}
          />
        )}

        {activeTab === 'calendar' && (
          <ContentCalendar 
            calendar={currentCalendar}
            onRegenerate={regenerateCalendar}
            onSave={saveCurrentCalendar}
            onSaveAndNext={saveAndPlanNext}
            onUpdatePost={updatePost}
            loading={loading}
            isSaved={isCurrentSaved}
            companyProfile={companyProfile}
          />
        )}

        {activeTab === 'history' && (
          <PastCalendars 
            calendars={pastCalendars}
            onSelectCalendar={viewPastCalendar}
            onDeleteCalendar={deletePastCalendar}
          />
        )}

        {activeTab === 'setup' && (
          <CompanySetup 
            existingProfile={companyProfile}
            onSave={saveCompanyProfile}
          />
        )}

        {activeTab === 'pricing' && (
          <PricingPage 
            onSubscribed={() => setActiveTab('dashboard')}
          />
        )}
      </main>

      {/* New Month Setup Modal */}
      {showNewMonthSetup && !loading && (
        <NewMonthSetup
          companyProfile={companyProfile}
          onGenerate={generateCalendar}
          onCancel={() => setShowNewMonthSetup(false)}
          loading={loading}
        />
      )}

      {/* Generating Progress Overlay */}
      {loading && (
        <GeneratingProgress postsPerWeek={generatingPostsPerWeek} />
      )}
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
