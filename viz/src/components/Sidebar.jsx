export default function Sidebar({ selectedEvent, hoveredEvent, stats }) {
  const event = selectedEvent || hoveredEvent

  return (
    <aside className="sidebar">
      <section className="stats-section">
        <h3>Statistics</h3>
        <div className="stats-grid">
          <div className="stat">
            <span className="value">{stats.total.toLocaleString()}</span>
            <span className="label">Total Events</span>
          </div>
          <div className="stat">
            <span className="value">{stats.filtered.toLocaleString()}</span>
            <span className="label">Filtered</span>
          </div>
          <div className="stat">
            <span className="value">{stats.cities}</span>
            <span className="label">Cities</span>
          </div>
          <div className="stat">
            <span className="value">{stats.yearRange}</span>
            <span className="label">Date Range</span>
          </div>
        </div>
      </section>

      <section className="event-section">
        <h3>Event Details</h3>
        {event ? (
          <div className="event-detail">
            <div className="detail-row">
              <span className="label">City</span>
              <span className="value city-badge" style={{ '--city-color': getCityColor(event.city) }}>
                {event.city}
              </span>
            </div>
            <div className="detail-row">
              <span className="label">Date</span>
              <span className="value">
                {event.date.toLocaleDateString('de-DE', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </span>
            </div>
            <div className="detail-row">
              <span className="label">Topic</span>
              <span className="value topic">{event.topic || 'Not specified'}</span>
            </div>
            {event.organizer && (
              <div className="detail-row">
                <span className="label">Organizer</span>
                <span className="value">{event.organizer}</span>
              </div>
            )}
            {event.participants_registered && (
              <div className="detail-row">
                <span className="label">Registered</span>
                <span className="value">{event.participants_registered.toLocaleString()} participants</span>
              </div>
            )}
            {event.participants_actual && (
              <div className="detail-row">
                <span className="label">Actual</span>
                <span className="value">{event.participants_actual.toLocaleString()} participants</span>
              </div>
            )}
            <div className="detail-row">
              <span className="label">Region</span>
              <span className="value">{event.region}</span>
            </div>
          </div>
        ) : (
          <p className="placeholder">Click or hover on a bubble to see details</p>
        )}
      </section>

      <section className="legend-section">
        <h3>City Legend</h3>
        <div className="legend-grid">
          {Object.entries(cityColors).map(([city, color]) => (
            <div key={city} className="legend-item">
              <span className="color-dot" style={{ backgroundColor: color }}></span>
              <span className="city-name">{city}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="about-section">
        <h3>About</h3>
        <p>
          This dataset leverages Freedom of Information laws to collect official protest
          data from 17 German cities. Data compiled via{' '}
          <a href="https://fragdenstaat.de" target="_blank" rel="noopener noreferrer">FragDenStaat</a>.
        </p>
        <p>
          Visualization inspired by{' '}
          <a href="https://webkid.io/projects/fragdenstaat-berlin-demonstrations/" target="_blank" rel="noopener noreferrer">
            webkid's Berlin Demonstrations project
          </a>.
        </p>
      </section>
    </aside>
  )
}

// City colors for legend
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

function getCityColor(city) {
  return cityColors[city] || '#6c757d'
}
