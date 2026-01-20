import { TOPIC_CATEGORIES, TOPIC_COLORS, DEFAULT_COLOR } from '../constants'
import DualRangeSlider from './DualRangeSlider'

export default function FilterPanel({
  filters,
  setFilters,
  cities,
  yearRange,
  viewRange,
  setViewRange,
  viewMode,
  setViewMode,
  topicCounts
}) {
  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  // Sort topics by count
  const sortedTopics = TOPIC_CATEGORIES
    .filter(t => topicCounts[t] > 0)
    .sort((a, b) => (topicCounts[b] || 0) - (topicCounts[a] || 0))

  return (
    <div className="filter-panel">
      <div className="filter-row">
        <div className="filter-group">
          <label>View Mode</label>
          <div className="view-mode-toggle">
            <button
              className={`mode-btn ${viewMode === 'all' ? 'active' : ''}`}
              onClick={() => setViewMode('all')}
            >
              All Cities
            </button>
            <button
              className={`mode-btn ${viewMode === 'by-city' ? 'active' : ''}`}
              onClick={() => setViewMode('by-city')}
            >
              By City
            </button>
          </div>
        </div>

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

      <div className="filter-group time-zoom">
        <label>Time Range (zoom view)</label>
        <DualRangeSlider
          min={yearRange.min}
          max={yearRange.max}
          valueStart={viewRange.start}
          valueEnd={viewRange.end}
          onChange={(range) => setViewRange(range)}
        />
      </div>
    </div>
  )
}
