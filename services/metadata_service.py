# services/metadata/metadata_service.py

from models.metadata import AgentMetadata
from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime

def create_metadata(
    db: Session,
    company_id: str,
    segment: Optional[str] = None,
    location_id: Optional[str] = None,
    product_id: Optional[str] = None,
    policy_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    additional_info: Optional[Dict] = None
) -> AgentMetadata:
    metadata = AgentMetadata(
        company_id=company_id,
        segment=segment,
        location_id=location_id,
        product_id=product_id,
        policy_id=policy_id,
        start_date=start_date,
        end_date=end_date,
        additional_info=additional_info
    )
    db.add(metadata)
    db.commit()
    db.refresh(metadata)
    return metadata


def create_metadata_from_user_query(db: Session, user_payload: Dict) -> AgentMetadata:
    return create_metadata(
        db=db,
        company_id=user_payload["company_id"],
        segment=user_payload.get("segment"),
        location_id=user_payload.get("location_id"),
        product_id=user_payload.get("product_id"),
        start_date=user_payload.get("start_date"),
        end_date=user_payload.get("end_date"),
        additional_info=user_payload.get("additional_info", {})
    )


def create_metadata_from_document(
    db: Session,
    extracted_logic: Dict,
    company_id: str
) -> AgentMetadata:
    return create_metadata(
        db=db,
        company_id=company_id,
        segment=extracted_logic.get("segment"),
        location_id=extracted_logic.get("location_id"),
        product_id=extracted_logic.get("product_id"),
        policy_id=extracted_logic.get("policy_id"),
        start_date=extracted_logic.get("start_date"),
        end_date=extracted_logic.get("end_date"),
        additional_info={"source": "document"}
    )

# services/metadata/metadata_service_async.py

from models.metadata import AgentMetadata
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from datetime import datetime
from typing import Optional, Dict
import uuid

async def create_metadata_from_document_async(
    db: AsyncSession,
    extracted_logic: Dict,
    company_id: str
) -> uuid.UUID:
    """
    Creates a new metadata row and returns its ID.
    """
    stmt = insert(AgentMetadata).values(
        id=uuid.uuid4(),
        company_id=company_id,
        segment=extracted_logic.get("segment"),
        location_id=extracted_logic.get("location_id"),
        product_id=extracted_logic.get("product_id"),
        policy_id=extracted_logic.get("policy_id"),
        start_date=extracted_logic.get("start_date"),
        end_date=extracted_logic.get("end_date"),
        additional_info={"source": "document"},
        created_at=datetime.utcnow()
    ).returning(AgentMetadata.id)

    result = await db.execute(stmt)
    metadata_id = result.scalar_one()
    return metadata_id
