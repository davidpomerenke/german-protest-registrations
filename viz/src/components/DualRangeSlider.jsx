import { useRef, useEffect, useState, useCallback } from 'react'
import './DualRangeSlider.css'

export default function DualRangeSlider({ min, max, valueStart, valueEnd, onChange }) {
  const trackRef = useRef(null)
  const [dragging, setDragging] = useState(null) // 'start', 'end', or 'range'
  const [dragStartX, setDragStartX] = useState(0)
  const [dragStartValues, setDragStartValues] = useState({ start: 0, end: 0 })

  const getValueFromX = useCallback((x) => {
    if (!trackRef.current) return min
    const rect = trackRef.current.getBoundingClientRect()
    const ratio = (x - rect.left) / rect.width
    const value = min + ratio * (max - min)
    return Math.max(min, Math.min(max, Math.round(value)))
  }, [min, max])

  const handleMouseDown = useCallback((e, handle) => {
    e.preventDefault()
    setDragging(handle)
    setDragStartX(e.clientX)
    setDragStartValues({ start: valueStart, end: valueEnd })
  }, [valueStart, valueEnd])

  const handleMouseMove = useCallback((e) => {
    if (!dragging) return

    if (dragging === 'start') {
      const newStart = getValueFromX(e.clientX)
      if (newStart < valueEnd) {
        onChange({ start: newStart, end: valueEnd })
      }
    } else if (dragging === 'end') {
      const newEnd = getValueFromX(e.clientX)
      if (newEnd > valueStart) {
        onChange({ start: valueStart, end: newEnd })
      }
    } else if (dragging === 'range') {
      const dx = e.clientX - dragStartX
      const rect = trackRef.current.getBoundingClientRect()
      const valueDelta = Math.round((dx / rect.width) * (max - min))
      const rangeSize = dragStartValues.end - dragStartValues.start

      let newStart = dragStartValues.start + valueDelta
      let newEnd = dragStartValues.end + valueDelta

      // Clamp to bounds
      if (newStart < min) {
        newStart = min
        newEnd = min + rangeSize
      }
      if (newEnd > max) {
        newEnd = max
        newStart = max - rangeSize
      }

      onChange({ start: newStart, end: newEnd })
    }
  }, [dragging, dragStartX, dragStartValues, getValueFromX, min, max, valueStart, valueEnd, onChange])

  const handleMouseUp = useCallback(() => {
    setDragging(null)
  }, [])

  useEffect(() => {
    if (dragging) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
      return () => {
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [dragging, handleMouseMove, handleMouseUp])

  // Calculate positions
  const startPercent = ((valueStart - min) / (max - min)) * 100
  const endPercent = ((valueEnd - min) / (max - min)) * 100

  return (
    <div className="dual-range-slider">
      <div className="slider-labels">
        <span>{min}</span>
        <span>{max}</span>
      </div>
      <div className="slider-track" ref={trackRef}>
        <div className="slider-track-inactive"></div>
        <div
          className="slider-track-active"
          style={{
            left: `${startPercent}%`,
            width: `${endPercent - startPercent}%`,
          }}
          onMouseDown={(e) => handleMouseDown(e, 'range')}
        ></div>
        <div
          className="slider-handle"
          style={{ left: `${startPercent}%` }}
          onMouseDown={(e) => handleMouseDown(e, 'start')}
        >
          <div className="slider-handle-label">{valueStart}</div>
        </div>
        <div
          className="slider-handle"
          style={{ left: `${endPercent}%` }}
          onMouseDown={(e) => handleMouseDown(e, 'end')}
        >
          <div className="slider-handle-label">{valueEnd}</div>
        </div>
      </div>
    </div>
  )
}
