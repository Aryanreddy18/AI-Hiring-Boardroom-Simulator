function InterviewQuestion({ question, value, onChange }) {
  return (
    <label className="field field--wide">
      <span>
        {question.agent} question
      </span>
      <div className="question-card">
        <strong>{question.question}</strong>
        <textarea
          value={value}
          onChange={(event) => onChange(question.agent, event.target.value)}
          placeholder={`Enter the candidate's response for the ${question.agent} round...`}
          rows={5}
        />
      </div>
    </label>
  );
}

function InterviewSummary({ result }) {
  if (!result) {
    return null;
  }

  const transcript = result.transcript || [];

  return (
    <div className="interview-summary">
      <div className="decision-inline">
        <div>
          <p className="eyebrow">Interview final</p>
          <h3>{result.final_decision.decision.replace("_", " ")}</h3>
          <p>{result.final_decision.explanation}</p>
        </div>
        <div className="decision-inline__score">{result.final_decision.score.toFixed(1)}</div>
      </div>

      <div className="metrics-grid">
        <div className="metric-tile">
          <span>Rounds completed</span>
          <strong>{result.interview_summary.rounds_completed}</strong>
        </div>
        <div className="metric-tile">
          <span>Baseline score</span>
          <strong>{result.supervisor_final.baseline_score.toFixed(1)}</strong>
        </div>
        <div className="metric-tile">
          <span>Interview weighted</span>
          <strong>{result.supervisor_final.interview_weighted_score.toFixed(1)}</strong>
        </div>
        <div className="metric-tile">
          <span>Debate conflicts</span>
          <strong>{result.supervisor_final.conflict_count}</strong>
        </div>
      </div>

      <div className="transcript-list">
        {transcript.map((entry) => (
          <article key={entry.timestamp + entry.agent} className="surface-card transcript-card">
            <div className="transcript-card__header">
              <span>
                Round {entry.round} • {entry.agent}
              </span>
              <strong>{entry.review.score.toFixed(1)}</strong>
            </div>
            <p><strong>Question:</strong> {entry.question}</p>
            <p><strong>Answer:</strong> {entry.answer_text}</p>
            <p><strong>Review:</strong> {entry.review.feedback}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

export default function InterviewPanel({
  interviewState,
  answers,
  onAnswerChange,
  onSubmitRound,
  onRefreshStatus,
  loadingAction,
}) {
  if (!interviewState) {
    return null;
  }

  const isFinished = interviewState.status === "finished";
  const questions = interviewState.questions || [];

  return (
    <section className="surface-card interview-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Interview workflow</p>
          <h2>Live panel interview</h2>
          <p>
            Session <code>{interviewState.session_id}</code> for {interviewState.candidate_name}
          </p>
        </div>
        <div className="interview-panel__actions">
          <button
            type="button"
            className="ghost-button"
            onClick={onRefreshStatus}
            disabled={Boolean(loadingAction)}
          >
            Refresh status
          </button>
        </div>
      </div>

      {interviewState.video_call && (
        <div className="callout">
          <span>Video room</span>
          <strong>{interviewState.video_call.room_id}</strong>
          <a href={interviewState.video_call.join_url} target="_blank" rel="noreferrer">
            Open join URL
          </a>
        </div>
      )}

      {!isFinished && questions.length > 0 && (
        <>
          <div className="form-grid">
            {questions.map((question) => (
              <InterviewQuestion
                key={question.question_id}
                question={question}
                value={answers[question.agent] || ""}
                onChange={onAnswerChange}
              />
            ))}
          </div>

          {interviewState.round_review && (
            <div className="callout">
              <span>Previous round supervisor note</span>
              <strong>{interviewState.round_review.supervisor.status}</strong>
              <p>{interviewState.round_review.supervisor.note}</p>
            </div>
          )}

          <div className="form-actions">
            <button
              type="button"
              className="primary-button"
              onClick={onSubmitRound}
              disabled={Boolean(loadingAction)}
            >
              {loadingAction === "submit" ? "Submitting round..." : "Submit interview round"}
            </button>
          </div>
        </>
      )}

      {isFinished && <InterviewSummary result={interviewState.final_result} />}
    </section>
  );
}
