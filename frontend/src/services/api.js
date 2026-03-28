import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  timeout: 30000,
});

function getErrorMessage(error) {
  if (error.response?.data?.detail) {
    return String(error.response.data.detail);
  }

  if (error.response?.data?.message) {
    return String(error.response.data.message);
  }

  return error.message || "Request failed.";
}

export async function evaluateCandidate(payload) {
  try {
    const formData = new FormData();
    formData.append("resume_file", payload.resume_file);
    formData.append("jd_text", payload.jd_text);

    const { data } = await api.post("/api/hiring/evaluate", formData);
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function startInterview(payload) {
  try {
    const formData = new FormData();
    formData.append("resume_file", payload.resume_file);
    formData.append("jd_text", payload.jd_text);
    formData.append("candidate_name", payload.candidate_name);
    formData.append("max_rounds", String(payload.max_rounds));

    const { data } = await api.post("/api/hiring/interview/start", formData);
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function submitInterviewAnswers(sessionId, answers) {
  try {
    const { data } = await api.post(`/api/hiring/interview/${sessionId}/respond`, {
      answers,
    });
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function getInterviewStatus(sessionId) {
  try {
    const { data } = await api.get(`/api/hiring/interview/${sessionId}/status`);
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}
