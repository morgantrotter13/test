import { useState, useEffect } from 'react'

function GeneratingProgress({ postsPerWeek }) {
  const [currentStep, setCurrentStep] = useState(0)
  const [dots, setDots] = useState('')
  
  const steps = [
    { icon: '🔍', text: 'Analyzing your brand', duration: 8000 },
    { icon: '📋', text: 'Developing content strategy', duration: 8000 },
    { icon: '🎯', text: 'Generating post topics', duration: 5000 },
    { icon: '✍️', text: `Writing ${postsPerWeek * 4} posts`, duration: 60000 },
    { icon: '🖼️', text: 'Adding image direction', duration: 5000 },
    { icon: '✅', text: 'Finalizing calendar', duration: 3000 }
  ]

  // Animate dots
  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.')
    }, 500)
    return () => clearInterval(interval)
  }, [])

  // Progress through steps
  useEffect(() => {
    if (currentStep >= steps.length) return
    
    const timer = setTimeout(() => {
      if (currentStep < steps.length - 1) {
        setCurrentStep(prev => prev + 1)
      }
    }, steps[currentStep].duration)
    
    return () => clearTimeout(timer)
  }, [currentStep, steps.length])

  return (
    <div className="generating-progress">
      <div className="progress-card">
        <div className="progress-header">
          <div className="spinner"></div>
          <h2>✨ Building Your Content Plan</h2>
        </div>
        
        <p className="progress-subtitle">
          Gridly is creating personalized posts for your business. This typically takes 1-2 minutes.
        </p>

        <div className="progress-steps">
          {steps.map((step, index) => (
            <div 
              key={index} 
              className={`progress-step ${index < currentStep ? 'completed' : ''} ${index === currentStep ? 'active' : ''}`}
            >
              <span className="step-icon">
                {index < currentStep ? '✓' : step.icon}
              </span>
              <span className="step-text">
                {step.text}
                {index === currentStep && dots}
              </span>
            </div>
          ))}
        </div>

        <div className="progress-tip">
          <strong>💡 While you wait:</strong> Think about any upcoming promotions or events you'd like to feature next month.
        </div>
      </div>
    </div>
  )
}

export default GeneratingProgress
