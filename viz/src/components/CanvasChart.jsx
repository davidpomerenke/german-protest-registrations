import { useRef, useEffect, useState, useMemo, useCallback } from 'react'
import * as d3 from 'd3'
import { TOPIC_COLORS, DEFAULT_COLOR, getOrganizationColor } from '../constants'

export default function CanvasChart({
  data,
  yearRange,
  viewRange,
  viewMode,
  filters,
  organizationCounts,
  onSelect,
  onHover
}) {
  const containerRef = useRef(null)
  const canvasRef = useRef(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })
  const [tooltip, setTooltip] = useState(null)
  const [precomputedPositions, setPrecomputedPositions] = useState(null)

  // Load precomputed positions once on mount
  useEffect(() => {
    fetch(import.meta.env.BASE_URL + 'positions.json')
      .then(res => res.json())
      .then(positions => {
        console.log('Loaded precomputed positions:', positions.meta)
        setPrecomputedPositions(positions)
      })
      .catch(err => console.error('Failed to load precomputed positions:', err))
  }, [])

  // Map data to precomputed positions and apply filters via visibility
  const { nodes, xScale, yearPositions, cityLanes, margin } = useMemo(() => {
    if (data.length === 0 || !precomputedPositions) {
      return { nodes: [], xScale: null, yearPositions: [], cityLanes: [], margin: null }
    }

    const margin = viewMode === 'by-city'
      ? { top: 50, right: 20, bottom: 40, left: 120 }
      : { top: 50, right: 20, bottom: 40, left: 20 }

    // Get precomputed positions for current view mode
    const positions = viewMode === 'by-city'
      ? precomputedPositions.byCity
      : precomputedPositions.all

    // Create position lookup
    const positionMap = new Map(positions.map(p => [p.id, p]))

    // Time scale for zooming
    const minDate = new Date(viewRange.start, 0, 1)
    const maxDate = new Date(viewRange.end, 11, 31)
    const xScale = d3.scaleTime()
      .domain([minDate, maxDate])
      .range([margin.left, dimensions.width - margin.right])

    // Create year positions for labels
    const years = []
    for (let y = viewRange.start; y <= viewRange.end; y++) {
      years.push({
        year: y,
        x: xScale(new Date(y, 6, 1))
      })
    }

    // Create city lanes for by-city mode
    let cityLanes = []
    if (viewMode === 'by-city') {
      const cities = [...new Set(data.map(d => d.city))].sort()
      const laneHeight = (dimensions.height - margin.top - margin.bottom) / cities.length
      cityLanes = cities.map((city, i) => ({
        city,
        y: margin.top + i * laneHeight + laneHeight / 2,
        height: laneHeight
      }))
    }

    // Map data to nodes with precomputed positions
    const nodes = data.map(d => {
      const pos = positionMap.get(d.id)
      if (!pos) {
        console.warn(`No precomputed position for event ${d.id}`)
        return null
      }

      // Determine visibility based on filters
      const visible =
        d.year >= viewRange.start &&
        d.year <= viewRange.end

      // Apply colors based on context
      let displayColor
      if (filters.topic) {
        displayColor = getOrganizationColor(d.primaryGroup, organizationCounts)
      } else {
        displayColor = d.color // Topic color
      }

      return {
        ...d,
        x: pos.x,
        y: pos.y,
        r: pos.r,
        displayColor,
        visible
      }
    }).filter(n => n !== null)

    return { nodes, xScale, yearPositions: years, cityLanes, margin }
  }, [data, precomputedPositions, dimensions, viewRange, viewMode, filters, organizationCounts])

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
    if (!canvasRef.current || nodes.length === 0 || !margin) return

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

    // Draw city lanes if in by-city mode
    if (viewMode === 'by-city' && cityLanes.length > 0) {
      ctx.font = '13px Inter, system-ui, sans-serif'
      ctx.textAlign = 'right'
      ctx.textBaseline = 'middle'

      cityLanes.forEach((lane, i) => {
        // Alternating background
        if (i % 2 === 0) {
          ctx.fillStyle = '#f9f9f9'
          ctx.fillRect(0, lane.y - lane.height / 2, dimensions.width, lane.height)
        }

        // City label
        ctx.fillStyle = '#333'
        ctx.font = 'bold 13px Inter, system-ui, sans-serif'
        ctx.fillText(lane.city, margin.left - 15, lane.y)

        // Separator line
        if (i > 0) {
          ctx.strokeStyle = '#e0e0e0'
          ctx.lineWidth = 1
          ctx.beginPath()
          ctx.moveTo(margin.left, lane.y - lane.height / 2)
          ctx.lineTo(dimensions.width, lane.y - lane.height / 2)
          ctx.stroke()
        }
      })
    }

    // Draw year labels and gridlines
    ctx.font = '12px Inter, system-ui, sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'alphabetic'
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

    // Draw bubbles (only visible ones)
    nodes.forEach(node => {
      if (!node.visible) return

      ctx.beginPath()
      ctx.arc(node.x, node.y, node.r, 0, 2 * Math.PI)
      ctx.fillStyle = node.displayColor + 'bb' // Add transparency
      ctx.fill()

      // Add border for small circles to ensure visibility
      if (node.r < 4) {
        ctx.strokeStyle = node.displayColor + 'ee'
        ctx.lineWidth = 0.8
        ctx.stroke()
      }
    })

  }, [nodes, dimensions, yearPositions, viewMode, cityLanes, margin])

  // Handle mouse interactions
  const handleMouseMove = useCallback((e) => {
    if (!canvasRef.current || nodes.length === 0) return

    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    // Find closest visible node within threshold
    let closest = null
    let minDist = 20 // Pixel threshold

    for (const node of nodes) {
      if (!node.visible) continue

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

    // Find clicked visible node
    for (const node of nodes) {
      if (!node.visible) continue

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

  if (!precomputedPositions) {
    return (
      <div className="canvas-chart" ref={containerRef}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
          <div className="spinner"></div>
          <p style={{ marginLeft: '1rem' }}>Loading precomputed layout...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="canvas-chart" ref={containerRef}>
      <canvas
        ref={canvasRef}
        onMouseMove={handleMouseMove}
        onClick={handleClick}
        onMouseLeave={handleMouseLeave}
        style={{ cursor: tooltip ? 'pointer' : 'default' }}
      />

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
