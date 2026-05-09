import json
from pathlib import Path

from app.database import KnowledgeItem, SessionLocal, create_db_and_tables


BASE_DIR = Path(__file__).resolve().parents[1]
SOP_SEED_PATH = BASE_DIR / "data" / "sop_seed.json"


def load_sop_seed_data() -> list[dict]:
    if not SOP_SEED_PATH.exists():
        raise FileNotFoundError(f"SOP seed file not found: {SOP_SEED_PATH}")

    with SOP_SEED_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def seed_sop_knowledge() -> None:
    create_db_and_tables()

    sop_items = load_sop_seed_data()
    db = SessionLocal()

    try:
        inserted_count = 0
        skipped_count = 0

        for item in sop_items:
            existing_item = (
                db.query(KnowledgeItem)
                .filter(
                    KnowledgeItem.entity == item["entity"],
                    KnowledgeItem.claim == item["claim"],
                    KnowledgeItem.source_type == item["source_type"],
                )
                .first()
            )

            if existing_item:
                skipped_count += 1
                continue

            knowledge_item = KnowledgeItem(
                entity=item["entity"],
                claim=item["claim"],
                condition=item.get("condition"),
                recommendation=item.get("recommendation"),
                source_type=item["source_type"],
                source_text=item.get("source_text"),
                confidence=item.get("confidence", 1.0),
                status=item.get("status", "approved"),
                risk_level=item.get("risk_level", "medium"),
                conflict_group_id=item.get("conflict_group_id"),
            )

            db.add(knowledge_item)
            inserted_count += 1

        db.commit()

        print("SOP seed completed.")
        print(f"Inserted: {inserted_count}")
        print(f"Skipped existing: {skipped_count}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_sop_knowledge()