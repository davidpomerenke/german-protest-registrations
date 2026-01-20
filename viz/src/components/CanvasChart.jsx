import { useRef, useEffect, useState, useMemo, useCallback } from 'react'
import * as d3 from 'd3'
import { TOPIC_COLORS, DEFAULT_COLOR } from '../constants'

export default function CanvasChart({ data, yearRange, filters, onSelect, onHover }) {
  const containerRef = useRef(null)
  const canvasRef = useRef(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })
  const [tooltip, setTooltip] = useState(null)

  // Precompute positions once when data changes
  const { nodes, xScale, yearPositions } = useMemo(() => {
    if (data.length === 0) return { nodes: [], xScale: null, yearPositions: [] }

    const margin = { top: 50, right: 20, bottom: 40, left: 20 }
    const width = dimensions.width - margin.left - margin.right
    const height = dimensions.height - margin.top - margin.bottom

    // Time scale
    const minDate = new Date(yearRange.min, 0, 1)
    const maxDate = new Date(yearRange.max, 11, 31)
    const xScale = d3.scaleTime()
      .domain([minDate, maxDate])
      .range([margin.left, dimensions.width - margin.right])

    // Create year positions for labels
    const years = []
    for (let y = yearRange.min; y <= yearRange.max; y++) {
      years.push({
        year: y,
        x: xScale(new Date(y, 6, 1))
      })
    }

    // Sample if too many points (for initial render performance)
    let displayData = data
    if (data.length > 15000) {
      // Stratified sample: take proportionally from each year
      const byYear = d3.group(data, d => d.year)
      const sampleRate = 15000 / data.length
      displayData = []
      byYear.forEach((events, year) => {
        const sampleSize = Math.ceil(events.length * sampleRate)
        const sampled = d3.shuffle([...events]).slice(0, sampleSize)
        displayData.push(...sampled)
      })
    }

    // Position nodes using a simple beeswarm-like algorithm
    // Group by month for vertical distribution
    const nodes = displayData.map(d => {
      const x = xScale(d.date)
      // Use deterministic pseudo-random y based on id for consistency
      const yOffset = ((d.id * 2654435761) % 1000) / 1000 // Knuth's multiplicative hash
      const y = margin.top + yOffset * height

      // Size based on participants (log scale, capped)
      const participants = d.participants_registered || 50
      const r = Math.max(2, Math.min(8, Math.sqrt(participants) * 0.15 + 1.5))

      return {
        ...d,
        x, y, r,
        screenX: x,
        screenY: y
      }
    })

    return { nodes, xScale, yearPositions: years }
  }, [data, dimensions, yearRange])

  // Update dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect()
        setDimensions({
          width: rect.width,
          height: Math.max(450, window.innerHeight - 280)
        })
      }
    }
    updateDimensions()
    window.addEventListener('resize', updateDimensions)
    return () => window.removeEventListener('resize', updateDimensions)
  }, [])

  // Draw on canvas
  useEffect(() => {
    if (!canvasRef.current || nodes.length === 0) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    const dpr = window.devicePixelRatio || 1

    // Set canvas size accounting for device pixel ratio
    canvas.width = dimensions.width * dpr
    canvas.height = dimensions.height * dpr
    canvas.style.width = `${dimensions.width}px`
    canvas.style.height = `${dimensions.height}px`
    ctx.scale(dpr, dpr)

    // Clear
    ctx.clearRect(0, 0, dimensions.width, dimensions.height)

    // Draw year labels and gridlines
    ctx.font = '12px Inter, system-ui, sans-serif'
    ctx.textAlign = 'center'
    yearPositions.forEach(({ year, x }) => {
      // Gridline
      ctx.strokeStyle = '#e5e5e5'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(x, 45)
      ctx.lineTo(x, dimensions.height - 30)
      ctx.stroke()

      // Year label
      ctx.fillStyle = '#666'
      ctx.fillText(year.toString(), x, 30)
    })

    // Draw bubbles
    nodes.forEach(node => {
      ctx.beginPath()
      ctx.arc(node.x, node.y, node.r, 0, 2 * Math.PI)
      ctx.fillStyle = node.color + 'bb' // Add transparency
      ctx.fill()
    })

  }, [nodes, dimensions, yearPositions])

  // Handle mouse interactions
  const handleMouseMove = useCallback((e) => {
    if (!canvasRef.current || nodes.length === 0) return

    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    // Find closest node within threshold
    let closest = null
    let minDist = 20 // Pixel threshold

    for (const node of nodes) {
      const dist = Math.sqrt((node.x - x) ** 2 + (node.y - y) ** 2)
      if (dist < minDist && dist < node.r + 10) {
        minDist = dist
        closest = node
      }
    }

    if (closest) {
      setTooltip({
        x: e.clientX,
        y: e.clientY,
        event: closest
      })
      onHover(closest)
    } else {
      setTooltip(null)
      onHover(null)
    }
  }, [nodes, onHover])

  const handleClick = useCallback((e) => {
    if (!canvasRef.current || nodes.length === 0) return

    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    // Find clicked node
    for (const node of nodes) {
      const dist = Math.sqrt((node.x - x) ** 2 + (node.y - y) ** 2)
      if (dist <= node.r + 5) {
        onSelect(node)
        return
      }
    }
    onSelect(null)
  }, [nodes, onSelect])

  const handleMouseLeave = useCallback(() => {
    setTooltip(null)
    onHover(null)
  }, [onHover])

  return (
    <div className="canvas-chart" ref={containerRef}>
      <canvas
        ref={canvasRef}
        onMouseMove={handleMouseMove}
        onClick={handleClick}
        onMouseLeave={handleMouseLeave}
        style={{ cursor: tooltip ? 'pointer' : 'default' }}
      />

      {data.length > 15000 && (
        <div className="sample-notice">
          Showing ~15,000 of {data.length.toLocaleString()} events
        </div>
      )}

      {tooltip && (
        <div
          className="tooltip"
          style={{
            left: Math.min(tooltip.x + 10, window.innerWidth - 300),
            top: tooltip.y + 10
          }}
        >
          <div className="tooltip-header">
            <span className="city">{tooltip.event.city}</span>
            <span className="date">{tooltip.event.date.toLocaleDateString('de-DE')}</span>
          </div>
          <div className="tooltip-topic">{tooltip.event.topic?.substring(0, 120)}{tooltip.event.topic?.length > 120 ? '...' : ''}</div>
          {tooltip.event.topics.length > 0 && (
            <div className="tooltip-categories">
              {tooltip.event.topics.slice(0, 3).map((t, i) => (
                <span
                  key={i}
                  className="category-tag"
                  style={{ backgroundColor: TOPIC_COLORS[t] || DEFAULT_COLOR }}
                >
                  {t}
                </span>
              ))}
            </div>
          )}
          {tooltip.event.participants_registered && (
            <div className="tooltip-meta">{tooltip.event.participants_registered.toLocaleString()} registered</div>
          )}
        </div>
      )}
    </div>
  )
}
