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

  // Precompute force-based layout positions once when data changes
  const { nodes, xScale, yearPositions, cityLanes } = useMemo(() => {
    if (data.length === 0) return { nodes: [], xScale: null, yearPositions: [], cityLanes: [] }

    const margin = viewMode === 'by-city'
      ? { top: 50, right: 20, bottom: 40, left: 120 } // More left margin for city labels
      : { top: 50, right: 20, bottom: 40, left: 20 }
    const width = dimensions.width - margin.left - margin.right
    const height = dimensions.height - margin.top - margin.bottom

    // Time scale (use viewRange for zoom, not yearRange)
    const minDate = new Date(viewRange.start, 0, 1)
    const maxDate = new Date(viewRange.end, 11, 31)
    const xScale = d3.scaleTime()
      .domain([minDate, maxDate])
      .range([margin.left, dimensions.width - margin.right])

    // Create year positions for labels (based on view range)
    const years = []
    for (let y = viewRange.start; y <= viewRange.end; y++) {
      years.push({
        year: y,
        x: xScale(new Date(y, 6, 1))
      })
    }

    // Sample if too many points (for performance)
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

    // Create city lanes for by-city mode
    let cityLanes = []
    if (viewMode === 'by-city') {
      const cities = [...new Set(displayData.map(d => d.city))].sort()
      const laneHeight = height / cities.length
      cityLanes = cities.map((city, i) => ({
        city,
        y: margin.top + i * laneHeight + laneHeight / 2,
        height: laneHeight
      }))
    }

    // Create nodes with radius based on participant count (area proportional to participants)
    // Area = π*r², so for area ∝ participants: r = sqrt(participants) * scale
    const nodes = displayData.map(d => {
      const participants = d.participants_registered || 50
      // Area-based sizing: radius = sqrt(participants) * scale + minimum
      const r = Math.max(2.5, Math.min(15, Math.sqrt(participants) * 0.12))

      // Determine target Y position based on view mode
      let targetY
      if (viewMode === 'by-city') {
        const lane = cityLanes.find(l => l.city === d.city)
        targetY = lane ? lane.y : margin.top + height / 2
      } else {
        targetY = margin.top + height / 2
      }

      return {
        ...d,
        r,
        targetX: xScale(d.date), // Target x position for force
        targetY, // Target y position (city lane or center)
        x: xScale(d.date), // Initial position
        y: targetY, // Start at target Y
        vx: 0,
        vy: 0
      }
    })

    // Run force simulation to completion (precompute positions for streamgraph)
    const yStrength = viewMode === 'by-city' ? 0.2 : 0.02 // Stronger Y force for city lanes
    const simulation = d3.forceSimulation(nodes)
      .force('x', d3.forceX(d => d.targetX).strength(1)) // Strong force to lock to timeline position
      .force('y', d3.forceY(d => d.targetY).strength(yStrength)) // Center within lane/view
      .force('collide', d3.forceCollide(d => d.r + 0.8).iterations(3).strength(0.9)) // Prevent overlap with good separation
      .force('charge', d3.forceManyBody().strength(-1).distanceMax(50)) // Slight repulsion for better distribution
      .velocityDecay(0.3) // Slower velocity decay for smoother settling
      .stop()

    // Run simulation synchronously to full completion for smooth streamgraph
    const iterations = Math.ceil(Math.log(simulation.alphaMin()) / Math.log(1 - simulation.alphaDecay()))
    for (let i = 0; i < iterations; ++i) {
      simulation.tick()
    }

    // Clamp y positions to canvas bounds
    if (viewMode === 'by-city') {
      // Clamp within city lanes
      nodes.forEach(node => {
        const lane = cityLanes.find(l => l.city === node.city)
        if (lane) {
          const laneTop = lane.y - lane.height / 2
          const laneBottom = lane.y + lane.height / 2
          node.y = Math.max(laneTop + node.r, Math.min(laneBottom - node.r, node.y))
        }
      })
    } else {
      // Clamp to overall bounds
      nodes.forEach(node => {
        node.y = Math.max(margin.top + node.r, Math.min(dimensions.height - margin.bottom - node.r, node.y))
      })
    }

    // Apply colors based on context
    nodes.forEach(node => {
      // If a topic is selected, color by organization; otherwise color by topic
      if (filters.topic) {
        node.displayColor = getOrganizationColor(node.primaryGroup, organizationCounts)
      } else {
        node.displayColor = node.color // Already set to topic color
      }
    })

    return { nodes, xScale, yearPositions: years, cityLanes, margin }
  }, [data, dimensions, viewRange, viewMode, filters, organizationCounts])

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

    // Draw bubbles
    nodes.forEach(node => {
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
