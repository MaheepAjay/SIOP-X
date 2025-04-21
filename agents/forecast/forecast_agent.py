
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
from uuid import UUID
import uuid
import math
from typing import List, Dict
import numpy as np
from sklearn.linear_model import LinearRegression
from openai import OpenAI
from core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# --------------------------------------
# ✅ Utilities
# --------------------------------------

def merge_forecasting_policy(method_name: str, blueprint: dict, segment_policy: dict, product_policy: dict) -> tuple[dict, int]:
    method = next((m for m in blueprint["methods"] if m["name"] == method_name), None)
    if not method:
        raise ValueError(f"Method '{method_name}' not found in blueprint")

    merged = {}
    for param, meta in method["parameters"].items():
        default = meta.get("default")
        value = default
        if meta.get("overridable") and param in segment_policy.get("params", {}):
            value = segment_policy["params"][param]
        if meta.get("overridable") and param in product_policy.get("params", {}):
            value = product_policy["params"][param]
        merged[param] = value

    user_horizon = product_policy.get("forecast_horizon") or segment_policy.get("forecast_horizon") or method.get("parameters", {}).get("forecast_periods", {}).get("default", 3)
    max_horizon = method.get("max_horizon", 36)
    final_horizon = min(user_horizon, max_horizon)
    return merged, final_horizon


def parse_forecast_response(text: str) -> List[float]:
    try:
        return eval(text.strip())
    except Exception as e:
        print(f"❌ LLM output parse error: {e}")
        return []

# --------------------------------------
# ✅ Forecasting Agent
# --------------------------------------

class ForecastingAgent:
    def __init__(self, company_id: UUID, db: AsyncSession, blueprint: dict):
        self.company_id = company_id
        self.db = db
        self.blueprint = blueprint

    async def run(self, default_horizon: int = 3):
        products = await self.fetch_products()
        results = []

        for product in products:
            segment_policy = await self.get_segment_policy(product["segment"])
            product_policy = product.get("policy_parameters") or {}
            method = product_policy.get("method") or segment_policy.get("method") or self.blueprint.get("default_method", "llm")

            merged_params, forecast_horizon = merge_forecasting_policy(method, self.blueprint, segment_policy, product_policy)
            sales = await self.get_sales_data(product["product_id"], product["location_id"])

            try:
                if method == "llm":
                    forecast = await self.run_llm_forecast(product, sales, merged_params, forecast_horizon)
                elif method == "moving_average":
                    forecast = self.run_moving_average(sales, merged_params, forecast_horizon)
                elif method == "linear_regression":
                    forecast = self.run_linear_regression(sales, forecast_horizon)
                elif method == "seasonal_decomposition":
                    forecast = self.run_seasonal_decomposition(sales, merged_params, forecast_horizon)
                elif method == "exponential_smoothing":
                    forecast = self.run_exponential_smoothing(sales, merged_params, forecast_horizon)
                elif method == "custom":
                    forecast = await self.run_custom_logic(product, sales, merged_params, forecast_horizon)
                else:
                    forecast = [0.0] * forecast_horizon
            except Exception as e:
                print(f"⚠️ Method '{method}' failed: {e}")
                forecast = [0.0] * forecast_horizon

            for i, qty in enumerate(forecast):
                forecast_month = (datetime.utcnow() + timedelta(days=30 * i)).replace(day=1).date()
                await self.save_forecast(
                    product_id=product["product_id"],
                    location_id=product["location_id"],
                    forecast_date=forecast_month,
                    forecast_qty=qty,
                    method=method
                )
                results.append({
                    "product_id": str(product["product_id"]),
                    "forecast": qty,
                    "month": forecast_month
                })

        await self.db.commit()
        return results

    async def fetch_products(self):
        result = await self.db.execute(text("""
            SELECT p.product_id, p.segment, p.location_id, p.policy_parameters
            FROM products p
            WHERE p.company_id = :company_id
        """), {"company_id": str(self.company_id)})
        return result.mappings().all()

    async def get_segment_policy(self, segment_name: str):
        result = await self.db.execute(text("""
            SELECT policy_parameters
            FROM segment_policies
            WHERE segment_name = :segment_name AND company_id = :company_id
        """), {"segment_name": segment_name, "company_id": str(self.company_id)})
        row = result.mappings().first()
        return row["policy_parameters"] if row else {}

    async def get_sales_data(self, product_id: UUID, location_id: UUID):
        result = await self.db.execute(text("""
            SELECT order_date, quantity
            FROM sales_orders
            WHERE product_id = :product_id AND location_id = :location_id
            ORDER BY order_date ASC
        """), {"product_id": str(product_id), "location_id": str(location_id)})
        return [r["quantity"] for r in result.mappings().all()]

    async def run_llm_forecast(self, product, sales: List[float], params: Dict, horizon: int):
        context_window = params.get("context_window", 8)
        trimmed_sales = sales[-context_window:] if context_window > 0 else sales

        prompt = f"""
        You are a demand planner. Based on this sales history, forecast the next {horizon} months.

        Product ID: {product["product_id"]}
        Location ID: {product["location_id"]}
        Sales history: {trimmed_sales}

        Return only a list like: [100, 105, 110]
        """
        response = client.chat.completions.create(
            model=params.get("model", "gpt-4"),
            messages=[{"role": "system", "content": "You are a forecasting expert."},
                      {"role": "user", "content": prompt}]
        )
        return parse_forecast_response(response.choices[0].message.content)[:horizon]

    def run_moving_average(self, sales: List[float], params: Dict, horizon: int) -> List[float]:
        window = params.get("window", 4)
        if len(sales) < window:
            return [sum(sales)/len(sales)] * horizon
        avg = sum(sales[-window:]) / window
        return [avg] * horizon

    def run_linear_regression(self, sales: List[float], horizon: int) -> List[float]:
        if len(sales) < 2:
            return [sales[-1] if sales else 0.0] * horizon
        X = np.arange(len(sales)).reshape(-1, 1)
        y = np.array(sales)
        model = LinearRegression().fit(X, y)
        future_X = np.arange(len(sales), len(sales) + horizon).reshape(-1, 1)
        return model.predict(future_X).tolist()

    def run_exponential_smoothing(self, sales: List[float], params: Dict, horizon: int) -> List[float]:
        alpha = params.get("alpha", 0.3)
        if not sales:
            return [0.0] * horizon
        forecast = sales[0]
        for val in sales[1:]:
            forecast = alpha * val + (1 - alpha) * forecast
        return [forecast] * horizon

    def run_seasonal_decomposition(self, sales: List[float], params: Dict, horizon: int) -> List[float]:
        period = params.get("period", 12)
        if len(sales) < period * 2:
            return [sum(sales) / len(sales)] * horizon
        seasonal_component = np.mean(sales[-period:])
        trend = np.mean(sales[-2*period:-period])
        return [(trend + seasonal_component) for _ in range(horizon)]

    async def run_custom_logic(self, product, sales: List[float], params: Dict, horizon: int):
        logic = params.get("logic", "")
        prompt = f"""
        You are an intelligent forecasting agent. Use the following logic to predict demand:

        Custom Logic: {logic}
        Sales History: {sales}

        Predict for next {horizon} months. Return only list format like: [100, 120, 110]
        """
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a rule interpreter and forecasting expert."},
                      {"role": "user", "content": prompt}]
        )
        return parse_forecast_response(response.choices[0].message.content)[:horizon]

    async def save_forecast(self, product_id, location_id, forecast_date, forecast_qty, method):
        await self.db.execute(text("""
            INSERT INTO forecast (
                id, company_id, product_id, location_id,
                forecast_date, forecast_quantity, method, created_at
            ) VALUES (
                :id, :company_id, :product_id, :location_id,
                :forecast_date, :forecast_quantity, :method, :created_at
            )
        """), {
            "id": str(uuid.uuid4()),
            "company_id": str(self.company_id),
            "product_id": str(product_id),
            "location_id": str(location_id),
            "forecast_date": forecast_date,
            "forecast_quantity": forecast_qty,
            "method": method,
            "created_at": datetime.utcnow()
      