# services/blueprint/fetch.py

from fastapi import Depends
from models.standard_blueprint import StandardBlueprint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Tuple, Dict, Any


async def get_blueprint_by_agent_type(agent_type: str, db: AsyncSession):
    result = await db.execute(
        select(StandardBlueprint).where(StandardBlueprint.agent_type == agent_type)
    )
    return result.scalar_one_or_none()


# services/blueprint/compare.py

async def compare_config_to_blueprint(
    agent_config: Dict[str, Any],
    standard_blueprint: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    """
    Compares user-defined agent config with standard blueprint.

    Returns:
    - matched_method_name: name of the matched method (e.g., "MinMax")
    - deviations: fields that differ or were missing in the user config
    - merged_config: final config with defaults filled in
    """

    user_method = agent_config.get("method_name", "").lower()
    methods = standard_blueprint.get("methods", [])
    matched_method = None

    # Step 1: Match method by name
    for method in methods:
        if method["method_name"].lower() == user_method:
            matched_method = method
            break

    if not matched_method:
        # fallback: use default method
        matched_method = next((m for m in methods if m.get("default")), None)
        user_method = matched_method["method_name"]

    deviations = {}
    merged_config = {}

    method_params = matched_method.get("parameters", {})
    user_params = agent_config.get("customizations", {})

    # Step 2: Compare each parameter and fill with default if needed
    for param_name, param_spec in method_params.items():
        user_value = user_params.get(param_name)
        default_value = param_spec.get("default")

        if user_value is None:
            if param_spec.get("required", False):
                deviations[param_name] = {
                    "status": "missing, using default",
                    "default_used": default_value
                }
            merged_config[param_name] = default_value
        else:
            if default_value is not None and user_value != default_value:
                deviations[param_name] = {
                    "status": "deviation",
                    "user_value": user_value,
                    "expected_default": default_value
                }
            merged_config[param_name] = user_value

    return user_method, deviations, merged_config
