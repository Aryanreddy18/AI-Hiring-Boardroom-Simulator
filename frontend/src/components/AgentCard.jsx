import { motion } from "framer-motion";

const toneByVote = {
  hire: "success",
  strong_hire: "success",
  hold: "warning",
  reject: "danger",
};

export default function AgentCard({
  title,
  agent,
  score,
  vote,
  confidence,
  rationale,
  strengths = [],
  concerns = [],
}) {
  const tone = toneByVote[vote] || "neutral";

  return (
    <motion.article
      whileHover={{ y: -4 }}
      className={`agent-card agent-card--${tone}`}
    >
      <div className="agent-card__header">
        <div>
          <p className="agent-card__eyebrow">{agent}</p>
          <h3>{title}</h3>
        </div>
        <div className="agent-card__score">{score.toFixed(1)}</div>
      </div>

      <div className="agent-card__meta">
        <span>{vote}</span>
        <span>{Math.round(confidence * 100)}% confidence</span>
      </div>

      <p className="agent-card__body">{rationale}</p>

      {strengths.length > 0 && (
        <div>
          <p className="agent-card__section-title">Strengths</p>
          <ul className="detail-list">
            {strengths.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {concerns.length > 0 && (
        <div>
          <p className="agent-card__section-title">Concerns</p>
          <ul className="detail-list">
            {concerns.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </motion.article>
  );
}
