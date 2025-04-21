# api/routes/chat_router.py

from typing import Any, Dict, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import false, select, true
from agents.replenishment.replenishment_agent import ReplenishmentAgent
from agents.segmentation.generate_rule import parse_segmentation_prompt
from agents.segmentation.run_segmentation import run_segmentation_rules
from api.utils.json_parser import safe_json_parse
from core.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from models.segmentation_rule import SegmentationRule
from models.standard_blueprint import StandardBlueprint
from services.extractor.blueprint import compare_config_to_blueprint
from services.extractor.prompt_doc import SQL_QUERY_PROMPT
from services.metadata_service import create_metadata_from_document
from services.rag.embedder import embed_all_documents_from_supabase
from services.rag.retriever import  get_document_answer_chain, query_vector_store
from services.rag.sql_agent import execute_update_sql, generate_update_sql, get_sql_agent, load_table_dictionary, query_sql_chat
from openai import OpenAI
from core.config import settings
from agents.utility.trigger_agent import execute_pending_actions
from uuid import UUID  # ✅ native Python UUID type for FastAPI/Pydantic






STANDARD_REPLENISHMENT_BLUEPRINT = {
  "methods": [
    {
      "tags": [
        "stable_demand",
        "simple"
      ],
      "default": true,
      "parameters": {
        "inventory": {
          "source": "inventory",
          "default": 0,
          "required": true
        },
        "lead_time": {
          "source": "policy",
          "default": 7,
          "required": false
        },
        "max_level": {
          "source": "policy",
          "default": 200,
          "required": true
        },
        "min_level": {
          "source": "policy",
          "default": 50,
          "required": true
        },
        "lead_time_offset_days": {
          "default": 0,
          "required": false
        }
      },
      "description": "Trigger replenishment when inventory falls below minimum level.",
      "method_name": "MinMax",
      "action_logic": "order_quantity = max_level - inventory",
      "fallback_strategy": "Use defaults if any values are missing",
      "trigger_condition": "inventory < min_level",
      "customizable_fields": [
        "trigger_condition",
        "action_logic",
        "parameters"
      ]
    },
    {
      "tags": [
        "predictive",
        "variable_demand"
      ],
      "parameters": {
        "inventory": {
          "source": "inventory",
          "default": 0,
          "required": true
        },
        "lead_time": {
          "source": "policy",
          "default": 7,
          "required": true
        },
        "safety_stock": {
          "source": "policy",
          "default": 20,
          "required": false
        },
        "avg_daily_demand": {
          "source": "demand_history",
          "default": 10,
          "required": true
        }
      },
      "description": "Calculate reorder point and order when inventory drops below ROP.",
      "method_name": "ROP (Reorder Point)",
      "action_logic": "ROP = avg_daily_demand * lead_time + safety_stock; order_quantity = ROP - inventory",
      "fallback_strategy": "Use default demand and safety stock if not available",
      "trigger_condition": "inventory < ROP",
      "customizable_fields": [
        "trigger_condition",
        "action_logic",
        "parameters"
      ]
    },
    {
      "tags": [
        "cost_optimized",
        "batch"
      ],
      "parameters": {
        "order_cost": {
          "source": "finance",
          "default": 100,
          "required": true
        },
        "demand_rate": {
          "source": "forecast",
          "default": 500,
          "required": true
        },
        "holding_cost": {
          "source": "finance",
          "default": 2,
          "required": true
        }
      },
      "description": "Optimize order size by minimizing total cost (ordering + holding).",
      "method_name": "EOQ (Economic Order Quantity)",
      "action_logic": "EOQ = sqrt((2 * demand_rate * order_cost) / holding_cost); order_quantity = EOQ",
      "fallback_strategy": "Use average values if cost inputs are missing",
      "trigger_condition": "Periodic review or inventory < threshold",
      "customizable_fields": [
        "parameters"
      ]
    },
    {
      "tags": [
        "real_time",
        "adaptive"
      ],
      "parameters": {
        "inventory": {
          "source": "inventory",
          "default": 0,
          "required": true
        },
        "lead_time": {
          "source": "policy",
          "default": 5,
          "required": true
        },
        "buffer_days": {
          "default": 2,
          "required": false
        },
        "past_30_day_usage": {
          "source": "usage_data",
          "default": 300,
          "required": true
        }
      },
      "description": "Order based on recent usage trends.",
      "method_name": "Consumption-Based",
      "action_logic": "order_quantity = ((past_30_day_usage / 30) * (lead_time + buffer_days)) - inventory",
      "fallback_strategy": "Use default usage and lead time if not found",
      "trigger_condition": "inventory < (past_30_day_usage / 30) * lead_time",
      "customizable_fields": [
        "parameters",
        "buffer_days",
        "trigger_condition"
      ]
    },
    {
      "tags": [
        "calendar",
        "retail"
      ],
      "parameters": {
        "inventory": {
          "source": "inventory",
          "default": 0,
          "required": true
        },
        "interval_days": {
          "default": 7,
          "required": true
        },
        "forecast_demand": {
          "source": "forecast",
          "default": 100,
          "required": false
        }
      },
      "description": "Replenishment every N days regardless of inventory.",
      "method_name": "Fixed Interval",
      "action_logic": "order_quantity = forecast_demand - inventory",
      "fallback_strategy": "If forecast missing, assume default demand",
      "trigger_condition": "run on schedule every interval_days",
      "customizable_fields": [
        "interval_days",
        "forecast_demand"
      ]
    }
  ],
  "agent_type": "Replenishment",
  "default_execution_strategy": "daily"
}

router = APIRouter(prefix="/chat", tags=["Chat"])

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Input schema
class ChatQuery(BaseModel):
    company_id: str
    query: str
    output_format: Optional[str] = None  # New

# 📥 Request model
class SegmentationPromptInput(BaseModel):
    prompt: str
    company_id: uuid.UUID



# 🚦 Naive query router
def route_query(query: str) -> str:
    sql_keywords = ["sales", "inventory", "forecast", "demand", "orders", "quantity"]
    if any(keyword in query.lower() for keyword in sql_keywords):
        return "sql"
    else:
        return "rag"

# 🧠 Main endpoint
@router.post("/query")
async def query_chat_engine(payload: ChatQuery, db: AsyncSession = Depends(get_async_session)):
    try:
        route = route_query(payload.query)

        schema_text = load_table_dictionary()
        output_format = payload.output_format or "Plain text summary with key values"

        # Format the system prompt
        prompt_string = SQL_QUERY_PROMPT.format(
            output_format=output_format,
            schema_text=schema_text
        )

        print(f"Prompt String: {prompt_string}")
        print(f"Route: {route}")
        # Call the appropriate agent based on the route
        
        if route == "sql":
            # Call sync function directly
            response = query_sql_chat(query=payload.query, system_prompt=prompt_string)
        else:
            # This remains async
            response = await ask_documents(payload)
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



def decide_engine(query: str):
    query_lower = query.lower()
    if any(word in query_lower for word in ["policy", "document", "rule", "chunk"]):
        return "retriever"
    return "sql"

async def route_to_agent(query: str):
    engine = decide_engine(query)

    if engine == "retriever":
        retriever_chain = []
        return retriever_chain.run(query)
    else:
        sql_agent = get_sql_agent()
        return sql_agent.run(query)
    

@router.post("/embed-documents")
async def embed_documents_endpoint(
    db: AsyncSession = Depends(get_async_session)
):
    try:
        await embed_all_documents_from_supabase(db)
        return {"message": "📚 Document embeddings completed and stored successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to embed documents: {str(e)}")
    



@router.post("/agents/run-all")
async def run_agents(db: AsyncSession = Depends(get_async_session)):
    
    await execute_pending_actions(db)
    return {"status": "completed"}


@router.post("/ask-docs", tags=["Document QA"])
async def ask_documents(payload: ChatQuery):
    chain = await get_document_answer_chain(company_id=payload.company_id)
    result = await chain.ainvoke({"query": payload.query})
    
    return {
        "answer": result["result"],
        "sources": [
            {
                "document_name": doc.metadata.get("document_name"),
                "source_doc": doc.metadata.get("source_doc"),
                "chunk": doc.page_content
            }
            for doc in result["source_documents"]
        ]
    }

class NLUpdateRequest(BaseModel):
    instruction: str

@router.post("/nl2db/update")
def handle_nl_update(payload: NLUpdateRequest):
    try:
        sql_query = generate_update_sql(payload.instruction)
        result = execute_update_sql(sql_query)
        return {"status": "success", "query": sql_query, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# ------------------------
# Pydantic Input Schema
# ------------------------
class AgentConfigInput(BaseModel):
    agent_type: str
    method_name: str
    customizations: dict[str, Any]

# ------------------------
# /blueprint/compare POST
# ------------------------
@router.post("/blueprint/compare")
async def compare_blueprint(
    agent_config: AgentConfigInput,
    db: AsyncSession = Depends(get_async_session)
):
    # Step 1: Fetch blueprint from DB
    result = await db.execute(
        select(StandardBlueprint).where(StandardBlueprint.agent_type == agent_config.agent_type)
    )
    blueprint_row = result.scalar_one_or_none()

    if not blueprint_row:
        raise HTTPException(status_code=404, detail="Blueprint not found for this agent type.")

    # Step 2: Compare
    method, deviations, final_config = await compare_config_to_blueprint(
        agent_config.dict(),
        blueprint_row.blueprint_json
    )

    return {
        "matched_method": method,
        "deviations": deviations,
        "final_config": final_config
    }


# 📤 Route: LLM-powered rule creator
@router.post("/segments/rules/from-prompt")
async def create_segmentation_rule_from_prompt(
    payload: SegmentationPromptInput,
    db: AsyncSession = Depends(get_async_session)
):
    parsed = parse_segmentation_prompt(payload.prompt)
    #parsed = safe_json_parse(raw_llm_result)

    if not parsed or not parsed.get("segment_name") or not parsed.get("rule_expression"):
        raise HTTPException(status_code=400, detail="Invalid rule parsed from LLM.")

    new_rule = SegmentationRule(
        company_id=payload.company_id,
        segment_name=parsed["segment_name"],
        rule_description=parsed.get("rule_description", payload.prompt),
        rule_expression=parsed["rule_expression"]
    )

    db.add(new_rule)
    await db.commit()
    await db.refresh(new_rule)

    return {
        "message": "Rule created from prompt",
        "rule": {
            "id": new_rule.id,
            "segment_name": new_rule.segment_name,
            "rule_expression": new_rule.rule_expression
        }
    }


@router.post("/segments/refresh")
async def apply_segmentation_rules(
    company_id: UUID = Query(..., description="Company ID"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Applies all segmentation rules for a company and updates product.segment fields.
    """
    results = await run_segmentation_rules(company_id, db)
    return {
        "message": "Segmentation rules applied.",
        "summary": results
    }

@router.post("/replenishment/plan")
async def run_replenishment_plan(
    company_id: UUID = Query(..., description="Company ID"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Run the replenishment agent using segmentation and policy logic.
    Stores planned orders directly in the `po` table (order_type = 3).
    """
    agent = ReplenishmentAgent(company_id=company_id, db=db, blueprint=STANDARD_REPLENISHMENT_BLUEPRINT)
    result = await agent.run()
    return {
        "message": f"{len(result)} planned orders created.",
        "orders": result
    }