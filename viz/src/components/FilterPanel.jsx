export default function FilterPanel({ filters, setFilters, cities, yearRange, stats }) {
  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  return (
    <div className="filter-panel">
      <div className="filter-group">
        <label>View</label>
        <div className="view-toggle">
          <button
            className={filters.viewMode === 'timeline' ? 'active' : ''}
            onClick={() => updateFilter('viewMode', 'timeline')}
          >
            Timeline
          </button>
          <button
            className={filters.viewMode === 'city' ? 'active' : ''}
            onClick={() => updateFilter('viewMode', 'city')}
          >
            By City
          </button>
        </div>
      </div>

      <div className="filter-group">
        <label htmlFor="city-filter">City</label>
        <select
          id="city-filter"
          value={filters.city}
          onChange={(e) => updateFilter('city', e.target.value)}
        >
          <option value="">All Cities ({cities.length})</option>
          {cities.map(city => (
            <option key={city} value={city}>{city}</option>
          ))}
        </select>
      </div>

      <div className="filter-group year-filter">
        <label>Years: {filters.yearStart} - {filters.yearEnd}</label>
        <div className="range-inputs">
          <input
            type="range"
            min={yearRange.min}
            max={yearRange.max}
            value={filters.yearStart}
            onChange={(e) => updateFilter('yearStart', Math.min(+e.target.value, filters.yearEnd))}
          />
          <input
            type="range"
            min={yearRange.min}
            max={yearRange.max}
            value={filters.yearEnd}
            onChange={(e) => updateFilter('yearEnd', Math.max(+e.target.value, filters.yearStart))}
          />
        </div>
      </div>

      <div className="filter-group">
        <label htmlFor="search">Search Topics</label>
        <input
          type="text"
          id="search"
          placeholder="e.g. climate, COVID, peace..."
          value={filters.search}
          onChange={(e) => updateFilter('search', e.target.value)}
        />
      </div>

      <div className="stats-badge">
        <span className="count">{stats.filtered.toLocaleString()}</span>
        <span className="label">events</span>
      </div>
    </div>
  )
}
