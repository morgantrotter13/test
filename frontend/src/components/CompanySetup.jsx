import { useState, useEffect } from 'react'
import { API_V1 } from '../config'

function CompanySetup({ existingProfile, onSave }) {
  const [step, setStep] = useState(existingProfile ? 'edit' : 'start')
  const [websiteUrl, setWebsiteUrl] = useState('')
  const [scraping, setScraping] = useState(false)
  const [formData, setFormData] = useState({
    brand_name: '',
    website_url: '',
    industry: '',
    target_audience: '',
    brand_values: '',
    brand_info: '',
    content_goals: '',
    platform: 'Instagram',
    tone: 'professional',
    include_cta: true,
    website_summary: ''
  })

  useEffect(() => {
    if (existingProfile) {
      setFormData(existingProfile)
      setStep('edit')
    }
  }, [existingProfile])

  const [error, setError] = useState('')

  const handleAnalyzeWebsite = async () => {
    if (!websiteUrl) return
    
    setScraping(true)
    setError('')
    
    try {
      console.log('Analyzing website:', websiteUrl)
      const response = await fetch(`${API_V1}/content/scrape-website`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: websiteUrl })
      })
      
      console.log('Response status:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log('Scrape response:', data)
        
        if (data.scraped_successfully && data.inferred_profile) {
          console.log('Inferred profile:', data.inferred_profile)
          // Auto-fill form with inferred data
          setFormData(prev => ({
            ...prev,
            website_url: websiteUrl,
            website_summary: data.summary || '',
            brand_name: data.inferred_profile.brand_name || prev.brand_name,
            industry: data.inferred_profile.industry || prev.industry,
            brand_info: data.inferred_profile.brand_info || prev.brand_info,
            target_audience: data.inferred_profile.target_audience || prev.target_audience,
            brand_values: data.inferred_profile.brand_values || prev.brand_values,
            content_goals: data.inferred_profile.content_goals || prev.content_goals,
            tone: data.inferred_profile.tone || prev.tone
          }))
          setStep('review')
        } else {
          // Website couldn't be scraped, go to manual entry
          console.log('Scrape failed or no profile inferred')
          setError('Could not analyze website. Please enter details manually.')
          setFormData(prev => ({ ...prev, website_url: websiteUrl }))
          setStep('edit')
        }
      } else {
        const errorText = await response.text()
        console.error('Server error:', errorText)
        setError(`Server error: ${response.status}. Make sure backend is running.`)
      }
    } catch (err) {
      console.error('Error analyzing website:', err)
      setError('Could not connect to server. Make sure the backend is running on port 8000.')
      setFormData(prev => ({ ...prev, website_url: websiteUrl }))
    } finally {
      setScraping(false)
    }
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSave(formData)
  }

  const handleSkipToManual = () => {
    setStep('edit')
  }

  // Step 1: Just enter website
  if (step === 'start') {
    return (
      <div className="setup-container">
        <div className="setup-card setup-start">
          <div className="setup-icon">🌐</div>
          <h2>Let's Get Started</h2>
          <p className="setup-description">
            Enter your website URL and we'll automatically learn about your business 
            to create personalized social media content.
          </p>

          <div className="website-input-container">
            <input
              type="text"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              placeholder="www.yourbusiness.com"
              className="website-input"
              onKeyDown={(e) => e.key === 'Enter' && handleAnalyzeWebsite()}
            />
            <button 
              className="analyze-button"
              onClick={handleAnalyzeWebsite}
              disabled={!websiteUrl || scraping}
            >
              {scraping ? (
                <>
                  <span className="spinner"></span>
                  Analyzing...
                </>
              ) : (
                <>🔍 Analyze My Website</>
              )}
            </button>
          </div>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          <button className="skip-link" onClick={handleSkipToManual}>
            I don't have a website - enter details manually
          </button>
        </div>
      </div>
    )
  }

  // Step 2: Review inferred data
  if (step === 'review') {
    return (
      <div className="setup-container">
        <div className="setup-card">
          <div className="review-header">
            <span className="success-icon">✓</span>
            <h2>We Found Your Business!</h2>
            <p className="setup-description">
              Here's what we learned from your website. Review and edit anything that needs adjustment.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="setup-form">
            <div className="inferred-data-section">
              <div className="form-group">
                <label htmlFor="brand_name">Company Name</label>
                <input
                  type="text"
                  id="brand_name"
                  name="brand_name"
                  value={formData.brand_name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="industry">Industry</label>
                <input
                  type="text"
                  id="industry"
                  name="industry"
                  value={formData.industry}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="brand_info">About Your Business</label>
                <textarea
                  id="brand_info"
                  name="brand_info"
                  value={formData.brand_info}
                  onChange={handleChange}
                  required
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label htmlFor="target_audience">Target Audience</label>
                <textarea
                  id="target_audience"
                  name="target_audience"
                  value={formData.target_audience}
                  onChange={handleChange}
                  required
                  rows="2"
                />
              </div>

              <div className="form-group">
                <label htmlFor="brand_values">Brand Values</label>
                <textarea
                  id="brand_values"
                  name="brand_values"
                  value={formData.brand_values}
                  onChange={handleChange}
                  required
                  rows="2"
                />
              </div>

              <div className="form-group">
                <label htmlFor="content_goals">Social Media Goals</label>
                <textarea
                  id="content_goals"
                  name="content_goals"
                  value={formData.content_goals}
                  onChange={handleChange}
                  required
                  rows="2"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="platform">Primary Platform</label>
                  <select
                    id="platform"
                    name="platform"
                    value={formData.platform}
                    onChange={handleChange}
                    required
                  >
                    <option value="Instagram">Instagram</option>
                    <option value="Facebook">Facebook</option>
                    <option value="LinkedIn">LinkedIn</option>
                    <option value="Twitter">Twitter/X</option>
                    <option value="TikTok">TikTok</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="tone">Brand Voice</label>
                  <select
                    id="tone"
                    name="tone"
                    value={formData.tone}
                    onChange={handleChange}
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual & Friendly</option>
                    <option value="playful">Playful & Fun</option>
                    <option value="authoritative">Authoritative</option>
                    <option value="inspirational">Inspirational</option>
                    <option value="educational">Educational</option>
                  </select>
                </div>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="include_cta"
                    checked={formData.include_cta}
                    onChange={handleChange}
                  />
                  Include call-to-action in posts
                </label>
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="primary-button">
                ✓ Looks Good - Save Profile
              </button>
            </div>
          </form>
        </div>
      </div>
    )
  }

  // Step 3: Full edit mode (manual entry or editing existing)
  return (
    <div className="setup-container">
      <div className="setup-card">
        <h2>🏢 Company Profile</h2>
        <p className="setup-description">
          {existingProfile 
            ? "Update your company details below."
            : "Tell us about your business to create personalized content."}
        </p>

        <form onSubmit={handleSubmit} className="setup-form">
          <div className="form-section">
            <h3>Basic Information</h3>
            
            <div className="form-group">
              <label htmlFor="brand_name">Company / Brand Name *</label>
              <input
                type="text"
                id="brand_name"
                name="brand_name"
                value={formData.brand_name}
                onChange={handleChange}
                required
                placeholder="e.g., Sunrise Bakery"
              />
            </div>

            <div className="form-group">
              <label htmlFor="website_url">Website URL (optional)</label>
              <input
                type="text"
                id="website_url"
                name="website_url"
                value={formData.website_url}
                onChange={handleChange}
                placeholder="e.g., www.sunrisebakery.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="industry">Industry *</label>
              <input
                type="text"
                id="industry"
                name="industry"
                value={formData.industry}
                onChange={handleChange}
                required
                placeholder="e.g., Food & Beverage, Local Bakery"
              />
            </div>

            <div className="form-group">
              <label htmlFor="brand_info">About Your Business *</label>
              <textarea
                id="brand_info"
                name="brand_info"
                value={formData.brand_info}
                onChange={handleChange}
                required
                rows="3"
                placeholder="What do you do? What makes you unique? What products/services do you offer?"
              />
            </div>
          </div>

          <div className="form-section">
            <h3>Target Audience</h3>
            
            <div className="form-group">
              <label htmlFor="target_audience">Who is your ideal customer? *</label>
              <textarea
                id="target_audience"
                name="target_audience"
                value={formData.target_audience}
                onChange={handleChange}
                required
                rows="2"
                placeholder="e.g., Local families, health-conscious millennials, busy professionals"
              />
            </div>

            <div className="form-group">
              <label htmlFor="brand_values">Brand Values *</label>
              <textarea
                id="brand_values"
                name="brand_values"
                value={formData.brand_values}
                onChange={handleChange}
                required
                rows="2"
                placeholder="e.g., Quality ingredients, community connection, sustainability"
              />
            </div>
          </div>

          <div className="form-section">
            <h3>Content Preferences</h3>

            <div className="form-group">
              <label htmlFor="content_goals">What do you want to achieve with social media? *</label>
              <textarea
                id="content_goals"
                name="content_goals"
                value={formData.content_goals}
                onChange={handleChange}
                required
                rows="2"
                placeholder="e.g., Increase foot traffic, build brand awareness, promote new products"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="platform">Primary Platform *</label>
                <select
                  id="platform"
                  name="platform"
                  value={formData.platform}
                  onChange={handleChange}
                  required
                >
                  <option value="Instagram">Instagram</option>
                  <option value="Facebook">Facebook</option>
                  <option value="LinkedIn">LinkedIn</option>
                  <option value="Twitter">Twitter/X</option>
                  <option value="TikTok">TikTok</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="tone">Brand Voice / Tone</label>
                <select
                  id="tone"
                  name="tone"
                  value={formData.tone}
                  onChange={handleChange}
                >
                  <option value="professional">Professional</option>
                  <option value="casual">Casual & Friendly</option>
                  <option value="playful">Playful & Fun</option>
                  <option value="authoritative">Authoritative</option>
                  <option value="inspirational">Inspirational</option>
                  <option value="educational">Educational</option>
                </select>
              </div>
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="include_cta"
                  checked={formData.include_cta}
                  onChange={handleChange}
                />
                Include call-to-action in posts (recommended)
              </label>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="primary-button">
              💾 Save Company Profile
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CompanySetup
