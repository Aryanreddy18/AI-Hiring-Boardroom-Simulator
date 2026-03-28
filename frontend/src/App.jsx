import { useMemo, useState } from "react";

import UploadForm from "./components/UploadForm";
import Home from "./components/pages/Home";
import Dashboard from "./components/pages/Dashboard";
import InterviewPanel from "./components/InterviewPanel";
import {
  evaluateCandidate,
  getInterviewStatus,
  startInterview,
  submitInterviewAnswers,
} from "./services/api";
import { normalizeHiringResult } from "./utils/normalizeHiringResult";

const initialForm = {
  candidateName: "Candidate",
  maxRounds: 2,
  jdText: "",
};

function buildSubmitPayload(form, resumeFile) {
  return {
    resume_file: resumeFile,
    jd_text: form.jdText.trim(),
    candidate_name: form.candidateName.trim() || "Candidate",
    max_rounds: Number(form.maxRounds) || 2,
  };
}

function buildAnswerMap(questions) {
  return questions.reduce((accumulator, question) => {
    accumulator[question.agent] = "";
    return accumulator;
  }, {});
}

export default function App() {
  const [form, setForm] = useState(initialForm);
  const [loadingAction, setLoadingAction] = useState("");
  const [error, setError] = useState("");
  const [stage, setStage] = useState("upload");
  const [resumeFile, setResumeFile] = useState(null);
  const [screeningResult, setScreeningResult] = useState(null);
  const [interviewState, setInterviewState] = useState(null);
  const [interviewAnswers, setInterviewAnswers] = useState({});

  const normalizedScreening = useMemo(
    () => (screeningResult ? normalizeHiringResult(screeningResult) : null),
    [screeningResult],
  );

  const updateForm = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: name === "maxRounds" ? Math.min(3, Math.max(1, Number(value))) : value,
    }));
  };

  const updateResumeFile = (event) => {
    const selectedFile = event.target.files?.[0] || null;
    setResumeFile(selectedFile);
  };

  const validateForm = () => {
    if (!resumeFile) {
      setError("Please upload a resume file before continuing.");
      return false;
    }

    if (form.jdText.trim().length < 20) {
      setError("Job description text must be at least 20 characters.");
      return false;
    }

    setError("");
    return true;
  };

  const handleAnalyze = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setError("");
      setLoadingAction("analyze");
      const response = await evaluateCandidate(buildSubmitPayload(form, resumeFile));
      setScreeningResult(response);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoadingAction("");
    }
  };

  const handleStartInterview = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setError("");
      setLoadingAction("interview");
      const response = await startInterview(buildSubmitPayload(form, resumeFile));
      setInterviewState(response);
      setInterviewAnswers(buildAnswerMap(response.questions || []));
      setStage("interview");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoadingAction("");
    }
  };

  const updateInterviewAnswer = (agent, value) => {
    setInterviewAnswers((current) => ({
      ...current,
      [agent]: value,
    }));
  };

  const refreshInterviewStatus = async () => {
    if (!interviewState?.session_id) {
      return;
    }

    try {
      setError("");
      setLoadingAction("status");
      const response = await getInterviewStatus(interviewState.session_id);
      setInterviewState((current) => ({ ...current, ...response }));
      setInterviewAnswers(buildAnswerMap(response.questions || []));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoadingAction("");
    }
  };

  const handleSubmitInterviewRound = async () => {
    if (!interviewState?.session_id || !interviewState?.questions?.length) {
      return;
    }

    const answers = interviewState.questions.map((question) => ({
      agent: question.agent,
      answer_text: (interviewAnswers[question.agent] || "").trim(),
    }));

    if (answers.some((answer) => answer.answer_text.length < 3)) {
      setError("Please answer every agent question before submitting the round.");
      return;
    }

    try {
      setError("");
      setLoadingAction("submit");
      const response = await submitInterviewAnswers(interviewState.session_id, answers);
      setInterviewState((current) => ({ ...current, ...response }));
      setInterviewAnswers(buildAnswerMap(response.questions || []));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoadingAction("");
    }
  };

  return (
    <main className="app-shell">
      <div className="app-shell__backdrop" />
      <div className="app-shell__content">
        <Home>
          <section className="stage-indicator surface-card">
            <div className={`stage-indicator__item ${stage === "upload" ? "is-active" : ""}`}>
              1. Upload resume
            </div>
            <div className={`stage-indicator__item ${stage === "interview" ? "is-active" : ""}`}>
              2. Live interview
            </div>
          </section>

          {stage === "upload" && (
            <UploadForm
              form={form}
              resumeFile={resumeFile}
              onChange={updateForm}
              onFileChange={updateResumeFile}
              onAnalyze={handleAnalyze}
              onStartInterview={handleStartInterview}
              loadingAction={loadingAction}
            />
          )}

          {error && <div className="alert-banner">{error}</div>}

          {stage === "upload" && normalizedScreening && <Dashboard result={normalizedScreening} />}

          {interviewState && (
            <InterviewPanel
              interviewState={interviewState}
              answers={interviewAnswers}
              onAnswerChange={updateInterviewAnswer}
              onSubmitRound={handleSubmitInterviewRound}
              onRefreshStatus={refreshInterviewStatus}
              loadingAction={loadingAction}
            />
          )}
        </Home>
      </div>
    </main>
  );
}
