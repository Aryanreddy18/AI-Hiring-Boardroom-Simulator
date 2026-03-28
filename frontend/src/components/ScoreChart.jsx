import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function ScoreChart({ data }) {
  return (
    <section className="surface-card chart-card">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Panel scoring</p>
          <h3>Agent-by-agent score spread</h3>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(20, 47, 45, 0.08)" />
          <XAxis dataKey="name" stroke="#335c59" />
          <YAxis stroke="#335c59" />
          <Tooltip />
          <Bar dataKey="score" fill="#0f766e" radius={[10, 10, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </section>
  );
}
