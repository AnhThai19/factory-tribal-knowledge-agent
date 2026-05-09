from app.schemas import ExtractedKnowledge, RiskLevel


def normalize_text(text: str) -> str:
    return text.lower().strip()


def extract_knowledge_from_transcript(transcript: str) -> ExtractedKnowledge | None:
    """
    Rule-based extractor for the prototype.

    In a production version, this module can be replaced or extended with an LLM-based
    JSON extractor. For this take-home prototype, rule-based extraction makes the
    demo deterministic and easy to evaluate.
    """
    text = normalize_text(transcript)

    if "hotel a polyester" in text:
        return ExtractedKnowledge(
            entity="hotel_a_polyester",
            claim="Hotel A polyester shrinks when processed together with cotton.",
            condition="normal cotton cycle or mixed cotton-polyester cycle",
            recommendation="Run Hotel A polyester separately or use a gentler polyester cycle.",
            confidence=0.68,
            risk_level=RiskLevel.MEDIUM,
            conflict_group_id="hotel_a_polyester_cycle",
        )

    if "dryer station 3" in text and ("85" in text or "85°c" in text):
        return ExtractedKnowledge(
            entity="dryer_station_3",
            claim="Dryer station 3 is often run at 85°C when cotton batches are still wet.",
            condition="cotton batch remains wet after standard cycle",
            recommendation="Increase dryer station 3 to 85°C only after supervisor review because it differs from SOP.",
            confidence=0.58,
            risk_level=RiskLevel.MEDIUM,
            conflict_group_id="dryer_station_3_temperature",
        )

    if "packaging line 2" in text and "sensor" in text:
        return ExtractedKnowledge(
            entity="packaging_line_2",
            claim="Packaging line 2 should be stopped when the sensor error light stays on.",
            condition="sensor error light remains on",
            recommendation="Stop packaging line 2 and notify maintenance.",
            confidence=0.82,
            risk_level=RiskLevel.HIGH,
            conflict_group_id="packaging_line_2_sensor_error",
        )

    if "welding station 3" in text and ("overheat" in text or "overheats" in text):
        return ExtractedKnowledge(
            entity="welding_station_3",
            claim="Welding station 3 may overheat after Tuesday lunch.",
            condition="Tuesday after lunch",
            recommendation="Reduce current by 5 percent only with supervisor approval.",
            confidence=0.62,
            risk_level=RiskLevel.HIGH,
            conflict_group_id="welding_station_3_current",
        )

    if "forklift" in text and "batter" in text:
        return ExtractedKnowledge(
            entity="forklift_battery_charging",
            claim="Forklift batteries should not be charged near the production floor.",
            condition="forklift battery charging",
            recommendation="Move forklift batteries to the designated charging area before charging.",
            confidence=0.86,
            risk_level=RiskLevel.HIGH,
            conflict_group_id="forklift_battery_safety",
        )

    return None