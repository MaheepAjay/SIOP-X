
from openai import OpenAI
from core.config import settings
from typing import List, Dict

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class ForecastDiagnosticAgent:
    def __init__(self):
        self.model = "gpt-4"

    async def explain_forecast(
        self,
        product_id: str,
        location_id: str,
        sales_history: List[float],
        forecast_result: List[float],
        method_used: str,
        params_used: Dict
    ) -> Dict:
        prompt = f"""
        You are a forecasting analyst.

        Help explain the forecast result below to a business user:
        - Product ID: {product_id}
        - Location ID: {location_id}
        - Historical sales data: {sales_history}
        - Forecast result: {forecast_result}
        - Method used: {method_used}
        - Parameters used: {params_used}

        Please answer:
        1. Why was this method suitable for this data?
        2. What assumptions does it make?
        3. Is the forecast pattern valid and reliable?
        4. What could improve the forecast?

        Return in JSON:
        {{
          "method_rationale": "...",
          "assumptions": "...",
          "forecast_reliability": "...",
          "improvement_suggestions": "..."
        }}
        """

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    { "role": "system", "content": "You are a forecast diagnostic expert." },
                    { "role": "user", "content": prompt }
                ]
            )
            content = response.choices[0].message.content.strip()
            return eval(content)  # You can replace with safe_json_parse
        except Exception as e:
            print(f"❌ Diagnostic LLM error: {e}")
            return {
                "method_rationale": "Unable to explain due to LLM error.",
                "assumptions": "N/A",
                "forecast_reliability": "Unknown",
                "improvement_suggestions": "Retry with cleaned data or try another method."
            }
