# services/segmentor/run_rules.py

from models.segmentation_rule import SegmentationRule
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from services.rag.sql_agent import execute_update_sql
from uuid import UUID

async def run_segmentation_rules(company_id: UUID, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(SegmentationRule).where(SegmentationRule.company_id == company_id)
    )
    rules = result.scalars().all()

    summary = []

    for rule in rules:
        query = f"""
            UPDATE products
            SET segment = '{rule.segment_name}'
            WHERE company_id = '{company_id}'
            AND ({rule.rule_expression})
        """
        try:
            msg = execute_update_sql(query)
            summary.append({
                "segment": rule.segment_name,
                "rule": rule.rule_expression,
                "status": "success",
                "result": msg
            })
        except Exception as e:
            summary.append({
                "segment": rule.segment_name,
                "rule": rule.rule_expression,
                "status": "error",
                "error": str(e)
            })

    return summary
