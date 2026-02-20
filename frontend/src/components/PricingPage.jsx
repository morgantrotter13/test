import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { API_V1 } from '../config'

const API_BASE = API_V1

function PricingPage({ onSubscribed }) {
  const { token, user } = useAuth()
  const [loading, setLoading] = useState(null)
  const [error, setError] = useState('')

  const handleSubscribe = async () => {
    setLoading('growth')
    setError('')

    try {
      const response = await fetch(`${API_BASE}/payments/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          price_id: 'growth',
          success_url: `${window.location.origin}/?subscribed=true`,
          cancel_url: `${window.location.origin}/pricing`
        })
      })

      if (response.ok) {
        const data = await response.json()
        window.location.href = data.checkout_url
      } else {
        const err = await response.json()
        setError(err.detail || 'Failed to start checkout')
      }
    } catch (err) {
      console.error('Checkout error:', err)
      setError('Could not connect to payment server')
    } finally {
      setLoading(null)
    }
  }

  const handleManageSubscription = async () => {
    setLoading('manage')
    try {
      const response = await fetch(`${API_BASE}/payments/create-portal-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          return_url: window.location.href
        })
      })

      if (response.ok) {
        const data = await response.json()
        window.location.href = data.portal_url
      }
    } catch (err) {
      console.error('Portal error:', err)
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="billing-page">
      {/* Hero Section */}
      <div className="billing-hero">
        <div className="billing-hero-content">
          <span className="billing-badge">✦ Simple Pricing</span>
          <h1>Try it free. Grow when you're ready.</h1>
          <p>Generate 1 content plan on us. Upgrade to Growth for unlimited access.</p>
        </div>
        <div className="billing-hero-glow"></div>
      </div>

      {error && (
        <div className="billing-error">
          {error}
        </div>
      )}

      {/* Pricing Cards */}
      <div className="billing-cards">
        {/* Free */}
        <div className="billing-card">
          <div className="billing-card-header">
            <h3>Free</h3>
            <p className="plan-desc">See Gridly in action</p>
          </div>
          <div className="billing-price">
            <span className="currency">$</span>
            <span className="amount">0</span>
            <span className="period"></span>
          </div>
          <ul className="billing-features">
            <li><span className="check">✓</span> 1 AI-generated post</li>
            <li><span className="check">✓</span> Company profile setup</li>
            <li><span className="check">✓</span> Website analysis</li>
            <li className="disabled"><span className="x">—</span> Full monthly calendar</li>
            <li className="disabled"><span className="x">—</span> Industry insights</li>
            <li className="disabled"><span className="x">—</span> Personalized recommendations</li>
            <li className="disabled"><span className="x">—</span> Unlimited regenerations</li>
            <li className="disabled"><span className="x">—</span> Priority support</li>
          </ul>
          <button className="billing-btn secondary" disabled>
            ✓ Current Plan
          </button>
        </div>

        {/* Growth - Featured */}
        <div className="billing-card featured">
          <div className="featured-badge">
            <span>⚡ RECOMMENDED</span>
          </div>
          <div className="billing-card-header">
            <h3>Growth</h3>
            <p className="plan-desc">The full content system</p>
          </div>
          <div className="billing-price">
            <span className="currency">$</span>
            <span className="amount">99</span>
            <span className="period">/mo</span>
          </div>
          <ul className="billing-features">
            <li><span className="check">✓</span> <strong>Unlimited</strong> posts per month</li>
            <li><span className="check">✓</span> <strong>Unlimited</strong> content calendars</li>
            <li><span className="check">✓</span> Full monthly content planning</li>
            <li><span className="check">✓</span> Industry insights and research</li>
            <li><span className="check">✓</span> Personalized strategy recommendations</li>
            <li><span className="check">✓</span> Website analysis and brand voice</li>
            <li><span className="check">✓</span> Image direction for every post</li>
            <li><span className="check">✓</span> Unlimited regenerations</li>
            <li><span className="check">✓</span> Priority support</li>
          </ul>
          <button 
            className="billing-btn primary"
            onClick={handleSubscribe}
            disabled={loading === 'growth'}
          >
            {loading === 'growth' ? (
              <span className="btn-loading">
                <span className="spinner"></span>
                Processing...
              </span>
            ) : (
              <>⚡ Get Growth</>
            )}
          </button>
          <p className="billing-guarantee">✓ 14-day money-back guarantee</p>
        </div>
      </div>

      {/* Trust Badges */}
      <div className="billing-trust">
        <div className="trust-item">
          <span className="trust-icon">🔒</span>
          <span>Secure Payment</span>
        </div>
        <div className="trust-item">
          <span className="trust-icon">💳</span>
          <span>Powered by Stripe</span>
        </div>
        <div className="trust-item">
          <span className="trust-icon">✕</span>
          <span>Cancel Anytime</span>
        </div>
        <div className="trust-item">
          <span className="trust-icon">⚡</span>
          <span>Priority Support</span>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="billing-faq">
        <h2>Common Questions</h2>
        <div className="faq-grid">
          <div className="faq-item">
            <h4>Can I cancel my subscription?</h4>
            <p>Yes. Cancel anytime with one click. No questions asked, no hidden fees.</p>
          </div>
          <div className="faq-item">
            <h4>What do I get for free?</h4>
            <p>You can set up your company profile, analyze your website, and generate 1 AI-powered post to see the quality of Gridly's output.</p>
          </div>
          <div className="faq-item">
            <h4>What does Growth unlock?</h4>
            <p>Growth gives you unlimited content calendars, industry insights, personalized recommendations, and unlimited post regenerations — the full content system.</p>
          </div>
          <div className="faq-item">
            <h4>What payment methods do you accept?</h4>
            <p>All major credit cards through Stripe's secure payment infrastructure.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PricingPage
