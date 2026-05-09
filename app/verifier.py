from dataclasses import dataclass
import re

from sqlalchemy.orm import Session

from app.database import KnowledgeItem
from app.schemas import ExtractedKnowledge, KnowledgeStatus, RiskLevel


@dataclass
class VerificationResult:
    status: KnowledgeStatus
    confidence: float
    reason: str
    conflicting_item_id: str | None = None


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    return text.lower().strip()


def extract_temperature_values(text: str | None) -> list[int]:
    """
    Extract simple Celsius temperature values from text.

    Examples:
    - "78°C" -> [78]
    - "85 C" -> [85]
    - "run at 80 degrees" -> [80]
    """
    if not text:
        return []

    patterns = [
        r"(\d+)\s*°c",
        r"(\d+)\s*c\b",
        r"(\d+)\s*degrees",
    ]

    values: list[int] = []

    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        values.extend(int(match) for match in matches)

    return values


def has_numeric_conflict(new_claim: str, existing_claim: str) -> bool:
    """
    Detect simple numeric conflicts, especially machine settings such as temperature.

    This is intentionally simple for the prototype.
    """
    new_values = extract_temperature_values(new_claim)
    existing_values = extract_temperature_values(existing_claim)

    if not new_values or not existing_values:
        return False

    return set(new_values) != set(existing_values)


def has_action_conflict(new_text: str, existing_text: str) -> bool:
    """
    Detect simple action-level conflict.

    Example:
    - SOP says stop the line.
    - Worker says ignore it.
    """
    new_text = normalize_text(new_text)
    existing_text = normalize_text(existing_text)

    unsafe_override_terms = [
        "ignore",
        "do not stop",
        "don't stop",
        "skip",
        "bypass",
        "without supervisor",
        "no supervisor",
    ]

    existing_requires_control = any(
        term in existing_text
        for term in ["stop", "supervisor", "maintenance", "designated charging area"]
    )

    new_bypasses_control = any(term in new_text for term in unsafe_override_terms)

    return existing_requires_control and new_bypasses_control


def find_conflicting_approved_item(
    extracted: ExtractedKnowledge,
    db: Session,
) -> KnowledgeItem | None:
    """
    Find an approved knowledge item in the same conflict group that conflicts
    with the extracted knowledge.
    """
    if not extracted.conflict_group_id:
        return None

    approved_items = (
        db.query(KnowledgeItem)
        .filter(KnowledgeItem.conflict_group_id == extracted.conflict_group_id)
        .filter(KnowledgeItem.status == KnowledgeStatus.APPROVED.value)
        .all()
    )

    new_combined_text = " ".join(
        part for part in [
            extracted.claim,
            extracted.condition,
            extracted.recommendation,
        ]
        if part
    )

    for item in approved_items:
        existing_combined_text = " ".join(
            part for part in [
                item.claim,
                item.condition,
                item.recommendation,
            ]
            if part
        )

        if has_numeric_conflict(new_combined_text, existing_combined_text):
            return item

        if has_action_conflict(new_combined_text, existing_combined_text):
            return item

    return None


def verify_extracted_knowledge(
    extracted: ExtractedKnowledge,
    db: Session,
) -> VerificationResult:
    """
    Decide whether extracted knowledge should be approved, pending review,
    or quarantined.

    This verifier is intentionally conservative:
    - Conflicts with approved SOP/knowledge are quarantined.
    - High-risk knowledge requires review.
    - Medium-risk worker knowledge is not auto-approved unless confidence is high.
    """
    conflicting_item = find_conflicting_approved_item(extracted, db)

    if conflicting_item is not None:
        return VerificationResult(
            status=KnowledgeStatus.QUARANTINED,
            confidence=min(extracted.confidence, 0.4),
            reason=(
                "The extracted knowledge conflicts with an existing approved "
                f"knowledge item in conflict group '{extracted.conflict_group_id}'."
            ),
            conflicting_item_id=conflicting_item.id,
        )

    if extracted.risk_level == RiskLevel.HIGH:
        return VerificationResult(
            status=KnowledgeStatus.PENDING_REVIEW,
            confidence=extracted.confidence,
            reason="High-risk operational knowledge requires supervisor review.",
        )

    if extracted.confidence < 0.75:
        return VerificationResult(
            status=KnowledgeStatus.PENDING_REVIEW,
            confidence=extracted.confidence,
            reason="Worker-provided knowledge has insufficient confidence for auto-approval.",
        )

    return VerificationResult(
        status=KnowledgeStatus.APPROVED,
        confidence=extracted.confidence,
        reason="No conflict detected and confidence is high enough for auto-approval.",
    )