export default function DebatePanel({ debate }) {
  return (
    <section className="debate-panel surface-card">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Debate room</p>
          <h3>Panel alignment and conflict notes</h3>
        </div>
      </div>

      <div className="debate-stats">
        <div>
          <span>Weighted</span>
          <strong>{debate.weightedScore.toFixed(1)}</strong>
        </div>
        <div>
          <span>Average</span>
          <strong>{debate.rawAverage.toFixed(1)}</strong>
        </div>
        <div>
          <span>Votes</span>
          <strong>
            {debate.votes.hire} hire / {debate.votes.hold} hold / {debate.votes.reject} reject
          </strong>
        </div>
      </div>

      <div className="debate-stream">
        {(debate.conflicts.length > 0 ? debate.conflicts : ["No major conflicts detected."]).map((item) => (
          <div key={item} className="debate-stream__item">
            {item}
          </div>
        ))}
      </div>

      <div>
        <p className="agent-card__section-title">Resolution notes</p>
        <ul className="detail-list">
          {debate.resolutionNotes.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
