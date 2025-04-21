
from openai import OpenAI
from core.config import settings
from agents.forecast.forecast_agent import ForecastingAgent
from agents.forecast.preforecast_agent import PreForecastAgent
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class ForecastPlanningChain:
    def __init__(self, company_id: UUID, db: AsyncSession, blueprint: dict):
        self.company_id = company_id
        self.db = db
        self.blueprint = blueprint
        self.forecasting_agent = ForecastingAgent(company_id, db, blueprint)
        self.preforecast_agent = PreForecastAgent()

    async def run_chain(self, product_id: str, location_id: str, sales_history: list, user_horizon: int = 12):
        # 🔹 Step 1: Use PreForecastAgent to get best method
        recommendation = await self.preforecast_agent.recommend_forecasting_policy(
            product_id=product_id,
            location_id=location_id,
            sales_history=sales_history,
            user_horizon=user_horizon
        )

        # 🔹 Step 2: Update product.policy_parameters manually or return suggestion
        recommended_method = recommendation.get("recommended_method", "moving_average")
        recommended_params = recommendation.get("recommended_params", {})

        # 🔹 Step 3: Override product policy with recommendation (demo use)
        policy_override = {
            "method": recommended_method,
            "params": recommended_params,
            "forecast_horizon": user_horizon
        }

        # 🔹 Step 4: Run Forecasting Agent using injected policy
        # We override product fetch and inject policy inline for demo
        product_stub = {
            "product_id": product_id,
            "location_id": location_id,
            "segment": "NA",
            "policy_parameters": policy_override
        }

        results = await self.forecasting_agent.run_on_single_product(product_stub)
        return {
            "recommendation": recommendation,
            "forecast_results": results
        }
