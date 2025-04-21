
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from agents.forecast.forecast_agent import ForecastingAgent, get_forecast_data
from core.database import get_async_session
from uuid import UUID

from agents.forecast.forecastplanningchain import ForecastPlanningChain
from agents.forecast.forecast_diagnostic import ForecastDiagnosticAgent

router = APIRouter(prefix="/forecast", tags=["Forecasting"])


class ForecastPlanningInput(BaseModel):
    company_id: UUID
    product_id: str
    location_id: str
    sales_history: List[float]
    forecast_horizon: int = 12


class ForecastDiagnosticInput(BaseModel):
    product_id: str
    location_id: str
    sales_history: List[float]
    forecast_result: List[float]
    method_used: str
    params_used: Dict


@router.post("/planning-chain")
async def run_forecast_planning_chain(payload: ForecastPlanningInput, db: AsyncSession = Depends(get_async_session)):
    blueprint = await load_forecasting_blueprint("forecast", db)

    planner = ForecastPlanningChain(payload.company_id, db, blueprint)

    # 🔁 Fetch sales history from DB
    sales_history = await planner.forecasting_agent.get_sales_data(
        product_id=payload.product_id,
        location_id=payload.location_id
    )

    return await planner.run_chain(
        product_id=payload.product_id,
        location_id=payload.location_id,
        sales_history=sales_history,  # ✅ Now comes from DB
        user_horizon=payload.forecast_horizon
    )

@router.post("/diagnose")
async def run_forecast_diagnosis(payload: ForecastDiagnosticInput, db: AsyncSession = Depends(get_async_session)):
    agent = ForecastDiagnosticAgent()
    company_id = 'c596d0b0-598f-48bd-9a4a-85db7b1d7eb5'
    # 🧠 Fetch actual sales history from DB
    forecasting_agent = ForecastingAgent(company_id, db=db, blueprint={})  # blueprint not needed for this call
    sales_history = await forecasting_agent.get_sales_data(
        product_id=payload.product_id,
        location_id=payload.location_id
    )

    # 🧠 Fetch forecasted values from DB
    forecast_result = await get_forecast_data(
        db=db,
        product_id=payload.product_id,
        location_id=pay