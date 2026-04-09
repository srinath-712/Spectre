# Phase 5C Judge Runbook

This runbook is for live demos and fallback operation.

## 1. Demo Story (6-8 minutes)
1. Open Spectre and select domain based on the sample scenario.
2. Use Sidebar -> Judge Demo Pack and click one sample:
   - Medical Dosage Patch
   - Financial Overwrite
   - Legal Clause Swap
3. Wait for analysis completion and walk through:
   - Verdict badge and confidence
   - Bounding boxes in the viewer
   - Findings list details
   - Tamper timeline with Laser Sync
4. Click timeline steps to show region linking behavior.
5. Toggle Adversarial Test Mode to show robustness under perturbation.
6. Export report and show generated PDF output.

## 2. Adversarial Showcase Script (talk track)
- Baseline: "This is the original document analysis with localized findings."
- Perturbation: "Now I enable adversarial mode to add realistic noise attacks."
- Resilience: "Notice detections remain available and confidence shifts are visible, not hidden."
- Auditability: "All findings are deterministic and reportable without LLM generation."

## 3. Public URL Demo Flow
Use this when internet is stable and judges need direct access.

### Backend
1. Deploy backend container/app to a public host.
2. Confirm these endpoints respond externally:
   - /health
   - /docs
   - /api/analyze
   - /api/result/{job_id}
   - /api/report/{job_id}
3. Set CORS for the frontend origin.

### Frontend
1. Build and deploy static frontend.
2. Configure environment:
   - VITE_API_BASE_URL=https://your-public-api/api
   - VITE_BACKEND_DOCS_URL=https://your-public-api/docs
3. Smoke test from a second network (mobile hotspot).

## 4. Local Fallback Demo Flow
Use this when public connectivity is unstable.

### Start backend
From project root:

```powershell
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start frontend
From project root:

```powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

### Verify
1. Open http://localhost:5173
2. Open API docs at http://localhost:8000/docs
3. Run one Judge Demo Pack sample and export report.

## 5. Pre-demo Checklist
1. Backend /health returns ok.
2. Frontend can upload and complete at least one sample.
3. Adversarial mode toggle works after completion.
4. Report export opens a PDF.
5. New Analysis button clears state without page refresh.
