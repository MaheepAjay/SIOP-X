from openai import OpenAI
from api.utils.json_parser import safe_json_parse
from core.config import settings
from typing import List, Dict

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class PreForecastAgent:
    def __init__(self):
        self.model = "gpt-4"

    async def recommend_forecasting_policy(
        self,
        product_id: str,
        location_id: str,
        sales_history: List[float],
        user_horizon: int = 12
    ) -> Dict:
        prompt = f"""
        You are a forecasting strategy expert.

        Analyze the sales history and recommend the best forecasting method.

        - Product ID: {product_id}
        - Location ID: {location_id}
        - Sales history (monthly): {sales_history}
        - Desired forecast horizon: {user_horizon} months

        Available methods:
        - moving_average
        - linear_regression
        - exponential_smoothing
        - seasonal_decomposition
        - llm
        - custom

        Return only a valid JSON object (no comments, no markdown). Example:
        {{
            "recommended_method": "linear_regression",
            "reason": "Sales show a trend...",
            "recommended_params": {{
                "horizon": 12,
                "frequency": "monthly"
            }}
        }}
        """

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    { "role": "system", "content": "You are a forecasting strategy assistant." },
                    { "role": "user", "content": prompt }
                ]
            )

            content = response.choices[0].message.content.strip()
            print("🔍 LLM raw response:", content)

            return safe_json_parse(content, fallback={
                "recommended_method": "moving_average",
                "reason": "Could not parse LLM response. Fallback applied.",
                "recommended_params": {
                    "window": 3,
                    