import AgentCard from "../AgentCard";
import DebatePanel from "../DebatePanel";
import FinalDecisionCard from "../FinalDecisionCard";
import ScoreChart from "../ScoreChart";

function MetricTile({ label, value, tone = "default" }) {
  return (
    <div className={`metric-tile metric-tile--${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default function Dashboard({ result }) {
  if (!result) {
    return null;
  }

  const {
    chartData,
    agentCards,
    finalDecision,
    supervisor,
    debate,
    metrics,
  } = result;

  return (
    <section className="dashboard">
      <div className="dashboard__hero">
        <div>
          <p className="eyebrow">Screening outcome</p>
          <h2>Boardroom screening result</h2>
          <p className="dashboard__lead">
            The panel blends resume-job similarity, role-fit scoring, and
            supervisor moderation into one recommendation.
          </p>
        </div>
        <FinalDecisionCard decision={finalDecision} supervisor={supervisor} />
      </div>

      <div className="metrics-grid">
        <MetricTile
          label="Required skill match"
          value={`${Math.round(metrics.requiredSkillMatch * 100)}%`}
          tone="success"
        />
        <MetricTile
          label="Experience alignment"
          value={`${Math.round(metrics.experienceMatch * 100)}%`}
        />
        <MetricTile
          label="Text similarity"
          value={`${Math.round(metrics.textSimilarity * 100)}%`}
        />
        <MetricTile
          label="Weighted debate score"
          value={debate.weightedScore.toFixed(1)}
        />
      </div>

      <div className="dashboard__grid">
        <ScoreChart data={chartData} />
        <DebatePanel debate={debate} />
      </div>

      <div className="agent-grid">
        {agentCards.map((card) => (
          <AgentCard key={card.agent} {...card} />
        ))}
      </div>
    </section>
  );
}
