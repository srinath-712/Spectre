# Phase 5D Freeze Checklist

This checklist is for the release-candidate freeze before submission.

## 1. Code Freeze
1. Stop feature work.
2. Merge or rebase the final changes into the release branch.
3. Confirm the working tree is clean.
4. Record the final commit SHA for submission notes.

## 2. Release Tagging
1. Create the release candidate tag once the tree is clean.
2. Use a stable tag name such as `v1.0.0-rc1`.
3. Push the tag to the remote repository if required by the submission flow.

Example:

```bash
git tag v1.0.0-rc1
git push origin v1.0.0-rc1
```

## 3. Public URL Validation
Validate the deployed public URL from at least two networks.

### Required checks
1. Open the frontend on a non-local machine or secondary browser profile.
2. Upload a PDF and confirm analysis completes.
3. Open the report export flow.
4. Toggle adversarial mode after completion.
5. Click New Analysis and confirm the upload state resets.
6. Repeat the same flow from a mobile hotspot or cellular network.

### Endpoints to confirm
- `/health`
- `/docs`
- `/api/analyze`
- `/api/result/{job_id}`
- `/api/report/{job_id}`
- `/api/adversarial`
- `/api/fingerprint`

## 4. Local Fallback Validation
Keep a local fallback available in case the public deployment is unreachable.

### Backend
```powershell
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

### Smoke test
1. Open `http://localhost:5173`.
2. Confirm the upload flow works.
3. Run one Judge Demo Pack sample.
4. Export the report.

## 5. Submission Notes
1. Capture the public URL and tag in the final handoff.
2. Mention the local fallback instructions.
3. Mention the demo pack and runbook locations.
