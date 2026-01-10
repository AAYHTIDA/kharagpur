import { useState } from 'react'
import FileInput from './components/FileInput'
import CsvInput from './components/CsvInput'
import ResultsTable from './components/ResultsTable'

const API_URL = 'http://localhost:8000'

function App() {
  const [novel1Content, setNovel1Content] = useState('')
  const [novel2Content, setNovel2Content] = useState('')
  const [novel1Status, setNovel1Status] = useState({ text: 'No file selected', type: '' })
  const [novel2Status, setNovel2Status] = useState({ text: 'No file selected', type: '' })
  const [novel1Name, setNovel1Name] = useState('')
  const [novel2Name, setNovel2Name] = useState('')
  const [csvData, setCsvData] = useState(null)
  const [csvStatus, setCsvStatus] = useState({ text: 'No file selected', type: '' })
  const [isChecking, setIsChecking] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const canCheck = novel1Content.trim().length > 0 && novel2Content.trim().length > 0 && csvData

  const handleCheckConsistency = async () => {
    if (!canCheck) return
    
    setIsChecking(true)
    setError(null)
    setResults(null)
    
    try {
      const response = await fetch(`${API_URL}/evaluate-csv`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          novel1_text: novel1Content,
          novel2_text: novel2Content,
          novel1_name: novel1Name || 'Novel 1',
          novel2_name: novel2Name || 'Novel 2',
          backstories: csvData
        })
      })
      
      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || 'Evaluation failed')
      }
      
      const data = await response.json()
      setResults(data.results)
    } catch (err) {
      setError(err.message || 'Failed to connect to server')
    } finally {
      setIsChecking(false)
    }
  }

  return (
    <div className="container">
      <header>
        <h1>Lore Ledger</h1>
        <p>Upload two novels and a CSV of backstories to check consistency</p>
      </header>

      <main>
        <section className="input-section">
          <FileInput
            label="Novel 1 Text File"
            status={novel1Status}
            onFileLoad={(content, name) => {
              setNovel1Content(content)
              setNovel1Name(name.replace(/\.[^/.]+$/, ''))
            }}
            onStatusChange={setNovel1Status}
          />
          <FileInput
            label="Novel 2 Text File"
            status={novel2Status}
            onFileLoad={(content, name) => {
              setNovel2Content(content)
              setNovel2Name(name.replace(/\.[^/.]+$/, ''))
            }}
            onStatusChange={setNovel2Status}
          />
          <CsvInput
            label="Backstories CSV File"
            status={csvStatus}
            onCsvLoad={setCsvData}
            onStatusChange={setCsvStatus}
          />
          <button
            className="check-button"
            disabled={!canCheck || isChecking}
            onClick={handleCheckConsistency}
          >
            {isChecking ? 'Analyzing... (this may take a while)' : 'Check Consistency'}
          </button>
          
          {error && (
            <div className="error-message">
              Error: {error}
            </div>
          )}
        </section>

        {results && (
          <section className="output-section">
            <ResultsTable results={results} />
          </section>
        )}
      </main>
    </div>
  )
}

export default App
