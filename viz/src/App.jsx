import { useState, useEffect, useMemo } from 'react'
import * as d3 from 'd3'
import BubbleChart from './components/BubbleChart'
import FilterPanel from './components/FilterPanel'
import Sidebar from './components/Sidebar'
import './App.css'

function App() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    city: '',
    yearStart: 2012,
    yearEnd: 2024,
    search: '',
    viewMode: 'timeline' // 'timeline', 'city', 'topic'
  })
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [hoveredEvent, setHoveredEvent] = useState(null)

  // Load data on mount
  useEffect(() => {
    d3.csv(import.meta.env.BASE_URL + 'data.csv').then(rawData => {
      const parsed = rawData.map((d, i) => ({
        id: i,
        region: d.region,
        city: d.city,
        date: new Date(d.date),
        year: new Date(d.date).getFullYear(),
        month: new Date(d.date).getMonth(),
        organizer: d.organizer || null,
        topic: d.topic || 'Unknown',
        participants_registered: d.participants_registered ? +d.participants_registered : null,
        participants_actual: d.participants_actual ? +d.participants_actual : null
      })).filter(d => !isNaN(d.date.getTime()))

      setData(parsed)
      setLoading(false)
    })
  }, [])

  // Filter data based on current filters
  const filteredData = useMemo(() => {
    return data.filter(d => {
      if (filters.city && d.city !== filters.city) return false
      if (d.year < filters.yearStart || d.year > filters.yearEnd) return false
      if (filters.search && !d.topic?.toLowerCase().includes(filters.search.toLowerCase())) return false
      return true
    })
  }, [data, filters])

  // Get unique cities for filter
  const cities = useMemo(() => {
    return [...new Set(data.map(d => d.city))].sort()
  }, [data])

  // Get year range from data
  const yearRange = useMemo(() => {
    if (data.length === 0) return { min: 2012, max: 2024 }
    const years = data.map(d => d.year).filter(y => !isNaN(y))
    return {
      min: Math.min(...years),
      max: Math.max(...years)
    }
  }, [data])

  // Stats
  const stats = useMemo(() => ({
    total: data.length,
    filtered: filteredData.length,
    cities: cities.length,
    yearRange: `${yearRange.min}-${yearRange.max}`
  }), [data, filteredData, cities, yearRange])

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading 70,000+ protest events...</p>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <h1>German Protest Registrations</h1>
        <p className="subtitle">
          Interactive visualization of {stats.total.toLocaleString()} demonstrations across {stats.cities} cities ({stats.yearRange})
        </p>
      </header>

      <FilterPanel
        filters={filters}
        setFilters={setFilters}
        cities={cities}
        yearRange={yearRange}
        stats={stats}
      />

      <main className="main">
        <BubbleChart
          data={filteredData}
          viewMode={filters.viewMode}
          onSelect={setSelectedEvent}
          onHover={setHoveredEvent}
          hoveredEvent={hoveredEvent}
        />
        <Sidebar
          selectedEvent={selectedEvent}
          hoveredEvent={hoveredEvent}
          stats={stats}
        />
      </main>

      <footer className="footer">
        <p>
          Data compiled from <a href="https://fragdenstaat.de" target="_blank" rel="noopener noreferrer">FragDenStaat</a> Freedom of Information requests.
          <a href="https://github.com/davidpomerenke/german-protest-registrations" target="_blank" rel="noopener noreferrer">View on GitHub</a> |
          <a href="https://zenodo.org/records/10094245" target="_blank" rel="noopener noreferrer">Dataset (Zenodo)</a>
        </p>
      </footer>
    </div>
  )
}

export default App
