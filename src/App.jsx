import { useState } from 'react'
import FileInput from './components/FileInput'
import ResultCard from './components/ResultCard'
import EvidenceCard from './components/EvidenceCard'
import ReasoningCard from './components/ReasoningCard'

const API_URL = 'http://localhost:8000'

function App() {
  const [novelContent, setNovelContent] = useState('')
  const [backstoryContent, setBackstoryContent] = useState('')
  const [novelStatus, setNovelStatus] = useState({ text: 'No file selected', type: '' })
  const [backstoryStatus, setBackstoryStatus] = useState({ text: 'No file selected', type: '' })
  const [isChecking, setIsChecking] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const canCheck = novelContent.trim().length > 0 && backstoryContent.trim().length > 0

  const handleCheckConsistency = async () => {
    if (!canCheck) return
    
    setIsChecking(true)
    setError(null)
    setResult(null)
    
    try {
      const response = await fetch(`${API_URL}/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          novel_text: novelContent,
          backstory: backstoryContent
        })
      })
      
      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || 'Evaluation failed')
      }
      
      const data = await response.json()
      
      // Transform response to match frontend expectations
      setResult({
        consistent: data.verdict === 'CONSISTENT',
        verdict: data.verdict,
        prediction: data.prediction,
        reasoning: data.reasoning,
        evidence: data.evidence,
        constraints: data.aggregated_constraints
      })
    } catch (err) {
      setError(err.message || 'Failed to connect to server')
    } finally {
      setIsChecking(false)
    }
  }

  return (
    <div className="container">
      <header>
        <h1>Narrative Consistency Checker</h1>
        <p>Check if a character backstory is logically consistent with a novel</p>
      </header>

      <main>
        <section className="input-section">
          <FileInput
            label="Novel Text File"
            status={novelStatus}
            onFileLoad={(content) => setNovelContent(content)}
            onStatusChange={setNovelStatus}
          />
          <FileInput
            label="Hypothetical Backstory File"
            status={backstoryStatus}
            onFileLoad={(content) => setBackstoryContent(content)}
            onStatusChange={setBackstoryStatus}
          />
          <button
            className="check-button"
            disabled={!canCheck || isChecking}
            onClick={handleCheckConsistency}
          >
            {isChecking ? 'Analyzing novel... (this may take a while)' : 'Check Consistency'}
          </button>
          
          {error && (
            <div className="error-message">
              Error: {error}
            </div>
          )}
        </section>

        {result && (
          <section className="output-section">
            <ResultCard result={result} />
            <ReasoningCard reasoning={result.reasoning} />
            <EvidenceCard evidence={result.evidence} />
          </section>
        )}
      </main>
    </div>
  )
}

export default App
