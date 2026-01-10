function ResultsTable({ results }) {
  if (!results || results.length === 0) {
    return <div className="no-results">No results to display</div>
  }

  const downloadCSV = () => {
    // Create CSV headers
    const headers = ['id', 'book_name', 'char', 'caption', 'content', 'label']
    
    // Convert results to CSV format
    const csvContent = [
      headers.join(','),
      ...results.map(row => [
        row.id,
        `"${row.book_name.replace(/"/g, '""')}"`, // Escape quotes in book name
        `"${row.char.replace(/"/g, '""')}"`, // Escape quotes in character name
        `"${row.caption.replace(/"/g, '""')}"`, // Escape quotes in caption
        `"${row.content.replace(/"/g, '""')}"`, // Escape quotes in content
        row.label
      ].join(','))
    ].join('\n')

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    
    link.setAttribute('href', url)
    link.setAttribute('download', `lore_ledger_results_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="results-table-container">
      <div className="results-header">
        <h2>Consistency Results</h2>
        <button className="download-csv-btn" onClick={downloadCSV}>
          📥 Download CSV
        </button>
      </div>
      <table className="results-table">
        <thead>
          <tr>
            <th>id</th>
            <th>book_name</th>
            <th>char</th>
            <th>caption</th>
            <th>content</th>
            <th>label</th>
          </tr>
        </thead>
        <tbody>
          {results.map((row, index) => (
            <tr key={index} className={row.label === 'consistent' ? 'consistent-row' : 'contradict-row'}>
              <td>{row.id}</td>
              <td>{row.book_name}</td>
              <td>{row.char}</td>
              <td>{row.caption}</td>
              <td className="content-cell">{row.content}</td>
              <td className={`result-cell ${row.label}`}>
                {row.label}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default ResultsTable
