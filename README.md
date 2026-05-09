# Factory Knowledge Agent

A prototype system for learning operational knowledge from factory worker conversations.

## Problem

Factory workers often hold important operational knowledge that is not written in SOPs, manuals, or policy documents. This project explores how an AI agent can safely learn from worker conversations without poisoning its own knowledge base.

## What This Prototype Focuses On

This prototype focuses on the core knowledge learning pipeline:

1. Capture worker conversation transcripts.
2. Extract structured knowledge candidates.
3. Verify new knowledge against existing SOP knowledge.
4. Detect conflicts and unsafe claims.
5. Store approved knowledge for retrieval.
6. Use approved knowledge to answer future questions.
7. Evaluate whether the agent improves after learning.

Voice input is simulated as text transcripts in this version. The main challenge is not speech recognition, but safe knowledge acquisition, integration, and evaluation.

## Planned Architecture

```text
Worker Transcript
      ↓
Knowledge Extractor
      ↓
Verifier & Conflict Checker
      ↓
Knowledge Status Workflow
(candidate / pending_review / approved / quarantined / rejected)
      ↓
SQLite Knowledge Store + ChromaDB Vector Index
      ↓
Retriever
      ↓
Agent Answer
      ↓
LLM-as-Judge Evaluation
```
How to Run
```
python -m venv .venv
```

Activate environment:
```
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```
Install dependencies:
```
pip install -r requirements.txt
```
Run API:
```
uvicorn app.main:app --reload
```
Open:
```
http://127.0.0.1:8000/docs
```
