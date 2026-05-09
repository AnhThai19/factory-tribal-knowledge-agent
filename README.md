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

## Current Status

- [x] Project skeleton
- [x] FastAPI health check
- [x] SQLite knowledge schema
- [x] SOP seed data
- [x] Knowledge extraction
- [x] Verification and conflict detection
- [ ] ChromaDB retrieval
- [ ] Agent answer endpoint
- [ ] Evaluation script
- [ ] Slide deck

## Seed SOP Knowledge

This project includes a small set of approved SOP knowledge items in `data/sop_seed.json`.

To seed the database:

```bash
python scripts/seed_db.py
```


## Knowledge Extraction

The prototype currently uses a deterministic rule-based extractor for sample worker transcripts.

This is intentional for the first version:

- It makes the demo deterministic.
- It avoids LLM API dependency during core workflow testing.
- The extractor is isolated in `app/extractor.py`, so it can later be replaced with an LLM-based JSON extractor.

Example request:

```json
{
  "conversation_id": "conv_001",
  "worker_id": "worker_a",
  "transcript": "For Hotel A polyester, don't run it with cotton. It shrinks if you use the normal cotton cycle."
}
```

Example extracted knowledge:
```json
{
  "entity": "hotel_a_polyester",
  "claim": "Hotel A polyester shrinks when processed together with cotton.",
  "condition": "normal cotton cycle or mixed cotton-polyester cycle",
  "recommendation": "Run Hotel A polyester separately or use a gentler polyester cycle.",
  "confidence": 0.68,
  "status": "candidate"
}
```

## Verification and Conflict Detection

After knowledge is extracted from a worker transcript, it is not immediately used by the agent.

The verifier checks the extracted knowledge against approved SOP knowledge using `conflict_group_id`.

Current prototype rules:

| Condition | Decision |
|---|---|
| Conflicts with approved SOP knowledge | `quarantined` |
| High-risk operational knowledge | `pending_review` |
| Worker knowledge with confidence below 0.75 | `pending_review` |
| No conflict and high confidence | `approved` |

This staged workflow helps prevent self-poisoning. The agent will only retrieve knowledge that has been explicitly approved.


### Example: Conflict with SOP

SOP knowledge:

```text
Dryer station 3 should run at 78°C for standard cotton cycles.
```


Worker says:
```
Dryer station 3 is usually better at 85°C for cotton.
```

Verifier result:
```json
{
  "verification_status": "quarantined",
  "verification_reason": "The extracted knowledge conflicts with an existing approved knowledge item in conflict group 'dryer_station_3_temperature'."
}
```