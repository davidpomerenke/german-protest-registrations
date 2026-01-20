#!/usr/bin/env node

/**
 * Precompute force layout positions for all view modes
 * This script runs the d3-force simulation to completion and saves positions
 * so the browser doesn't need to run any physics calculations
 */

import * as d3 from 'd3';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Configuration matching the chart
const CANVAS_WIDTH = 1400;
const CANVAS_HEIGHT = 600;
const YEAR_MIN = 2012;
const YEAR_MAX = 2024;

console.log('Reading CSV data...');
const csvPath = path.join(__dirname, '../../docs/data.csv');
const csvContent = fs.readFileSync(csvPath, 'utf-8');
const rawData = d3.csvParse(csvContent);

console.log(`Loaded ${rawData.length} events`);

// Parse data (matching App.jsx logic)
const data = rawData.map((d, i) => {
  let topics = [];
  try {
    if (d.protest_topics) {
      topics = JSON.parse(d.protest_topics);
    }
  } catch (e) {
    topics = [];
  }

  const date = new Date(d.date);
  return {
    id: i,
    city: d.city,
    date: date,
    year: date.getFullYear(),
    participants_registered: d.participants_registered ? +d.participants_registered : null,
  };
}).filter(d => !isNaN(d.date.getTime()));

console.log(`Parsed ${data.length} valid events`);

// Helper function to compute positions for a given view mode
function computePositions(data, viewMode, dimensions) {
  const margin = viewMode === 'by-city'
    ? { top: 50, right: 20, bottom: 40, left: 120 }
    : { top: 50, right: 20, bottom: 40, left: 20 };

  const width = dimensions.width - margin.left - margin.right;
  const height = dimensions.height - margin.top - margin.bottom;

  // Time scale
  const minDate = new Date(YEAR_MIN, 0, 1);
  const maxDate = new Date(YEAR_MAX, 11, 31);
  const xScale = d3.scaleTime()
    .domain([minDate, maxDate])
    .range([margin.left, dimensions.width - margin.right]);

  // Create city lanes for by-city mode
  let cityLanes = [];
  if (viewMode === 'by-city') {
    const cities = [...new Set(data.map(d => d.city))].sort();
    const laneHeight = height / cities.length;
    cityLanes = cities.map((city, i) => ({
      city,
      y: margin.top + i * laneHeight + laneHeight / 2,
      height: laneHeight
    }));
  }

  // Create nodes
  const nodes = data.map(d => {
    const participants = d.participants_registered || 50;
    const r = Math.max(2.5, Math.min(15, Math.sqrt(participants) * 0.12));

    let targetY;
    if (viewMode === 'by-city') {
      const lane = cityLanes.find(l => l.city === d.city);
      targetY = lane ? lane.y : margin.top + height / 2;
    } else {
      targetY = margin.top + height / 2;
    }

    return {
      id: d.id,
      r,
      targetX: xScale(d.date),
      targetY,
      x: xScale(d.date),
      y: targetY,
      vx: 0,
      vy: 0,
      city: d.city
    };
  });

  console.log(`Running force simulation for ${viewMode} mode...`);

  // Run force simulation
  const yStrength = viewMode === 'by-city' ? 0.2 : 0.02;
  const simulation = d3.forceSimulation(nodes)
    .force('x', d3.forceX(d => d.targetX).strength(1))
    .force('y', d3.forceY(d => d.targetY).strength(yStrength))
    .force('collide', d3.forceCollide(d => d.r + 0.8).iterations(3).strength(0.9))
    .force('charge', d3.forceManyBody().strength(-1).distanceMax(50))
    .velocityDecay(0.3)
    .stop();

  const iterations = Math.ceil(Math.log(simulation.alphaMin()) / Math.log(1 - simulation.alphaDecay()));

  for (let i = 0; i < iterations; ++i) {
    simulation.tick();
    if (i % 50 === 0) {
      process.stdout.write(`\r  Progress: ${Math.round(i / iterations * 100)}%`);
    }
  }
  console.log('\r  Progress: 100%');

  // Clamp y positions
  if (viewMode === 'by-city') {
    nodes.forEach(node => {
      const lane = cityLanes.find(l => l.city === node.city);
      if (lane) {
        const laneTop = lane.y - lane.height / 2;
        const laneBottom = lane.y + lane.height / 2;
        node.y = Math.max(laneTop + node.r, Math.min(laneBottom - node.r, node.y));
      }
    });
  } else {
    nodes.forEach(node => {
      node.y = Math.max(margin.top + node.r, Math.min(dimensions.height - margin.bottom - node.r, node.y));
    });
  }

  // Return positions
  return nodes.map(n => ({
    id: n.id,
    x: Math.round(n.x * 100) / 100,  // Round to 2 decimals
    y: Math.round(n.y * 100) / 100,
    r: Math.round(n.r * 100) / 100
  }));
}

// Compute for both view modes
console.log('\n=== Computing ALL CITIES view ===');
const allPositions = computePositions(data, 'all', { width: CANVAS_WIDTH, height: CANVAS_HEIGHT });

console.log('\n=== Computing BY CITY view ===');
const byCityPositions = computePositions(data, 'by-city', { width: CANVAS_WIDTH, height: CANVAS_HEIGHT });

// Create output object
const output = {
  meta: {
    generatedAt: new Date().toISOString(),
    eventCount: data.length,
    canvasWidth: CANVAS_WIDTH,
    canvasHeight: CANVAS_HEIGHT,
    yearRange: [YEAR_MIN, YEAR_MAX]
  },
  all: allPositions,
  byCity: byCityPositions
};

// Write to file
const outputPath = path.join(__dirname, '../../docs/positions.json');
fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));

console.log(`\n✓ Wrote precomputed positions to ${outputPath}`);
console.log(`  File size: ${(fs.statSync(outputPath).size / 1024 / 1024).toFixed(2)} MB`);
