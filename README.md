# 🛡️ Spectre — Forensic Document Intelligence Platform

**Spectre** is a production-grade document forgery and deepfake detection system designed to identify, localize, and classify tampering in scanned or digital documents. Unlike generative AI solutions, Spectre relies entirely on classical computer vision, signal processing, and traditional machine learning to deliver forensic-level accuracy.

![Spectre Dashboard Placeholder](https://via.placeholder.com/800x450/080B14/00F5D4?text=Spectre+Forensic+Intelligence+Dashboard)

## 📋 Table of Contents
- [Executive Summary](#-executive-summary)
- [Tampering Categories Detected](#-tampering-categories-detected)
- [Technology Stack](#-technology-stack)
- [Key Features](#-key-features)
- [Getting Started](#-getting-started)
- [Demo Runbook](#-demo-runbook)
- [Freeze Checklist](#-freeze-checklist)
- [Roadmap](#-roadmap)

---

## 🚀 Executive Summary
Spectre addresses the core challenge of identifying small, localized changes within documents—rather than whole-document classification. It applies a modular, multi-signal detection pipeline that produces precise bounding boxes, per-region tampering labels, and confidence scores.

The platform is built to be deployable for medical, financial, legal, and identity document verification where auditability and non-generative certainty are paramount.

## 🔍 Tampering Categories Detected
Spectre is designed to detect all 9 core categories of document tampering:
1.  **Copy-Paste Content:** ELA + SIFT/ORB patch matching.
2.  **Overwriting Text:** Ink density anomaly + noise variance maps.
3.  **Added Content:** Font fingerprinting + Laplacian of Gaussian edge detection.
4.  **Erasure / Removal:** Background continuity analysis + gap detection.
5.  **Merging Documents:** Scanner profile fingerprinting & baseline alignment.
6.  **Watermark Removal:** FFT ghost pattern analysis in the Fourier domain.
7.  **Irregular Spacing:** OCR typographic baseline & character-width statistics.
8.  **Fully AI-Generated:** Haralick texture features & frequency spectrum analysis.
9.  **Partial AI Edits:** Local vs global noise fingerprint mismatch.

## 💻 Technology Stack
| Layer | Technologies |
|---|---|
| **Frontend** | React, Vite, TailwindCSS, Zustand, Lucide Icons |
| **Backend** | FastAPI, Uvicorn |
| **Forensics** | OpenCV, scikit-image, PyMuPDF, SciPy, Pillow |
| **Analysis** | Tesseract OCR, NumPy, scikit-learn (SVM/Ensembles) |
| **Reporting** | ReportLab |

## ✨ Key Features
### 🖋️ Interactive Forensic Viewer
A dark-themed, cinematic dashboard that renders documents with color-coded bounding box overlays for each specific type of tampering found.

### 📊 Forensic Heatmaps
Visualize spatial distribution of suspicion scores across the document to identify high-risk zones at a glance.

### 🧬 Document DNA Fingerprinting
Assigns a unique forensic fingerprint to every document using perceptual hashing and scanner noise profiles to detect drift on re-submission.

### 📜 Tamper Timeline
Reconstructs the chronological order of modifications based on ELA compression layers and signal interaction patterns.

---

## 🛠️ Getting Started

### Prerequisites
- Node.js (v18+)
- npm or yarn

### Installation
1.  Clone the repository:
    ```bash
    git clone https://github.com/srinath-712/Spectre.git
    cd Spectre
    ```

2.  Install dependencies for the frontend:
    ```bash
    cd frontend
    npm install
    ```

3.  Run the development server:
    ```bash
    npm run dev
    ```

The dashboard will be available at `http://localhost:5173`.

### Backend startup
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🎬 Demo Runbook
Judge-mode demo and fallback operation steps are documented in:

- `docs/PHASE5C_RUNBOOK.md`

## 🧊 Freeze Checklist
Release-candidate freeze and public URL validation steps are documented in:

- `docs/PHASE5D_FREEZE.md`

---

## 🗺️ Roadmap
- [x] **Phase 1:** UI Shell, Design System, & Interactive Mockups.
- [x] **Phase 2:** Backend Core Pipeline (FastAPI & Document Ingestion).
- [x] **Phase 3:** Implementation of all 9 Forensic Detection Modules.
- [x] **Phase 4:** Forensic PDF Report Export & DNA Fingerprinting logic.
- [x] **Phase 5A-5C:** Integration, QA, Domain-Specific Tuning, and Demo Polish.
- [ ] **Phase 5D:** Freeze, tag release candidate, and final public URL validation.

---

## ⚖️ Constraint Compliance
Spectre strictly adheres to **No LLMs or Generative AI** constraints. All detection logic is rooted in deterministic signal processing and classical machine learning, ensuring outcomes are verifiable and explainable.

---

**Built for the Forensic Document Intelligence Hackathon.** 
*Submission Date: 8 April 2026*
