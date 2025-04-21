# services/agents/agent_dispatcher.py

from agents.services.replenishment_agent import run_replenishment
from agents.services.forecast_agent import run_forecast

async def run_user_action(action):
    action_type = action.action_type
    print(f"🚀 Running action: {action_type}")

    if action_type == "replenishment":
        return await run_replenishment(action)
    
    elif action_type == "forecast":
        return await run_forecast(action)

    # Add more action types as needed
    else:
        raise ValueError(f"Unsupported action_type: {action_type}")
