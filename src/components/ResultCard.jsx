function ResultCard({ result }) {
  const isConsistent = result.prediction === 1

  return (
    <div className="result-card">
      <h2>Consistency Result</h2>
      <div className="result-status">
        <span className={`status-label ${isConsistent ? 'consistent' : 'inconsistent'}`}>
          {result.verdict}
        </span>
        <span className="prediction-text">
          Prediction: {result.prediction} ({isConsistent ? 'Consistent' : 'Inconsistent'})
        </span>
      </div>
    </div>
  )
}

export default ResultCard
