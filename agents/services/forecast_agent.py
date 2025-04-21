# services/agents/forecast_agent.py

from models.analysis_agent import UserAction

async def run_forecast(action: UserAction):
    print("📈 Running Forecasting Agent...")
    print(f"🔧 Rule: {action.description}")
    
    # Dummy output
    return {
        "action": "forecast",
        "status": "success",
        "details": "Forecasted 120 units for Product-A using 3MA"
    }
