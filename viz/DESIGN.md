# German Protest Registrations Visualization - Architecture Design

**Inspired by:** https://fragdenstaat.de/dossier/demo-hauptstadt-berlin/

## Design Philosophy

Following FragDenStaat's approach: **narrative-driven, transparent, accessible**. Clean typography, open data principles, minimal aesthetic with maximum information density. Dark mode support for accessibility.

---

## 1. Component Structure

### 1.1 Layout Architecture

```
App
├── Header
│   ├── Logo/Title
│   ├── ThemeToggle (light/dark mode)
│   └── DataDownload (CSV/JSON export)
│
├── ControlPanel
│   ├── ViewModeSelector (overall/city/topic facets)
│   ├── FilterControls
│   │   ├── CityFilter (multi-select dropdown)
│   │   ├── TopicFilter (search + autocomplete)
│   │   └── DateRangeFilter (dual slider)
│   └── StatsOverview (live counts)
│
├── VisualizationContainer
│   ├── ForceGraphView
│   │   ├── D3ForceSimulation
│   │   ├── NodeGroup (protests as bubbles)
│   │   ├── LinkGroup (temporal/thematic connections)
│   │   └── TooltipOverlay
│   │
│   ├── TimelineView
│   │   ├── TimelineAxis (D3 time scale)
│   │   ├── BubbleStream (protests over time)
│   │   ├── Scrubber (interactive time navigation)
│   │   └── MiniMap (overview + context)
│   │
│   └── ViewTransition (animated switching)
│
├── DetailPanel (slide-out)
│   ├── MetadataDisplay
│   │   ├── ProtestInfo (date, organizer, topic, participants)
│   │   ├── CityContext (population, trends)
│   │   └── SourceLinks
│   │       ├── GitHubLink (raw CSV data)
│   │       └── FragDenStaatLink (FOI request)
│   └── RelatedProtests (similarity clustering)
│
└── Footer
    ├── MethodologyLink
    ├── CitationInfo (DOI: 10.5281/zenodo.10094245)
    └── LicenseInfo (CC BY 4.0)
```

### 1.2 Component Details

#### ForceGraphView
**Purpose:** Show protest network with force-directed physics

**Props:**
- `data: Protest[]` - filtered protest events
- `viewMode: 'overall' | 'city' | 'topic'` - faceting mode
- `onNodeClick: (protest: Protest) => void`
- `highlightedNode: string | null`

**D3 Integration:**
- Force simulation: `d3.forceSimulation()`
- Collision detection: `d3.forceCollide(radius)`
- Clustering: `d3.forceX()`, `d3.forceY()` for facets
- Node size: sqrt scale based on `participants_registered`
- Color: categorical scale by city or topic

**Interactions:**
- Hover: tooltip with basic info
- Click: open DetailPanel
- Drag: reposition nodes (sticky)
- Zoom/pan: d3.zoom()

#### TimelineView
**Purpose:** Chronological bubble stream with temporal patterns

**Props:**
- `data: Protest[]`
- `brushRange: [Date, Date]` - for mini-map
- `onTimeSelect: (date: Date) => void`

**D3 Integration:**
- X-axis: `d3.scaleTime()` (date range)
- Y-axis: `d3.scaleLinear()` (participants or jittered for clarity)
- Bubbles: positioned by date, sized by participants
- Brush: `d3.brushX()` for range selection

**Visual Encoding:**
- X-position: date
- Y-position: participant count (log scale) or beeswarm layout
- Size: registered participants (area = sqrt scale)
- Color: city or topic
- Opacity: can fade non-matching filters

#### DetailPanel
**Purpose:** Rich metadata display for selected protest

**Data Structure:**
```typescript
interface ProtestDetail {
  id: string;
  date: Date;
  city: string;
  region: string;
  organizer: string | null;
  topic: string;
  participants_registered: number | null;
  participants_actual: number | null;
  github_data_url: string;
  fragdenstaat_request_id: string | null;
  fragdenstaat_request_url: string | null;
}
```

**Sections:**
1. **Header:** Topic (large), date, city
2. **Metadata Grid:**
   - Organizer (if available)
   - Registered: N participants
   - Actual: N participants (if available)
   - City population context
3. **Source Links:**
   - GitHub: Link to CSV row/commit
   - FragDenStaat: Link to FOI request
4. **Related Protests:**
   - Same organizer (temporal view)
   - Similar topic (NLP clustering)
   - Same date in other cities

---

## 2. Data Transformation Requirements

### 2.1 Input Data Schema

**Source CSV:** `/data/processed/german_protest_registrations_5_cities_2018-2022.csv`

```csv
region,city,date,organizer,topic,participants_registered,participants_actual
Bayern,München,2018-01-01,Gemeinschaft Sant Egidio,Friedenskundgebung,150.0,
```

### 2.2 Transformed Data Structure

```typescript
interface Protest {
  // Core identifiers
  id: string; // hash of city+date+topic

  // Temporal
  date: Date; // parsed ISO string
  year: number;
  month: number;
  dayOfWeek: number;

  // Spatial
  city: string;
  region: string;
  cityPopulation: number; // from lookup table
  coordinates: [number, number]; // lat/lng for mapping

  // Metadata
  organizer: string | null;
  topic: string;
  topicCategory: string; // clustered via NLP or manual tags
  participantsRegistered: number | null;
  participantsActual: number | null;

  // Source provenance
  dataSourceUrl: string; // GitHub blob URL
  foiRequestId: string | null; // FragDenStaat request ID
  foiRequestUrl: string | null;
}

interface CityMetadata {
  name: string;
  region: string;
  population: number; // 2022 estimate
  coordinates: [number, number];
  dataYears: [number, number]; // coverage range
  totalProtests: number;
  fragdenstaatRequestId: string | null;
}

interface TopicCluster {
  label: string; // e.g., "Climate", "Labor", "Anti-Racism"
  keywords: string[];
  color: string;
  count: number;
}
```

### 2.3 Data Processing Pipeline

**Phase 1: ETL (Extract, Transform, Load)**
```typescript
// data/transformer.ts
export async function loadProtestData(): Promise<Protest[]> {
  const csv = await fetch('/data/german_protest_registrations_5_cities_2018-2022.csv');
  const parsed = d3.csvParse(csv);

  return parsed.map(row => ({
    id: generateId(row.city, row.date, row.topic),
    date: new Date(row.date),
    year: new Date(row.date).getFullYear(),
    // ... rest of mapping

    // Generate GitHub URL
    dataSourceUrl: generateGitHubBlobUrl(row),

    // Map to FragDenStaat request
    foiRequestId: cityToFoiMapping[row.city]?.requestId,
    foiRequestUrl: cityToFoiMapping[row.city]?.url,
  }));
}
```

**Phase 2: Topic Clustering**
- Option A (Simple): Keyword matching on `topic` field
- Option B (Advanced): TF-IDF + K-means clustering
- Option C (Hybrid): Manual seed categories + fuzzy matching

```typescript
const topicCategories = {
  'climate': ['klima', 'umwelt', 'fridays', 'kohle', 'verkehr'],
  'labor': ['streik', 'tarif', 'ig metall', 'verdi', 'arbeit'],
  'antiracism': ['rassismus', 'migration', 'flucht', 'asyl'],
  'peace': ['frieden', 'krieg', 'nato', 'rüstung'],
  'feminism': ['frauen', 'femini', 'gender', '8. märz'],
  'housing': ['miete', 'wohnung', 'enteignung', 'gentrifizierung'],
  'democracy': ['demokratie', 'grundrechte', 'überwachung'],
  // ... more categories
};
```

**Phase 3: Aggregations**

```typescript
interface AggregatedStats {
  totalProtests: number;
  totalParticipants: number;
  byCity: Record<string, number>;
  byTopic: Record<string, number>;
  byYear: Record<number, number>;
  timeSeriesDaily: Array<{ date: Date; count: number }>;
}
```

### 2.4 Data Enrichment

**City Metadata JSON** (`/data/city_metadata.json`)
```json
{
  "München": {
    "population": 1512000,
    "coordinates": [48.1351, 11.5820],
    "fragdenstaatRequest": {
      "id": "123456",
      "url": "https://fragdenstaat.de/anfrage/...",
      "title": "Versammlungen München 2018-2022"
    }
  }
}
```

**FOI Request Mapping** (`/data/foi_mapping.json`)
- Parse `/foi-requests/fragdenstaat_requests.json`
- Map city names to request IDs
- Store request metadata (status, dates, attachments)

---

## 3. Technology Stack Recommendations

### 3.1 Core Framework

**React 18+** with TypeScript
- Hooks-based architecture
- Concurrent rendering for smooth animations
- Suspense for data loading states

**Why React?**
- Component reusability
- Declarative D3 integration pattern
- Strong TypeScript support
- Rich ecosystem

### 3.2 D3.js Integration

**D3.js v7** (modular imports)
```typescript
import { scaleLinear, scaleTime } from 'd3-scale';
import { forceSimulation, forceLink, forceCollide } from 'd3-force';
import { zoom, zoomIdentity } from 'd3-zoom';
import { select, selectAll } from 'd3-selection';
```

**Integration Pattern:**
- **React for structure**, **D3 for math**
- React renders SVG elements
- D3 calculates positions, scales, forces
- useRef for D3 selections
- useEffect for simulation lifecycle

**Example:**
```typescript
function ForceGraph({ data }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation | null>(null);

  useEffect(() => {
    const simulation = d3.forceSimulation(data.nodes)
      .force('charge', d3.forceManyBody().strength(-50))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .on('tick', () => {
        // Update React state to trigger re-render
        setNodes([...simulation.nodes()]);
      });

    simulationRef.current = simulation;
    return () => simulation.stop();
  }, [data]);

  return (
    <svg ref={svgRef}>
      {nodes.map(node => (
        <circle key={node.id} cx={node.x} cy={node.y} />
      ))}
    </svg>
  );
}
```

### 3.3 State Management

**Option A: React Context + useReducer (Recommended)**
- Lightweight for this app size
- Built-in TypeScript support
- No external dependencies

```typescript
interface AppState {
  protests: Protest[];
  filters: FilterState;
  viewMode: ViewMode;
  selectedProtest: Protest | null;
  theme: 'light' | 'dark';
}

const AppContext = createContext<{
  state: AppState;
  dispatch: Dispatch<Action>;
} | null>(null);
```

**Option B: Zustand**
- Simpler API than Redux
- Built-in devtools
- Good for derived state (filtered protests)

```typescript
const useProtestStore = create<ProtestStore>((set, get) => ({
  protests: [],
  filters: defaultFilters,

  filteredProtests: () => {
    const { protests, filters } = get();
    return applyFilters(protests, filters);
  },

  setFilter: (key, value) => set(state => ({
    filters: { ...state.filters, [key]: value }
  })),
}));
```

### 3.4 Routing

**React Router v6**
```typescript
<Routes>
  <Route path="/" element={<App />}>
    <Route index element={<OverallView />} />
    <Route path="city/:cityName" element={<CityFacetView />} />
    <Route path="topic/:topicId" element={<TopicFacetView />} />
    <Route path="protest/:protestId" element={<ProtestDetailView />} />
  </Route>
</Routes>
```

**URL State Synchronization:**
```
/?view=overall&cities=Berlin,München&topics=climate&date=2018-2022
/protest/berlin-2020-01-15-fridays-for-future
```

### 3.5 Styling

**CSS-in-JS: Styled Components**
- Theme support (light/dark)
- TypeScript props
- No global namespace pollution

```typescript
const theme = {
  light: {
    bg: '#ffffff',
    text: '#1a1a1a',
    primary: '#0066cc',
    accent: '#ff6b35',
  },
  dark: {
    bg: '#1a1a1a',
    text: '#f4f4f4',
    primary: '#3399ff',
    accent: '#ff8c42',
  },
};

const Container = styled.div`
  background: ${props => props.theme.bg};
  color: ${props => props.theme.text};
  transition: all 0.3s ease;
`;
```

**Alternative: CSS Modules + CSS Variables**
- Native CSS performance
- Better for dark mode (prefers-color-scheme)
- Simpler build setup

### 3.6 Build Tools

**Vite** (Recommended)
- Fastest dev server
- Native ESM
- Optimized production builds
- TypeScript out-of-box

**Alternative: Create React App**
- More opinionated
- Slower dev server
- Easier for beginners

### 3.7 Additional Libraries

| Purpose | Library | Why |
|---------|---------|-----|
| CSV parsing | `d3-dsv` | Built into D3, fast, standards-compliant |
| Date handling | `date-fns` | Lightweight, tree-shakeable, i18n support |
| URL state | `use-query-params` | Sync filters to URL |
| Animations | `framer-motion` | Smooth view transitions, spring physics |
| Charts (if needed) | `recharts` | React-native charts for stats panels |
| Fuzzy search | `fuse.js` | Topic filter autocomplete |
| Export data | `file-saver` | Download filtered CSV/JSON |

### 3.8 Testing

**Unit Tests:** Vitest (fast, Vite-native)
**Component Tests:** React Testing Library
**E2E Tests:** Playwright (visual regression for D3 visualizations)

---

## 4. File Structure

```
viz/
├── public/
│   ├── data/
│   │   ├── german_protest_registrations_5_cities_2018-2022.csv
│   │   ├── city_metadata.json
│   │   ├── foi_mapping.json
│   │   └── topic_clusters.json
│   ├── index.html
│   └── favicon.ico
│
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Container.tsx
│   │   │
│   │   ├── controls/
│   │   │   ├── ControlPanel.tsx
│   │   │   ├── ViewModeSelector.tsx
│   │   │   ├── CityFilter.tsx
│   │   │   ├── TopicFilter.tsx
│   │   │   ├── DateRangeFilter.tsx
│   │   │   └── StatsOverview.tsx
│   │   │
│   │   ├── visualizations/
│   │   │   ├── ForceGraphView/
│   │   │   │   ├── ForceGraphView.tsx
│   │   │   │   ├── D3ForceSimulation.ts
│   │   │   │   ├── NodeGroup.tsx
│   │   │   │   ├── LinkGroup.tsx
│   │   │   │   └── useForceSimulation.ts (hook)
│   │   │   │
│   │   │   ├── TimelineView/
│   │   │   │   ├── TimelineView.tsx
│   │   │   │   ├── TimelineAxis.tsx
│   │   │   │   ├── BubbleStream.tsx
│   │   │   │   ├── Scrubber.tsx
│   │   │   │   └── MiniMap.tsx
│   │   │   │
│   │   │   ├── shared/
│   │   │   │   ├── Tooltip.tsx
│   │   │   │   ├── Legend.tsx
│   │   │   │   └── ZoomControls.tsx
│   │   │   │
│   │   │   └── VisualizationContainer.tsx
│   │   │
│   │   ├── detail/
│   │   │   ├── DetailPanel.tsx
│   │   │   ├── MetadataDisplay.tsx
│   │   │   ├── SourceLinks.tsx
│   │   │   └── RelatedProtests.tsx
│   │   │
│   │   └── common/
│   │       ├── Button.tsx
│   │       ├── Dropdown.tsx
│   │       ├── Slider.tsx
│   │       └── Card.tsx
│   │
│   ├── hooks/
│   │   ├── useProtestData.ts
│   │   ├── useFilteredData.ts
│   │   ├── useD3Zoom.ts
│   │   ├── useDebounce.ts
│   │   └── useMediaQuery.ts
│   │
│   ├── utils/
│   │   ├── data/
│   │   │   ├── dataLoader.ts
│   │   │   ├── dataTransformer.ts
│   │   │   ├── topicClustering.ts
│   │   │   └── aggregations.ts
│   │   │
│   │   ├── d3/
│   │   │   ├── scales.ts
│   │   │   ├── forces.ts
│   │   │   ├── layouts.ts
│   │   │   └── transitions.ts
│   │   │
│   │   ├── filters.ts
│   │   ├── formatters.ts (date, numbers)
│   │   ├── urlState.ts
│   │   └── exportData.ts
│   │
│   ├── context/
│   │   ├── AppContext.tsx
│   │   ├── ThemeContext.tsx
│   │   └── FilterContext.tsx
│   │
│   ├── types/
│   │   ├── protest.ts
│   │   ├── filters.ts
│   │   ├── visualization.ts
│   │   └── index.ts
│   │
│   ├── styles/
│   │   ├── theme.ts
│   │   ├── globalStyles.ts
│   │   └── variables.css
│   │
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
│
├── tests/
│   ├── unit/
│   │   ├── dataTransformer.test.ts
│   │   └── filters.test.ts
│   ├── components/
│   │   └── ForceGraphView.test.tsx
│   └── e2e/
│       └── visualization.spec.ts
│
├── scripts/
│   ├── processData.ts (pre-processing for JSON)
│   └── generateFoiMapping.ts
│
├── .gitignore
├── package.json
├── tsconfig.json
├── vite.config.ts
├── README.md
└── DESIGN.md (this file)
```

---

## 5. Visual Design Specifications

### 5.1 Color Palette

**Light Mode:**
```css
--bg-primary: #ffffff;
--bg-secondary: #f8f9fa;
--text-primary: #1a1a1a;
--text-secondary: #6c757d;
--border: #dee2e6;
--primary: #0066cc;
--accent: #ff6b35;
--success: #28a745;
--warning: #ffc107;
```

**Dark Mode:**
```css
--bg-primary: #1a1a1a;
--bg-secondary: #2d2d2d;
--text-primary: #f4f4f4;
--text-secondary: #adb5bd;
--border: #495057;
--primary: #3399ff;
--accent: #ff8c42;
--success: #5cb85c;
--warning: #f0ad4e;
```

**Categorical Colors (Cities/Topics):**
- Use D3 color schemes: `d3.schemeTableau10` or `d3.schemePaired`
- Ensure WCAG AA contrast compliance
- Colorblind-friendly palettes

### 5.2 Typography

**Font Stack:**
```css
font-family:
  'Inter',
  -apple-system,
  BlinkMacSystemFont,
  'Segoe UI',
  system-ui,
  sans-serif;
```

**Type Scale:**
- Display: 2.5rem (40px) - Main title
- H1: 2rem (32px) - Section headers
- H2: 1.5rem (24px) - Panel titles
- Body: 1rem (16px) - Default text
- Small: 0.875rem (14px) - Metadata, labels
- Tiny: 0.75rem (12px) - Annotations

**Variable Font:** Use Inter's variable font for smooth weight transitions

### 5.3 Layout Grid

- **Desktop:** 12-column grid, 1200px max-width
- **Tablet:** 8-column grid, full-width
- **Mobile:** 4-column grid, full-width

**Spacing Scale:** 4px base unit (4, 8, 12, 16, 24, 32, 48, 64)

### 5.4 Visualization Aesthetics

**Force Graph:**
- Node radius: `sqrt(participants_registered)` scaled to 3-20px
- Stroke: 1px, color-coded border
- Opacity: 0.8 default, 1.0 on hover
- Links: 1px, `#ccc`, opacity 0.3

**Timeline Bubbles:**
- Same sizing as force graph
- Y-jitter for overlap prevention (beeswarm)
- Fade-in animation on load
- Glow effect on hover

**Transitions:**
- Duration: 300ms default, 600ms for view changes
- Easing: cubic-bezier(0.4, 0.0, 0.2, 1) (Material Design)
- Smooth morphing between view modes

---

## 6. Interaction Patterns

### 6.1 Filtering Flow

1. User selects city filter (multi-select)
2. Topic filter autocomplete updates suggestions
3. Date range slider updates visible range
4. All filters trigger debounced data update (300ms)
5. Visualization smoothly transitions to filtered state
6. Stats panel updates counts
7. URL updates with current filter state

### 6.2 View Mode Switching

**Overall View:**
- Force graph: all protests, clustered by density
- Timeline: chronological stream

**City Facets:**
- Force graph: separate clusters per city
- Timeline: color-coded by city, stacked lanes

**Topic Facets:**
- Force graph: separate clusters per topic category
- Timeline: color-coded by topic, grouped

### 6.3 Hover States

**Minimal Tooltip:**
```
München, 2020-03-15
Fridays for Future
1,500 participants
[Click for details]
```

**Hover Effects:**
- Node scale: 1.2x
- Glow: 0 0 8px rgba(primary, 0.5)
- Connected nodes highlight
- Dim non-connected nodes (opacity 0.3)

### 6.4 Click Actions

- **Click node:** Open DetailPanel (slide from right)
- **Click background:** Close DetailPanel
- **Click city label:** Filter to that city
- **Click topic in detail:** Filter to that topic

---

## 7. Data Provenance & Attribution

### 7.1 GitHub Links

**Format:**
```
https://github.com/davidpomerenke/german-protest-registrations/blob/main/data/processed/german_protest_registrations_5_cities_2018-2022.csv#L{line_number}
```

**Implementation:**
- Calculate line number from protest ID
- Deep link to specific CSV row
- Show commit hash for data version

### 7.2 FragDenStaat Links

**Request Mapping:**
```json
{
  "Berlin": {
    "requestId": "308169",
    "url": "https://fragdenstaat.de/anfrage/versammlungen-berlin-2023-2024/",
    "title": "Versammlungen Berlin 2023-2024",
    "status": "resolved"
  }
}
```

**Display:**
- Icon: FragDenStaat logo
- Text: "FOI Request: Versammlungen Berlin 2023-2024"
- Link opens in new tab

### 7.3 Citation

**Footer Always Visible:**
```
Data: Pomerenke, D. (2023). German Protest Registrations Dataset.
DOI: 10.5281/zenodo.10094245. License: CC BY 4.0
```

---

## 8. Performance Considerations

### 8.1 Data Loading

- **Lazy load CSV:** Fetch on mount, show skeleton loader
- **Progressive enhancement:** Show aggregated stats first, then full data
- **Caching:** Store parsed data in IndexedDB for repeat visits

### 8.2 Rendering Optimization

**Canvas vs SVG:**
- Use **SVG** for < 5,000 nodes (accessibility, interactivity)
- Switch to **Canvas** for > 5,000 nodes (performance)

**Virtual Scrolling:**
- Timeline: only render visible date range
- Detail panel list: virtualize related protests

**Debouncing:**
- Filter updates: 300ms debounce
- Force simulation: throttle tick updates to 60fps

### 8.3 Bundle Size

**Code Splitting:**
```typescript
const ForceGraphView = lazy(() => import('./ForceGraphView'));
const TimelineView = lazy(() => import('./TimelineView'));
```

**Tree-shaking D3:**
```typescript
// ❌ Don't
import * as d3 from 'd3';

// ✅ Do
import { scaleLinear } from 'd3-scale';
import { forceSimulation } from 'd3-force';
```

**Target:** < 200KB initial bundle, < 500KB total

---

## 9. Accessibility

### 9.1 Keyboard Navigation

- Tab through filters
- Arrow keys to navigate nodes in focus mode
- Enter to select, Escape to close detail panel
- Vim-style hjkl for power users (optional)

### 9.2 Screen Readers

- Semantic HTML: `<nav>`, `<main>`, `<aside>`
- ARIA labels on visualizations
- Alternative text for all data points
- Live regions for filter updates

### 9.3 Color Independence

- Never rely on color alone
- Use patterns, shapes, labels
- High contrast mode support
- WCAG AAA compliance goal

---

## 10. Future Enhancements (Post-MVP)

### Phase 2
- [ ] Geographic map view (Leaflet + D3)
- [ ] Network analysis: organizer collaboration graph
- [ ] Topic modeling: LDA or BERT embeddings
- [ ] Time-series forecasting: predict protest frequency

### Phase 3
- [ ] Comparison mode: side-by-side cities
- [ ] Embedding: iframe widget for external sites
- [ ] API: GraphQL endpoint for filtered data
- [ ] Localization: German and English

### Phase 4
- [ ] User annotations: crowdsourced protest details
- [ ] Event photos: integrate with Wikimedia Commons
- [ ] Social sharing: generate shareable visualizations
- [ ] Real-time updates: WebSocket for new FOI data

---

## 11. Development Workflow

### 11.1 Setup

```bash
cd /home/david/german-protest-registrations/viz

# Initialize Vite + React + TypeScript
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install d3 d3-scale d3-force d3-zoom d3-selection
npm install react-router-dom styled-components
npm install date-fns fuse.js file-saver
npm install -D @types/d3 @types/styled-components

# Dev server
npm run dev
```

### 11.2 Data Pipeline

```bash
# 1. Copy processed CSV to public/data/
cp ../data/processed/*.csv public/data/

# 2. Generate metadata JSON
npm run process-data

# 3. Map FOI requests
npm run generate-foi-mapping
```

### 11.3 Testing

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Visual regression
npm run test:visual
```

### 11.4 Deployment

**Static Hosting:** Vercel, Netlify, GitHub Pages

```bash
npm run build
# Outputs to dist/

# GitHub Pages
npm run deploy
```

---

## 12. Open Questions / Decisions Needed

1. **Data Update Frequency:** Manual vs automated pipeline?
2. **Topic Clustering:** Manual categories vs ML-based?
3. **Mobile Experience:** Simplified view or full feature parity?
4. **Hosting:** GitHub Pages or dedicated domain?
5. **Analytics:** Privacy-preserving tracking (Plausible, Fathom)?
6. **License:** Inherit CC BY 4.0 from data, or separate for code?

---

## 13. Success Metrics

**User Engagement:**
- Average session duration > 3 minutes
- Filter usage rate > 60%
- Detail panel open rate > 40%

**Performance:**
- Initial load < 2 seconds
- Interaction latency < 100ms
- Lighthouse score > 90

**Impact:**
- Citations in academic papers
- Media coverage
- FOI requests inspired by visualization

---

## References

- **FragDenStaat Berlin Dossier:** https://fragdenstaat.de/dossier/demo-hauptstadt-berlin/
- **D3 Force Graph Examples:** https://observablehq.com/@d3/force-directed-graph
- **React + D3 Integration:** https://2019.wattenberger.com/blog/react-and-d3
- **Observable Plot:** https://observablehq.com/plot/ (potential alternative to raw D3)

---

**Document Version:** 1.0
**Date:** 2026-01-15
**Author:** Architecture design for German Protest Registrations visualization
