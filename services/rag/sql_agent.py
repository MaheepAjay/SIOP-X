from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents import AgentExecutor  # still valid, unless migrating to LangGraph

from langchain_community.utilities import SQLDatabase

from langchain.prompts import SystemMessagePromptTemplate
from sqlalchemy import text
from core.config import settings
from core.database import get_sync_db
from langchain_openai import ChatOpenAI


# Step 1: Load schema context from table_dictionary
def load_table_dictionary() -> str:
    db = get_sync_db()
    with db() as session:
        query = text("SELECT table_name, column_name, data_type, description FROM table_dictionary ORDER BY table_name")
        result = session.execute(query).fetchall()
        schema_text = ""
        last_table = None
        for row in result:
            if row.table_name != last_table:
                schema_text += f"\n\n📄 Table: {row.table_name}\n"
                last_table = row.table_name
            schema_text += f"- {row.column_name} ({row.data_type}): {row.description}\n"
        return schema_text

# Step 2: Create SQL agent
def get_sql_agent() -> AgentExecutor:
    db = SQLDatabase.from_uri(settings.DATABASE_URL)
    llm = ChatOpenAI(model_name="gpt-4", temperature=0, openai_api_key=settings.OPENAI_API_KEY)

    schema = load_table_dictionary()
    system_message = SystemMessagePromptTemplate.from_template(f"""
You are a supply chain SQL expert. Translate user questions into SQL using this schema:

{schema}

Always return clear, helpful answers. If uncertain or data is missing, explain why.
""")

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        system_message=system_message,
        verbose=True,
        return_intermediate_steps=True,
    )
    return agent

# Step 3: Sync query function used by LangChain Tool
def query_sql(prompt: str) -> dict:
    agent = get_sql_agent()
    result = agent.invoke({"input": prompt})

    sql_queries = []
    for step in result.get("intermediate_steps", []):
        if hasattr(step[0], "tool_input") and isinstance(step[0].tool_input, str):
            sql_queries.append(step[0].tool_input)

    return {
        "question": prompt,
        "sql": sql_queries[-1] if sql_queries else None,
        "output": result["output"]
    }

from langchain.agents.agent_types import AgentType
from langchain.agents.agent import AgentExecutor
from core.config import settings
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent


def query_sql_chat(query: str, system_prompt: str) -> str:
    # Create SQLDatabase from sync URI
    db = SQLDatabase.from_uri(settings.DATABASE_URL)

    # Create LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    # Create SQL Agent with injected system prompt
    agent: AgentExecutor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        agent_executor_kwargs={"system_message": system_prompt}
    )

    output = agent.run(query)
    print(f"SQL Agent Output: {output}")
    # Run the query through the agent
    return agent.run(query)


# services/nl2db/nl2db_agent.py

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from services.extractor.prompt_doc import UPDATE_PROMPT_TEMPLATE
from services.rag.sql_agent import load_table_dictionary  # reuse your schema
from core.config import settings

def get_nl2sql_update_chain():
    prompt = PromptTemplate(
        template=UPDATE_PROMPT_TEMPLATE,
        input_variables=["instruction", "schema"]
    )
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    return LLMChain(prompt=prompt, llm=llm)

def generate_update_sql(user_instruction: str):
    schema = load_table_dictionary()
    chain = get_nl2sql_update_chain()
    return chain.run({"instruction": user_instruction, "schema": schema})

from sqlalchemy import text
from core.database import get_sync_db

def execute_update_sql(query: str) -> str:
    if any(word in query.lower() for word in ["delete", "drop", "truncate"]):
        raise ValueError("Dangerous query blocked.")

    # ✅ Clean the SQL string BEFORE passing to SQLAlchemy
    cleaned_query = clean_sql_code(query)

    db = get_sync_db()
    with db() as session:
        result = session.execute(text(cleaned_query))  # only here wrap with text()
        session.commit()
        return f"Query executed: {cleaned_query}"



# utils/sql_cleaner.py

def clean_sql_code(sql: str) -> str:
    """
    Cleans LLM-generated SQL by removing markdown code block markers like ```sql ... ```
    Returns the plain SQL string ready for execution.
    """
    # Remove leading/trailing whitespace
    cleaned = sql.strip()

    # Remove triple backtick with or without language tag (e.g., ```sql or ```)
    if cleaned.startswith("```"):
        cleaned = cleaned.lstrip("`").lstrip("sql").strip()
    if cleaned.endswith("```"):
        cleaned = cleaned.rstrip("`").strip()

    # Also handle cases where it's wrapped in a full block
    cleaned = cleaned.replace("```sql", "").replace("```", "").strip()

    return cleaned
