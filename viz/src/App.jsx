import { useState, useEffect, useMemo } from 'react'
import * as d3 from 'd3'
import CanvasChart from './components/CanvasChart'
import FilterPanel from './components/FilterPanel'
import Sidebar from './components/Sidebar'
import { TOPIC_CATEGORIES, getTopicColor } from './constants'
import './App.css'

function App() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    city: '',
    topic: '',
    yearStart: 2012,
    yearEnd: 2024,
  })
  const [viewMode, setViewMode] = useState('all') // 'all' or 'by-city'
  const [viewRange, setViewRange] = useState({ start: 2012, end: 2024 }) // For zoom slider
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [hoveredEvent, setHoveredEvent] = useState(null)

  // Load data on mount
  useEffect(() => {
    d3.csv(import.meta.env.BASE_URL + 'data.csv').then(rawData => {
      const parsed = rawData.map((d, i) => {
        // Parse protest_topics JSON
        let topics = []
        try {
          if (d.protest_topics) {
            topics = JSON.parse(d.protest_topics)
          }
        } catch (e) {
          topics = []
        }

        // Parse protest_groups JSON
        let groups = []
        try {
          if (d.protest_groups) {
            groups = JSON.parse(d.protest_groups)
          }
        } catch (e) {
          groups = []
        }

        const date = new Date(d.date)
        return {
          id: i,
          region: d.region,
          city: d.city,
          date: date,
          year: date.getFullYear(),
          month: date.getMonth(),
          organizer: d.organizer || null,
          topic: d.topic || 'Unknown',
          topics: topics, // Array of categorized topics
          primaryTopic: topics[0] || null,
          groups: groups, // Array of organizations/groups
          primaryGroup: groups[0] || d.organizer || null,
          participants_registered: d.participants_registered ? +d.participants_registered : null,
          participants_actual: d.participants_actual ? +d.participants_actual : null,
          color: getTopicColor(topics)
        }
      }).filter(d => !isNaN(d.date.getTime()))

      setData(parsed)

      // Set year range from data
      const years = parsed.map(d => d.year)
      const minYear = Math.min(...years)
      const maxYear = Math.max(...years)
      setFilters(f => ({ ...f, yearStart: minYear, yearEnd: maxYear }))
      setViewRange({ start: minYear, end: maxYear })

      setLoading(false)
    })
  }, [])

  // Filter data based on current filters (NOT by year - that's handled by view zoom)
  const filteredData = useMemo(() => {
    return data.filter(d => {
      if (filters.city && d.city !== filters.city) return false
      if (filters.topic && !d.topics.includes(filters.topic)) return false
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

  // Topic counts for the filter
  const topicCounts = useMemo(() => {
    const counts = {}
    data.forEach(d => {
      d.topics.forEach(t => {
        counts[t] = (counts[t] || 0) + 1
      })
    })
    return counts
  }, [data])

  // Organization counts (for coloring when topic is selected)
  const organizationCounts = useMemo(() => {
    const counts = {}
    filteredData.forEach(d => {
      if (d.primaryGroup) {
        counts[d.primaryGroup] = (counts[d.primaryGroup] || 0) + 1
      }
    })
    return counts
  }, [filteredData])

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
          {stats.filtered.toLocaleString()} of {stats.total.toLocaleString()} demonstrations
          {filters.topic && ` • ${filters.topic}`}
          {filters.city && ` • ${filters.city}`}
        </p>
      </header>

      <FilterPanel
        filters={filters}
        setFilters={setFilters}
        cities={cities}
        yearRange={yearRange}
        viewRange={viewRange}
        setViewRange={setViewRange}
        viewMode={viewMode}
        setViewMode={setViewMode}
        topicCounts={topicCounts}
      />

      <main className="main">
        <CanvasChart
          data={filteredData}
          yearRange={yearRange}
          viewRange={viewRange}
          viewMode={viewMode}
          filters={filters}
          organizationCounts={organizationCounts}
          onSelect={setSelectedEvent}
          onHover={setHoveredEvent}
        />
        <Sidebar
          selectedEvent={selectedEvent}
          hoveredEvent={hoveredEvent}
          stats={stats}
          topicCounts={topicCounts}
        />
      </main>

      <footer className="footer">
        <p>
          Data from <a href="https://fragdenstaat.de" target="_blank" rel="noopener noreferrer">FragDenStaat</a> FOI requests •
          <a href="https://github.com/davidpomerenke/german-protest-registrations" target="_blank" rel="noopener noreferrer">GitHub</a> •
          <a href="https://zenodo.org/records/10094245" target="_blank" rel="noopener noreferrer">Zenodo</a>
        </p>
      </footer>
    </div>
  )
}

export default App
