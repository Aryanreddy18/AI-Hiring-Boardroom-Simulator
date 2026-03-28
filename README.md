# AI Hiring Boardroom Simulator

AI-powered hiring workflow with:
- Resume upload and JD screening
- Multi-agent interview rounds (`tech`, `manager`, `hr`)
- Supervisor moderation and final hire/hold/reject decision
- Live interview UI with webcam preview and agent question prompts

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: React + Vite

## Project Structure

```text
backend/
  app.py
  routes/hiring.py
  core/
  agents/
frontend/
  src/
requirements.txt
package.json
vite.config.js
```

## Prerequisites

- Python 3.10+
- Node.js 18+

## Backend Setup

```powershell
python -m venv venv
.\venv\Scripts\python -m pip install -r requirements.txt
.\venv\Scripts\python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

Health check:

```powershell
curl http://127.0.0.1:8000/health
```

## Frontend Setup

In a new terminal:

```powershell
npm install
npm run dev
```

Vite runs from `frontend/` (configured in `vite.config.js`) and proxies `/api` to `http://127.0.0.1:8000`.

## How to Use

1. Open the app (usually `http://localhost:3000`).
2. Upload resume file (`.pdf`, `.docx`, `.doc`, `.txt`, `.md`, `.rtf`).
3. Enter job description text (minimum 20 characters).
4. Optional: edit candidate name and max rounds (1-3).
5. Click `Run screening` for initial panel evaluation.
6. Click `Start interview` to enter live interview stage:
   - Webcam preview is enabled in-browser.
   - Agents ask round questions.
   - Submit answers each round.
7. Review final supervisor decision and transcript.

## API Endpoints

- `GET /health`
- `POST /api/hiring/evaluate` (multipart form: `resume_file`, `jd_text`)
- `POST /api/hiring/interview/start` (multipart form: `resume_file`, `jd_text`, `candidate_name`, `max_rounds`)
- `POST /api/hiring/interview/{session_id}/respond`
- `GET /api/hiring/interview/{session_id}/status`

## Environment Variables

Optional:

- `FEATHERLESS_API_KEY`: enables LLM-generated interview questions
- `CORS_ALLOW_ORIGINS`: comma-separated frontend origins
- `INTERVIEW_SESSION_TTL_SECONDS`
- `INTERVIEW_MAX_SESSIONS`

If `FEATHERLESS_API_KEY` is not set or fails, the system falls back to rule-based questions.

## Troubleshooting

### `http proxy error ... ECONNREFUSED 127.0.0.1:8000`
Backend is not running. Start FastAPI first:

```powershell
.\venv\Scripts\python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

### `Request failed with status code 500`
- Check backend terminal logs for traceback.
- Ensure dependencies are installed from `requirements.txt`.
- Verify uploaded resume has readable text content.

### Vite/esbuild platform mismatch
If dependencies were copied from another OS, reinstall locally:

```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json
npm install
```

## Notes

- Webcam requires browser permission and HTTPS/localhost context.
- Keep backend and frontend terminals running during development.
