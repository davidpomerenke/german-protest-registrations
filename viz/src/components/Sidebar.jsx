import { TOPIC_COLORS, DEFAULT_COLOR, TOPIC_CATEGORIES } from '../constants'

export default function Sidebar({ selectedEvent, hoveredEvent, stats, topicCounts }) {
  const event = selectedEvent || hoveredEvent

  // Get top topics
  const topTopics = TOPIC_CATEGORIES
    .filter(t => topicCounts[t] > 0)
    .sort((a, b) => (topicCounts[b] || 0) - (topicCounts[a] || 0))
    .slice(0, 12)

  return (
    <aside className="sidebar">
      {event ? (
        <section className="event-detail">
          <h3>Event Details</h3>

          <div className="detail-row">
            <span className="label">City</span>
            <span className="value">{event.city}</span>
          </div>

          <div className="detail-row">
            <span className="label">Date</span>
            <span className="value">{event.date.toLocaleDateString('de-DE', {
              weekday: 'short',
              year: 'numeric',
              month: 'short',
              day: 'numeric'
            })}</span>
          </div>

          <div className="detail-row full">
            <span className="label">Topic</span>
            <span className="value topic-text">{event.topic}</span>
          </div>

          {event.organizer && (
            <div className="detail-row full">
              <span className="label">Organizer</span>
              <span className="value">{event.organizer}</span>
            </div>
          )}

          {event.topics && event.topics.length > 0 && (
            <div className="detail-row full">
              <span className="label">Categories</span>
              <div className="category-tags">
                {event.topics.map((t, i) => (
                  <span
                    key={i}
                    className="category-tag"
                    style={{ backgroundColor: TOPIC_COLORS[t] || DEFAULT_COLOR }}
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}

          {(event.participants_registered || event.participants_actual) && (
            <div className="detail-row">
              <span className="label">Participants</span>
              <span className="value">
                {event.participants_registered && `${event.participants_registered.toLocaleString()} registered`}
                {event.participants_registered && event.participants_actual && ' / '}
                {event.participants_actual && `${event.participants_actual.toLocaleString()} actual`}
              </span>
            </div>
          )}

          <div className="detail-row">
            <span className="label">Region</span>
            <span className="value">{event.region}</span>
          </div>
        </section>
      ) : (
        <section className="topic-legend">
          <h3>Top Categories</h3>
          <p className="legend-hint">Click on a bubble to see details</p>

          <div className="topic-list">
            {topTopics.map(topic => (
              <div key={topic} className="topic-item">
                <span
                  className="topic-dot"
                  style={{ backgroundColor: TOPIC_COLORS[topic] || DEFAULT_COLOR }}
                />
                <span className="topic-name">{topic}</span>
                <span className="topic-count">{(topicCounts[topic] || 0).toLocaleString()}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="about-section">
        <h3>About</h3>
        <p>
          Official protest registration data from 17 German cities, collected via{' '}
          <a href="https://fragdenstaat.de" target="_blank" rel="noopener noreferrer">FragDenStaat</a>{' '}
          Freedom of Information requests. AI-categorized using GPT-4.
        </p>
      </section>
    </aside>
  )
}
