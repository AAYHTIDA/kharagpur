import { useState } from 'react'

function ReasoningCard({ reasoning }) {
  const [isExpanded, setIsExpanded] = useState(true)

  if (!reasoning) return null

  return (
    <div className="reasoning-card">
      <div className="reasoning-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h3>Structured Reasoning</h3>
        <button className={`toggle-btn ${!isExpanded ? 'collapsed' : ''}`}>
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>
      <div className={`reasoning-content ${isExpanded ? 'expanded' : 'collapsed'}`}>
        <div className="reasoning-item">
          <h4>Temporal Consistency</h4>
          <p>{reasoning.temporal_consistency}</p>
        </div>
        <div className="reasoning-item">
          <h4>Causal Reasoning</h4>
          <p>{reasoning.causal_reasoning}</p>
        </div>
        <div className="reasoning-item">
          <h4>Narrative Constraints</h4>
          <p>{reasoning.narrative_constraints}</p>
        </div>
      </div>
    </div>
  )
}

export default ReasoningCard
