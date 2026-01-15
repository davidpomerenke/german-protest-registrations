import { useRef, useEffect, useState, useMemo } from 'react'
import * as d3 from 'd3'

// City color palette
const cityColors = {
  'Berlin': '#e63946',
  'München': '#457b9d',
  'Köln': '#2a9d8f',
  'Dresden': '#e9c46a',
  'Bremen': '#f4a261',
  'Freiburg': '#264653',
  'Mainz': '#a8dadc',
  'Erfurt': '#1d3557',
  'Kiel': '#f77f00',
  'Magdeburg': '#d62828',
  'Karlsruhe': '#003049',
  'Wiesbaden': '#588157',
  'Duisburg': '#bc6c25',
  'Saarbrücken': '#606c38',
  'Dortmund': '#283618',
  'Wuppertal': '#9b2226',
  'Potsdam': '#005f73'
}

const getCityColor = (city) => cityColors[city] || '#6c757d'

export default function BubbleChart({ data, viewMode, onSelect, onHover, hoveredEvent }) {
  const containerRef = useRef(null)
  const svgRef = useRef(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })

  // Sample data for performance - max 8000 bubbles
  const displayData = useMemo(() => {
    if (data.length <= 8000) return data
    // Stratified sampling: keep more recent data
    const sorted = [...data].sort((a, b) => b.date - a.date)
    return sorted.slice(0, 8000)
  }, [data])

  // Update dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect()
        setDimensions({
          width: rect.width,
          height: Math.max(500, window.innerHeight - 300)
        })
      }
    }
    updateDimensions()
    window.addEventListener('resize', updateDimensions)
    return () => window.removeEventListener('resize', updateDimensions)
  }, [])

  // Render bubbles
  useEffect(() => {
    if (!svgRef.current || displayData.length === 0) return

    const { width, height } = dimensions
    const margin = { top: 40, right: 20, bottom: 60, left: 60 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove()

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Time scale for x-axis
    const timeExtent = d3.extent(displayData, d => d.date)
    const xScale = d3.scaleTime()
      .domain(timeExtent)
      .range([0, innerWidth])

    // Calculate node positions based on view mode
    let nodes
    if (viewMode === 'timeline') {
      // Timeline view: x = date, y = random within year band
      nodes = displayData.map(d => ({
        ...d,
        x: xScale(d.date),
        y: innerHeight / 2 + (Math.random() - 0.5) * innerHeight * 0.8,
        r: Math.sqrt(d.participants_registered || 50) * 0.3 + 2
      }))
    } else if (viewMode === 'city') {
      // Group by city
      const cities = [...new Set(displayData.map(d => d.city))].sort()
      const yScale = d3.scaleBand()
        .domain(cities)
        .range([0, innerHeight])
        .padding(0.1)

      nodes = displayData.map(d => ({
        ...d,
        x: xScale(d.date),
        y: yScale(d.city) + yScale.bandwidth() / 2 + (Math.random() - 0.5) * yScale.bandwidth() * 0.6,
        r: Math.sqrt(d.participants_registered || 50) * 0.25 + 1.5
      }))

      // Add city labels
      g.selectAll('.city-label')
        .data(cities)
        .enter()
        .append('text')
        .attr('class', 'city-label')
        .attr('x', -10)
        .attr('y', d => yScale(d) + yScale.bandwidth() / 2)
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'middle')
        .attr('font-size', '11px')
        .attr('fill', '#666')
        .text(d => d)
    } else {
      // Default: random positions with force layout
      nodes = displayData.map(d => ({
        ...d,
        x: Math.random() * innerWidth,
        y: Math.random() * innerHeight,
        r: Math.sqrt(d.participants_registered || 50) * 0.3 + 2
      }))
    }

    // Run force simulation for collision detection
    const simulation = d3.forceSimulation(nodes)
      .force('x', d3.forceX(d => d.x).strength(0.3))
      .force('y', d3.forceY(d => d.y).strength(0.3))
      .force('collide', d3.forceCollide(d => d.r + 0.5).iterations(2))
      .stop()

    // Run simulation synchronously
    for (let i = 0; i < 120; i++) simulation.tick()

    // Draw x-axis (timeline)
    const xAxis = d3.axisBottom(xScale)
      .ticks(d3.timeYear.every(1))
      .tickFormat(d3.timeFormat('%Y'))

    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${innerHeight + 10})`)
      .call(xAxis)
      .selectAll('text')
      .attr('fill', '#666')
      .attr('font-size', '11px')

    g.selectAll('.x-axis path, .x-axis line')
      .attr('stroke', '#ddd')

    // Draw bubbles
    const bubbles = g.selectAll('.bubble')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('class', 'bubble')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', d => d.r)
      .attr('fill', d => getCityColor(d.city))
      .attr('fill-opacity', 0.7)
      .attr('stroke', 'white')
      .attr('stroke-width', 0.5)
      .style('cursor', 'pointer')
      .on('mouseenter', function(event, d) {
        d3.select(this)
          .attr('fill-opacity', 1)
          .attr('stroke', '#333')
          .attr('stroke-width', 2)
        onHover(d)
      })
      .on('mouseleave', function(event, d) {
        d3.select(this)
          .attr('fill-opacity', 0.7)
          .attr('stroke', 'white')
          .attr('stroke-width', 0.5)
        onHover(null)
      })
      .on('click', function(event, d) {
        onSelect(d)
      })

    // Add title for year labels at top
    const years = [...new Set(displayData.map(d => d.year))].sort()
    if (viewMode === 'timeline') {
      g.selectAll('.year-label')
        .data(years)
        .enter()
        .append('text')
        .attr('class', 'year-label')
        .attr('x', d => xScale(new Date(d, 6, 1)))
        .attr('y', -15)
        .attr('text-anchor', 'middle')
        .attr('font-size', '12px')
        .attr('font-weight', 'bold')
        .attr('fill', '#333')
        .text(d => d)
    }

  }, [displayData, dimensions, viewMode, onSelect, onHover])

  return (
    <div className="bubble-chart" ref={containerRef}>
      {displayData.length < data.length && (
        <div className="sample-notice">
          Showing {displayData.length.toLocaleString()} of {data.length.toLocaleString()} events for performance
        </div>
      )}
      <svg ref={svgRef} />
      {hoveredEvent && (
        <div
          className="tooltip"
          style={{
            position: 'absolute',
            top: '10px',
            right: '10px'
          }}
        >
          <strong>{hoveredEvent.city}</strong>
          <div>{hoveredEvent.date.toLocaleDateString('de-DE')}</div>
          <div className="topic">{hoveredEvent.topic?.substring(0, 100)}{hoveredEvent.topic?.length > 100 ? '...' : ''}</div>
          {hoveredEvent.participants_registered && (
            <div>{hoveredEvent.participants_registered.toLocaleString()} registered</div>
          )}
        </div>
      )}
    </div>
  )
}
