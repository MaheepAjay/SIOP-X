# agents/utility/action_generator.py
from uuid import uuid4
from datetime import datetime
from typing import List, Optional
from models.analysis_agent import UserAction
from sqlalchemy.ext.asyncio import AsyncSession

async def generate_user_actions_from_rules(
    rules: List[dict],
    company_id: str,
    document_id: Optional[str],
    db: AsyncSession
):
    actions = []

    for rule in rules:
        action_id = str(uuid4())
        domain = rule.get("domain")
        method = rule.get("method")
        segment = rule.get("segment")
        rule_type = rule.get("rule_type")
        frequency = rule.get("frequency")
        trigger_type = "manual"

        # 🔧 Simple default action message generation
        if domain == "forecasting":
            action_type = "run_forecast"
            description = f"Forecast generation for segment '{segment}' using {method}."
        elif domain == "replenishment":
            action_type = "replenish_inventory"
            description = f"Replenishment action for segment '{segment}' using method: {method}."
        elif domain == "safety_stock":
            action_type = "calculate_safety_stock"
            logic = rule.get("logic", "formula")
            description = f"Calculate safety stock for '{segment}' using logic: {logic}."
        else:
            action_type = "review_rule"
            description = f"Review rule: {rule_type} in domain {domain}."

        db_action = UserAction(
            id=action_id,
            company_id=company_id,
            document_id=document_id,
            action_type=action_type,
            description=description,
            target_segment=segment,
            trigger_type=trigger_type,
            frequency=frequency,
            output_config_id=None,
            created_at=datetime.utcnow()
        )

        db.add(db_action)
        actions.append(db_action)

    await db.commit()
    return actions
