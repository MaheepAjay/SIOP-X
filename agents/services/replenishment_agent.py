import asyncio
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool  # ✅ This is the CORRECT Tool
from langchain.chains import LLMMathChain
from core.config import settings
from fastapi.concurrency import run_in_threadpool

from models.analysis_agent import UserAction
from services.rag.sql_agent import query_sql

# 🔧 LLM
llm = ChatOpenAI(model_name="gpt-4", temperature=0, openai_api_key=settings.OPENAI_API_KEY)

def echo_tool_func(input: str) -> str:
    return f"Echo: {input}"

test_tool1 = Tool.from_function(
    name="EchoTool",
    func=echo_tool_func,
    description="Echoes back the input"
)



test_tool = [
    Tool.from_function(
        name="InventorySQLTool",
        func=query_sql,
        description="Use this to fetch inventory, lead time, and part-level details. Input should be a natural language question like 'get stock for SKU-123'."
    ),
    Tool.from_function(
        name="LLMMathTool",
        func=LLMMathChain.from_llm(llm=llm).run,
        description="Use this for calculating formulas like 'SS = Z * σ * √LT'."
    ),
    Tool.from_function(
    name="EchoTool",
    func=echo_tool_func,
    description="Echoes back the input"
    )

]

# 🧠 Initialize agent
agent = initialize_agent(
    tools=test_tool,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 🏃 Call agent
async def run_replenishment(action: UserAction):
    prompt = f"""
You are a replenishment planning expert. Based on the following rule, generate a replenishment recommendation.

Rule Name: {action.action_type}
Logic: {action.description}

Use the tools available to fetch inventory and perform calculations if required.
"""
    prompt1= f"""
You are my IT expert. based on the dictionary provided, tell me the total sales in my system
"""

    print("🔍 Prompt:")
    print(prompt)
    result = await run_in_threadpool(agent.run, prompt1)
    print("✅ Agent response:", result)
