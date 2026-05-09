from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import KnowledgeItem, create_db_and_tables, get_db
from app.extractor import extract_knowledge_from_transcript
from app.schemas import (
    ConversationIngestRequest,
    IngestConversationResponse,
    KnowledgeCreate,
    KnowledgeRead,
    KnowledgeStatus,
    SourceType,
)
from app.verifier import verify_extracted_knowledge


app = FastAPI(
    title=settings.app_name,
    description=(
        "A prototype factory knowledge learning agent that captures, "
        "verifies, and retrieves operational knowledge from worker conversations."
    ),
    version="0.1.0",
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {
        "message": "Factory Knowledge Agent API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "env": settings.app_env
    }


@app.post("/knowledge", response_model=KnowledgeRead)
def create_knowledge_item(
    payload: KnowledgeCreate,
    db: Session = Depends(get_db)
):
    item = KnowledgeItem(
        entity=payload.entity,
        claim=payload.claim,
        condition=payload.condition,
        recommendation=payload.recommendation,
        source_type=payload.source_type.value,
        source_text=payload.source_text,
        confidence=payload.confidence,
        status=payload.status.value,
        risk_level=payload.risk_level.value,
        conflict_group_id=payload.conflict_group_id,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@app.get("/knowledge", response_model=List[KnowledgeRead])
def list_knowledge_items(
    status: KnowledgeStatus | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(KnowledgeItem)

    if status is not None:
        query = query.filter(KnowledgeItem.status == status.value)

    return query.order_by(KnowledgeItem.created_at.desc()).all()


@app.get("/knowledge/{knowledge_id}", response_model=KnowledgeRead)
def get_knowledge_item(
    knowledge_id: str,
    db: Session = Depends(get_db)
):
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == knowledge_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Knowledge item not found")

    return item


@app.post("/knowledge/{knowledge_id}/approve", response_model=KnowledgeRead)
def approve_knowledge_item(
    knowledge_id: str,
    db: Session = Depends(get_db)
):
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == knowledge_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Knowledge item not found")

    item.status = KnowledgeStatus.APPROVED.value
    db.commit()
    db.refresh(item)

    return item


@app.post("/knowledge/{knowledge_id}/quarantine", response_model=KnowledgeRead)
def quarantine_knowledge_item(
    knowledge_id: str,
    db: Session = Depends(get_db)
):
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == knowledge_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Knowledge item not found")

    item.status = KnowledgeStatus.QUARANTINED.value
    db.commit()
    db.refresh(item)

    return item


@app.post("/knowledge/{knowledge_id}/reject", response_model=KnowledgeRead)
def reject_knowledge_item(
    knowledge_id: str,
    db: Session = Depends(get_db)
):
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == knowledge_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Knowledge item not found")

    item.status = KnowledgeStatus.REJECTED.value
    db.commit()
    db.refresh(item)

    return item


@app.post("/ingest/conversation", response_model=IngestConversationResponse)
def ingest_conversation(
    payload: ConversationIngestRequest,
    db: Session = Depends(get_db)
):
    extracted = extract_knowledge_from_transcript(payload.transcript)

    if extracted is None:
        raise HTTPException(
            status_code=422,
            detail="No operational knowledge could be extracted from this transcript."
        )

    verification = verify_extracted_knowledge(extracted, db)

    item = KnowledgeItem(
        entity=extracted.entity,
        claim=extracted.claim,
        condition=extracted.condition,
        recommendation=extracted.recommendation,
        source_type=SourceType.WORKER_CONVERSATION.value,
        source_text=(
            f"conversation_id={payload.conversation_id}; "
            f"worker_id={payload.worker_id}; "
            f"transcript={payload.transcript}; "
            f"verification_reason={verification.reason}; "
            f"conflicting_item_id={verification.conflicting_item_id}"
        ),
        confidence=verification.confidence,
        status=verification.status.value,
        risk_level=extracted.risk_level.value,
        conflict_group_id=extracted.conflict_group_id,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return IngestConversationResponse(
        knowledge=item,
        verification_status=verification.status,
        verification_reason=verification.reason,
        conflicting_item_id=verification.conflicting_item_id,
    )

