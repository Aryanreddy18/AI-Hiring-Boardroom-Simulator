import { useEffect, useMemo, useRef, useState } from "react";

function InterviewQuestion({
  question,
  value,
  onChange,
  isActive,
  onAskQuestion,
}) {
  return (
    <label className={`field field--wide ${isActive ? "field--active" : ""}`}>
      <span>{question.agent} question</span>
      <div className="question-card">
        <div className="question-card__head">
          <strong>{question.question}</strong>
          <button
            type="button"
            className="ghost-button"
            onClick={() => onAskQuestion(question)}
          >
            Ask question
          </button>
        </div>
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
                Round {entry.round} | {entry.agent}
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
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [videoError, setVideoError] = useState("");
  const [activeQuestionId, setActiveQuestionId] = useState("");

  const isFinished = interviewState?.status === "finished";
  const questions = useMemo(() => interviewState?.questions || [], [interviewState?.questions]);

  useEffect(() => {
    if (!interviewState || isFinished) {
      return undefined;
    }

    let isMounted = true;

    const enableCamera = async () => {
      if (!navigator.mediaDevices?.getUserMedia) {
        if (isMounted) {
          setVideoError("Camera preview is not supported in this browser.");
        }
        return;
      }

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
        if (!isMounted) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        setVideoError("");
      } catch (error) {
        setVideoError("Unable to access camera. Allow camera permission to display live video.");
      }
    };

    enableCamera();

    return () => {
      isMounted = false;
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
    };
  }, [interviewState?.session_id, isFinished]);

  useEffect(() => {
    if (!questions.length || isFinished) {
      return;
    }
    const firstQuestion = questions[0];
    setActiveQuestionId(firstQuestion.question_id);
    if (typeof window === "undefined" || !window.speechSynthesis) {
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new window.SpeechSynthesisUtterance(
      `${firstQuestion.agent} agent asks: ${firstQuestion.question}`,
    );
    utterance.rate = 1;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  }, [questions, isFinished]);

  if (!interviewState) {
    return null;
  }

  const askQuestion = (question) => {
    setActiveQuestionId(question.question_id);
    if (typeof window === "undefined" || !window.speechSynthesis) {
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new window.SpeechSynthesisUtterance(
      `${question.agent} agent asks: ${question.question}`,
    );
    window.speechSynthesis.speak(utterance);
  };

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

      <div className="live-interview-grid">
        <div className="video-panel">
          <p className="eyebrow">Video is on</p>
          <video
            ref={videoRef}
            className="video-panel__feed"
            autoPlay
            muted
            playsInline
          />
          {videoError && <p className="video-panel__error">{videoError}</p>}
          {interviewState.video_call && (
            <div className="callout">
              <span>Video room</span>
              <strong>{interviewState.video_call.room_id}</strong>
              <a href={interviewState.video_call.join_url} target="_blank" rel="noreferrer">
                Open join URL
              </a>
            </div>
          )}
        </div>

        <div className="question-queue">
          <p className="eyebrow">Current round prompts</p>
          {questions.map((question) => (
            <button
              key={question.question_id}
              type="button"
              className={`question-pill ${activeQuestionId === question.question_id ? "is-active" : ""}`}
              onClick={() => askQuestion(question)}
            >
              {question.agent}: {question.question}
            </button>
          ))}
        </div>
      </div>

      {!isFinished && questions.length > 0 && (
        <>
          <div className="form-grid">
            {questions.map((question) => (
              <InterviewQuestion
                key={question.question_id}
                question={question}
                value={answers[question.agent] || ""}
                onChange={onAnswerChange}
                isActive={activeQuestionId === question.question_id}
                onAskQuestion={askQuestion}
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
