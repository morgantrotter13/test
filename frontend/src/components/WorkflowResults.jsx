function WorkflowResults({ results }) {
  if (!results) return null

  // Handle different response structures
  const workflowResults = results.results || {}
  const { brand_analysis, strategy, post_generation } = workflowResults
  const finalOutput = results.final_output || post_generation?.output
  const finalRenderedPrompt = results.final_rendered_prompt || post_generation?.rendered_prompt

  return (
    <div className="results-card">
      <h2>Generated Content</h2>
      
      <div className="workflow-steps">
        <div className="step-result">
          <div className="step-header">
            <span className="step-number">1</span>
            <h3>Brand Analysis</h3>
          </div>
          <div className="step-content">
            <pre>{brand_analysis?.output || brand_analysis || 'No output - Step may have failed'}</pre>
          </div>
        </div>

        <div className="step-arrow">↓</div>

        <div className="step-result">
          <div className="step-header">
            <span className="step-number">2</span>
            <h3>Content Strategy</h3>
          </div>
          <div className="step-content">
            <pre>{strategy?.output || strategy || 'No output - Step may have failed'}</pre>
          </div>
        </div>

        <div className="step-arrow">↓</div>

        <div className="step-result highlight">
          <div className="step-header">
            <span className="step-number">3</span>
            <h3>Generated Post</h3>
          </div>
          <div className="step-content final-post">
            <pre>{post_generation?.output || 'No output'}</pre>
          </div>
          <button 
            className="copy-button"
            onClick={() => {
              const text = post_generation?.output || ''
              navigator.clipboard.writeText(text)
              alert('Copied to clipboard!')
            }}
          >
            Copy Post
          </button>
        </div>

        <div className="step-result">
          <div className="step-header">
            <span className="step-number">✓</span>
            <h3>Final Output</h3>
          </div>
          <div className="step-content final-post">
            <pre>{finalOutput || 'No output'}</pre>
          </div>
          {finalRenderedPrompt && (
            <div className="step-content" style={{ marginTop: '0.75rem' }}>
              <strong>Rendered Prompt Sent to LLM:</strong>
              <pre style={{ marginTop: '0.35rem' }}>{finalRenderedPrompt}</pre>
            </div>
          )}
          <button
            className="copy-button"
            onClick={() => {
              const text = finalOutput || ''
              navigator.clipboard.writeText(text)
              alert('Copied to clipboard!')
            }}
          >
            Copy Final Output
          </button>
        </div>
      </div>
    </div>
  )
}

export default WorkflowResults
