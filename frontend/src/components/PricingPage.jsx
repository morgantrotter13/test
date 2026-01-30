import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { API_V1 } from '../config'

const API_BASE = API_V1

function PricingPage({ onSubscribed }) {
  const { token, user } = useAuth()
  const [loading, setLoading] = useState(null)
  const [error, setError] = useState('')

  const handleSubscribe = async (plan) => {
    setLoading(plan)
    setError('')

    try {
      const response = await fetch(`${API_BASE}/payments/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          price_id: plan,
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
          <span className="billing-badge">✨ Launch Pricing</span>
          <h1>Supercharge Your Social Media</h1>
          <p>AI-powered content that converts. Cancel anytime.</p>
        </div>
        <div className="billing-hero-glow"></div>
      </div>

      {error && (
        <div className="billing-error">
          <span>⚠️</span> {error}
        </div>
      )}


      {/* Pricing Cards */}
      <div className="billing-cards">
        {/* Starter */}
        <div className="billing-card">
          <div className="billing-card-header">
            <span className="plan-icon">🌱</span>
            <h3>Starter</h3>
            <p className="plan-desc">Try it out</p>
          </div>
          <div className="billing-price">
            <span className="currency">$</span>
            <span className="amount">29</span>
            <span className="cents">.99</span>
            <span className="period">/mo</span>
          </div>
          <ul className="billing-features">
            <li><span className="check">✓</span> 4 AI-generated posts per month</li>
            <li><span className="check">✓</span> Image ideas for each post</li>
            <li><span className="check">✓</span> Caption optimization</li>
            <li className="disabled"><span className="x">✗</span> Full monthly calendar</li>
            <li className="disabled"><span className="x">✗</span> Industry insights</li>
            <li className="disabled"><span className="x">✗</span> Personalized tips</li>
            <li className="disabled"><span className="x">✗</span> Unlimited regenerations</li>
          </ul>
          <button 
            className="billing-btn secondary"
            onClick={() => handleSubscribe('starter')}
            disabled={loading === 'starter'}
          >
            {loading === 'starter' ? 'Processing...' : 'Get Started'}
          </button>
        </div>

        {/* Pro - Featured */}
        <div className="billing-card featured">
          <div className="featured-badge">
            <span>🔥 BEST VALUE</span>
          </div>
          <div className="billing-card-header">
            <span className="plan-icon">⚡</span>
            <h3>Pro</h3>
            <p className="plan-desc">For growing businesses</p>
          </div>
          <div className="billing-price">
            <span className="currency">$</span>
            <span className="amount">99</span>
            <span className="cents">.99</span>
            <span className="period">/mo</span>
          </div>
          <ul className="billing-features">
            <li><span className="check">✓</span> <strong>Unlimited</strong> posts per month</li>
            <li><span className="check">✓</span> <strong>Unlimited</strong> content calendars</li>
            <li><span className="check">✓</span> Full monthly content planning</li>
            <li><span className="check">✓</span> Industry insights & research</li>
            <li><span className="check">✓</span> Personalized strategy tips</li>
            <li><span className="check">✓</span> Website analysis & brand voice</li>
            <li><span className="check">✓</span> Image ideas for every post</li>
            <li><span className="check">✓</span> Unlimited regenerations</li>
            <li><span className="check">✓</span> Priority support</li>
          </ul>
          <button 
            className="billing-btn primary"
            onClick={() => handleSubscribe('monthly')}
            disabled={loading === 'monthly'}
          >
            {loading === 'monthly' ? (
              <span className="btn-loading">
                <span className="spinner"></span>
                Processing...
              </span>
            ) : (
              <>Get Pro</>
            )}
          </button>
          <p className="billing-guarantee">✓ 14-day money-back guarantee</p>
        </div>

        {/* Enterprise */}
        <div className="billing-card">
          <div className="billing-card-header">
            <span className="plan-icon">🏢</span>
            <h3>Enterprise</h3>
            <p className="plan-desc">For teams & agencies</p>
          </div>
          <div className="billing-price custom">
            <span className="amount">Custom</span>
          </div>
          <ul className="billing-features">
            <li><span className="check">✓</span> Everything in Pro</li>
            <li><span className="check">✓</span> Multi-brand management</li>
            <li><span className="check">✓</span> Team collaboration</li>
            <li><span className="check">✓</span> API access</li>
            <li><span className="check">✓</span> Dedicated account manager</li>
            <li><span className="check">✓</span> Custom integrations</li>
          </ul>
          <button className="billing-btn outline">
            Contact Sales
          </button>
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
          <span className="trust-icon">🚫</span>
          <span>Cancel Anytime</span>
        </div>
        <div className="trust-item">
          <span className="trust-icon">💬</span>
          <span>24/7 Support</span>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="billing-faq">
        <h2>Frequently Asked Questions</h2>
        <div className="faq-grid">
          <div className="faq-item">
            <h4>Can I cancel my subscription?</h4>
            <p>Yes! Cancel anytime with one click. No questions asked, no hidden fees.</p>
          </div>
          <div className="faq-item">
            <h4>What's the difference between Starter and Pro?</h4>
            <p>Starter gives you 4 posts/month to test it out. Pro unlocks unlimited posts, industry insights, and personalized tips.</p>
          </div>
          <div className="faq-item">
            <h4>Can I upgrade later?</h4>
            <p>Absolutely! Start with Starter to try the quality, then upgrade to Pro when you're ready for more.</p>
          </div>
          <div className="faq-item">
            <h4>What payment methods do you accept?</h4>
            <p>We accept all major credit cards through Stripe's secure payment system.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PricingPage
