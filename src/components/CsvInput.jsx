import { useRef } from 'react'

function CsvInput({ label, status, onCsvLoad, onStatusChange }) {
  const fileInputRef = useRef(null)

  const parseCSV = (text) => {
    const lines = text.trim().split('\n')
    if (lines.length < 2) return []
    
    // Parse header
    const header = lines[0].split(',').map(h => h.trim().toLowerCase())
    
    // Expected columns: id, book_name, char, caption, content
    const idIdx = header.findIndex(h => h === 'id')
    const bookIdx = header.findIndex(h => h === 'book_name' || h === 'book')
    const charIdx = header.findIndex(h => h === 'char' || h === 'character')
    const captionIdx = header.findIndex(h => h === 'caption')
    const contentIdx = header.findIndex(h => h === 'content' || h === 'backstory')
    
    const rows = []
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim()
      if (!line) continue
      
      // Handle CSV with quoted fields
      const values = parseCSVLine(line)
      
      rows.push({
        id: idIdx >= 0 ? values[idIdx] : String(i),
        book_name: bookIdx >= 0 ? values[bookIdx] : '',
        character: charIdx >= 0 ? values[charIdx] : '',
        caption: captionIdx >= 0 ? values[captionIdx] : '',
        content: contentIdx >= 0 ? values[contentIdx] : values[values.length - 1] || ''
      })
    }
    return rows
  }

  const parseCSVLine = (line) => {
    const result = []
    let current = ''
    let inQuotes = false
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i]
      if (char === '"') {
        inQuotes = !inQuotes
      } else if (char === ',' && !inQuotes) {
        result.push(current.trim())
        current = ''
      } else {
        current += char
      }
    }
    result.push(current.trim())
    return result
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (!file) {
      onStatusChange({ text: 'No file selected', type: '' })
      onCsvLoad(null)
      return
    }

    if (!file.name.endsWith('.csv')) {
      onStatusChange({ text: 'Please select a CSV file', type: 'error' })
      onCsvLoad(null)
      return
    }

    const reader = new FileReader()
    reader.onload = (event) => {
      try {
        const text = event.target.result
        const data = parseCSV(text)
        if (data.length === 0) {
          onStatusChange({ text: 'CSV file is empty or invalid', type: 'error' })
          onCsvLoad(null)
        } else {
          onStatusChange({ text: `Loaded ${data.length} backstories from ${file.name}`, type: 'loaded' })
          onCsvLoad(data)
        }
      } catch (err) {
        onStatusChange({ text: `Error parsing CSV: ${err.message}`, type: 'error' })
        onCsvLoad(null)
      }
    }
    reader.onerror = () => {
      onStatusChange({ text: 'Error reading file', type: 'error' })
      onCsvLoad(null)
    }
    reader.readAsText(file)
  }

  return (
    <div className="input-group">
      <label>{label}</label>
      <div className="file-input-wrapper">
        <input
          type="file"
          ref={fileInputRef}
          accept=".csv"
          onChange={handleFileChange}
        />
      </div>
      <div className={`file-status ${status.type}`}>
        {status.text}
      </div>
      <div className="csv-format-hint">
        Expected columns: id, book_name, char, caption, content
      </div>
    </div>
  )
}

export default CsvInput
