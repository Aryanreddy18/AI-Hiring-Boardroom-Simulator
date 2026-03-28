import { motion } from "framer-motion";

export default function FinalDecisionCard({ decision, supervisor }) {
  const color =
    decision.decision === "strong_hire" || decision.decision === "hire"
      ? "decision-card--success"
      : decision.decision === "reject"
        ? "decision-card--danger"
        : "decision-card--warning";

  return (
    <motion.article
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={`decision-card ${color}`}
    >
      <p className="eyebrow">Final decision</p>
      <h3>{decision.decision.replace("_", " ")}</h3>
      <p className="decision-card__score">{decision.score.toFixed(1)}</p>

      <p>{decision.explanation}</p>

      <div className="decision-card__footer">
        <span>Supervisor confidence</span>
        <strong>{Math.round(supervisor.confidence * 100)}%</strong>
      </div>
    </motion.article>
  );
}
