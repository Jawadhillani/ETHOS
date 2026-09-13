# ETHOS
**Ethical Trust & Holistic Oversight System**

A facial biometric recognition system with built-in AI-powered fairness auditing, designed for EU AI Act compliance.

## Key Results

| Metric | Value |
|--------|-------|
| EER (Equal Error Rate) | **0.30%** |
| AUC | **0.9994** |
| Race FMRD (fairness gap) | **9.19×** |
| Age FMRD (fairness gap) | **42.30×** |

> FMRD (Fairness-weighted Match Rate Disparity) measures recognition gap across demographic subgroups — lower is fairer.

## Overview

ETHOS is a full-stack biometric pipeline that combines state-of-the-art face recognition with demographic fairness analysis. It detects, embeds, matches, and audits facial biometrics — flagging bias across gender, age, and ethnicity groups in compliance with EU AI Act requirements.

## Features

- **Face Detection** — RetinaFace-based detector
- **Face Recognition** — IResNet/ArcFace embeddings (512-d)
- **1:1 Verification & 1:N Identification** — cosine similarity + CMC ranking
- **Fairness Auditing** — FMRD metric across demographic subgroups
- **Anti-Spoofing (PAD)** — MiniFASNetV2 liveness detection via webcam
- **Robustness Testing** — domain perturbation evaluation
- **Full-Stack App** — React frontend + FastAPI backend + Gradio GUI

## Project Structure

```
src/
├── detection/       # RetinaFace face detector
├── embeddings/      # ArcFace IResNet embeddings
├── fairness/        # FMRD fairness auditor
├── matching/        # Cosine similarity + threshold engine
├── security/        # Anti-spoofing (PAD)
├── robustness/      # Domain generalization evaluation
└── visualization/   # Plots and audit reports
backend/             # FastAPI REST API
frontend/            # React + Vite dashboard
gui/                 # Gradio interface
```

## Tech Stack

- **Python** — PyTorch, ONNX Runtime, OpenCV, NumPy
- **Backend** — FastAPI, Uvicorn
- **Frontend** — React, Vite, Tailwind CSS, Plotly
- **ML Models** — ArcFace (IResNet-100), RetinaFace, MiniFASNetV2

## Setup

```bash
# Python dependencies
pip install -r requirements.txt

# Frontend
cd frontend && npm install && npm run dev

# Backend
uvicorn backend.main:app --reload
```

## Project Status

Active development — Master's project at UPEC, Spring 2026

## Author

Jawad Hillani
