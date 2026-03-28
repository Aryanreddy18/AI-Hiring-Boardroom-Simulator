import { motion } from "framer-motion";

const fieldLabels = {
  candidateName: "Candidate name",
  maxRounds: "Interview rounds",
};

export default function UploadForm({
  form,
  onChange,
  onAnalyze,
  onStartInterview,
  loadingAction,
}) {
  const isAnalyzing = loadingAction === "analyze";
  const isStartingInterview = loadingAction === "interview";

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1 }}
      className="composer-panel"
    >
      <div className="composer-panel__header">
        <p className="eyebrow">Live hiring workspace</p>
        <h1>AI Hiring Boardroom Simulator</h1>
        <p>
          Paste a resume and job description to run the screening board. Start
          the interview flow when you want the panel to ask live follow-up
          questions.
        </p>
      </div>

      <div className="form-grid">
        <label className="field field--wide">
          <span>Resume text</span>
          <textarea
            name="resumeText"
            value={form.resumeText}
            onChange={onChange}
            placeholder="Paste the candidate's resume text here..."
            rows={12}
          />
        </label>

        <label className="field field--wide">
          <span>Job description</span>
          <textarea
            name="jdText"
            value={form.jdText}
            onChange={onChange}
            placeholder="Paste the role requirements, skills, and responsibilities..."
            rows={12}
          />
        </label>

        {Object.entries(fieldLabels).map(([name, label]) => (
          <label key={name} className="field">
            <span>{label}</span>
            <input
              name={name}
              type={name === "maxRounds" ? "number" : "text"}
              min={name === "maxRounds" ? "1" : undefined}
              max={name === "maxRounds" ? "3" : undefined}
              value={form[name]}
              onChange={onChange}
            />
          </label>
        ))}
      </div>

      <div className="form-actions">
        <button
          type="button"
          className="primary-button"
          onClick={onAnalyze}
          disabled={Boolean(loadingAction)}
        >
          {isAnalyzing ? "Analyzing panel..." : "Run screening"}
        </button>

        <button
          type="button"
          className="secondary-button"
          onClick={onStartInterview}
          disabled={Boolean(loadingAction)}
        >
          {isStartingInterview ? "Starting interview..." : "Start interview"}
        </button>
      </div>
    </motion.section>
  );
}
