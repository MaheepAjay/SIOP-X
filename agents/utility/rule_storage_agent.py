from models.document_rules import DocumentRules     
from uuid import uuid4
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from services.metadata_service import create_metadata_from_document_async

async def store_rules_to_db(
    rules: list,
    company_id: str,
    document_id: str,
    source_doc: str,
    db: AsyncSession
) -> List[str]:
    
    saved_rule_ids = []

    for rule in rules:
        metadata_id = await create_metadata_from_document_async(
            db=db,
            extracted_logic=rule,
            company_id=company_id
        )

        rule_id = str(uuid4())

        rule_obj = DocumentRules(
            id=rule_id,
            company_id=company_id,
            document_id=document_id,
            domain=rule.get("domain"),
            rule_type=rule.get("rule_type"),
            frequency=rule.get("frequency"),
            method=rule.get("method"),
            conditions=rule.get("conditions"),
            logic=rule.get("logic"),
            source_doc=source_doc,
            extracted_by=rule.get("extracted_by"),
            metadata_id=metadata_id
        )

        db.add(rule_obj)
        saved_rule_ids.append(rule_id)


    await db.commit()
    return saved_rule_ids
