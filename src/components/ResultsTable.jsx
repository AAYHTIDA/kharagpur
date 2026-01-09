function ResultsTable({ results }) {
  if (!results || results.length === 0) {
    return <div className="no-results">No results to display</div>
  }

  return (
    <div className="results-table-container">
      <h2>Consistency Results</h2>
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
