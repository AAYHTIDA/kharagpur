function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function FileInput({ label, status, onFileLoad, onStatusChange }) {
  const handleFileChange = async (e) => {
    const file = e.target.files[0]
    
    if (!file) {
      onStatusChange({ text: 'No file selected', type: '' })
      onFileLoad('', '')
      return
    }
    
    if (!file.name.match(/\.(txt|md)$/i)) {
      onStatusChange({ text: 'Please select a .txt or .md file', type: 'error' })
      onFileLoad('', '')
      return
    }
    
    if (file.size > 10 * 1024 * 1024) {
      onStatusChange({ text: 'File too large (max 10MB)', type: 'error' })
      onFileLoad('', '')
      return
    }
    
    onStatusChange({ text: 'Loading file...', type: '' })
    
    try {
      const content = await file.text()
      onFileLoad(content, file.name)
      onStatusChange({ text: `✓ ${file.name} (${formatFileSize(file.size)})`, type: 'loaded' })
    } catch (error) {
      onStatusChange({ text: 'Error reading file', type: 'error' })
      onFileLoad('', '')
    }
  }

  return (
    <div className="input-group">
      <label>{label}</label>
      <div className="file-input-wrapper">
        <input type="file" accept=".txt,.md" onChange={handleFileChange} />
        <div className={`file-status ${status.type}`}>{status.text}</div>
      </div>
    </div>
  )
}

export default FileInput
