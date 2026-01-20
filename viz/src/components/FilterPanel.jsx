import { TOPIC_CATEGORIES, TOPIC_COLORS, DEFAULT_COLOR } from '../constants'

export default function FilterPanel({ filters, setFilters, cities, yearRange, topicCounts }) {
  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  // Generate year buttons
  const years = []
  for (let y = yearRange.min; y <= yearRange.max; y++) {
    years.push(y)
  }

  // Sort topics by count
  const sortedTopics = TOPIC_CATEGORIES
    .filter(t => topicCounts[t] > 0)
    .sort((a, b) => (topicCounts[b] || 0) - (topicCounts[a] || 0))

  const isYearInRange = (year) => year >= filters.yearStart && year <= filters.yearEnd

  const toggleYear = (year) => {
    // If clicking on the only selected year, reset to all
    if (filters.yearStart === year && filters.yearEnd === year) {
      setFilters(prev => ({ ...prev, yearStart: yearRange.min, yearEnd: yearRange.max }))
      return
    }

    // If all years selected, select just this year
    if (filters.yearStart === yearRange.min && filters.yearEnd === yearRange.max) {
      setFilters(prev => ({ ...prev, yearStart: year, yearEnd: year }))
      return
    }

    // Extend or shrink range
    if (year < filters.yearStart) {
      setFilters(prev => ({ ...prev, yearStart: year }))
    } else if (year > filters.yearEnd) {
      setFilters(prev => ({ ...prev, yearEnd: year }))
    } else {
      // Click within range - set single year
      setFilters(prev => ({ ...prev, yearStart: year, yearEnd: year }))
    }
  }

  const selectAllYears = () => {
    setFilters(prev => ({ ...prev, yearStart: yearRange.min, yearEnd: yearRange.max }))
  }

  return (
    <div className="filter-panel">
      <div className="filter-row">
        <div className="filter-group">
          <label>Topic Category</label>
          <select
            value={filters.topic}
            onChange={(e) => updateFilter('topic', e.target.value)}
            style={{
              borderLeft: filters.topic ? `4px solid ${TOPIC_COLORS[filters.topic] || DEFAULT_COLOR}` : undefined
            }}
          >
            <option value="">All Topics</option>
            {sortedTopics.map(topic => (
              <option key={topic} value={topic}>
                {topic} ({(topicCounts[topic] || 0).toLocaleString()})
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>City</label>
          <select
            value={filters.city}
            onChange={(e) => updateFilter('city', e.target.value)}
          >
            <option value="">All Cities ({cities.length})</option>
            {cities.map(city => (
              <option key={city} value={city}>{city}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="filter-group year-filter">
        <div className="year-header">
          <label>
            Years: {filters.yearStart === filters.yearEnd
              ? filters.yearStart
              : `${filters.yearStart}–${filters.yearEnd}`}
          </label>
          {(filters.yearStart !== yearRange.min || filters.yearEnd !== yearRange.max) && (
            <button className="reset-btn" onClick={selectAllYears}>
              Show all
            </button>
          )}
        </div>
        <div className="year-buttons">
          {years.map(year => (
            <button
              key={year}
              className={`year-btn ${isYearInRange(year) ? 'active' : ''}`}
              onClick={() => toggleYear(year)}
            >
              {year.toString().slice(-2)}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
