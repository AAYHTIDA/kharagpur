import { useState } from 'react'

function EvidenceCard({ evidence }) {
  const [isExpanded, setIsExpanded] = useState(true)

  return (
    <div className="evidence-card">
      <div className="evidence-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h3>Evidence Summary</h3>
        <button className={`toggle-btn ${!isExpanded ? 'collapsed' : ''}`}>
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>
      <div className={`evidence-content ${isExpanded ? 'expanded' : 'collapsed'}`}>
        <ul>
          {evidence.map((item, index) => (
            <li key={index} className={`evidence-item ${item.supports ? 'supports' : 'contradicts'}`}>
              <div className="claim">{item.claim}</div>
              <div className="evidence">"{item.evidence}"</div>
              <span className={`tag ${item.supports ? 'supports' : 'contradicts'}`}>
                {item.supports ? 'Supports' : 'Contradicts'}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default EvidenceCard
