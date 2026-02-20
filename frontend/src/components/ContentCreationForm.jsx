import { useState } from 'react'

function ContentCreationForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState({
    brand_name: '',
    industry: '',
    target_audience: '',
    brand_values: '',
    brand_info: '',
    content_goals: '',
    platform: 'LinkedIn',
    post_frequency: '3 times per week',
    content_themes: '',
    post_topic: '',
    tone: 'professional',
    post_type: 'standard',
    include_cta: true,
  })

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <div className="form-card">
      <h2>Content Creation Workflow</h2>
      <p className="form-description">
        Fill in your brand information to generate a complete post through our AI workflow.
      </p>
      
      <form onSubmit={handleSubmit} className="content-form">
        <div className="form-section-title">Brand Information</div>
        
        <div className="form-group">
          <label htmlFor="brand_name">Brand Name *</label>
          <input
            type="text"
            id="brand_name"
            name="brand_name"
            value={formData.brand_name}
            onChange={handleChange}
            required
            placeholder="e.g., TechStart Inc"
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
            placeholder="e.g., SaaS, E-commerce, Healthcare"
          />
        </div>

        <div className="form-group">
          <label htmlFor="target_audience">Target Audience *</label>
          <input
            type="text"
            id="target_audience"
            name="target_audience"
            value={formData.target_audience}
            onChange={handleChange}
            required
            placeholder="e.g., Small business owners, Entrepreneurs"
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
            rows="3"
            placeholder="e.g., Innovation, Simplicity, Customer-first"
          />
        </div>

        <div className="form-group">
          <label htmlFor="brand_info">Brand Info / Description *</label>
          <textarea
            id="brand_info"
            name="brand_info"
            value={formData.brand_info}
            onChange={handleChange}
            required
            rows="3"
            placeholder="Brief description of your brand, products, or services"
          />
        </div>

        <div className="form-section-title">Content Strategy</div>

        <div className="form-group">
          <label htmlFor="content_goals">Content Goals *</label>
          <textarea
            id="content_goals"
            name="content_goals"
            value={formData.content_goals}
            onChange={handleChange}
            required
            rows="2"
            placeholder="e.g., Increase brand awareness, Drive sign-ups"
          />
        </div>

        <div className="form-group">
          <label htmlFor="platform">Platform *</label>
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
            <option value="TikTok">TikTok</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="post_frequency">Post Frequency</label>
          <input
            type="text"
            id="post_frequency"
            name="post_frequency"
            value={formData.post_frequency}
            onChange={handleChange}
            placeholder="e.g., 3 times per week"
          />
        </div>

        <div className="form-group">
          <label htmlFor="content_themes">Content Themes</label>
          <textarea
            id="content_themes"
            name="content_themes"
            value={formData.content_themes}
            onChange={handleChange}
            rows="2"
            placeholder="e.g., Product updates, Customer success stories"
          />
        </div>

        <div className="form-section-title">Post Details</div>

        <div className="form-group">
          <label htmlFor="post_topic">Post Topic *</label>
          <input
            type="text"
            id="post_topic"
            name="post_topic"
            value={formData.post_topic}
            onChange={handleChange}
            required
            placeholder="e.g., Announcing our new feature release"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="tone">Tone</label>
            <select
              id="tone"
              name="tone"
              value={formData.tone}
              onChange={handleChange}
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="friendly">Friendly</option>
              <option value="authoritative">Authoritative</option>
              <option value="conversational">Conversational</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="post_type">Post Type</label>
            <select
              id="post_type"
              name="post_type"
              value={formData.post_type}
              onChange={handleChange}
            >
              <option value="standard">Standard</option>
              <option value="announcement">Announcement</option>
              <option value="educational">Educational</option>
              <option value="promotional">Promotional</option>
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
            Include Call-to-Action
          </label>
        </div>

        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? 'Generating Content...' : 'Generate Content'}
        </button>
      </form>
    </div>
  )
}

export default ContentCreationForm
