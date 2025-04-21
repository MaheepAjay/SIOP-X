# services/agents/trigger_agents.py

from sqlalchemy.future import select
from models.analysis_agent import UserAction
from sqlalchemy.ext.asyncio import AsyncSession
from agents.utility.agent_dispatcher import run_user_action

async def execute_pending_actions(db: AsyncSession):
    # Fetch all actions that haven't been executed yet
    result = await db.execute(select(UserAction).where(UserAction.status != "completed"))
    actions = result.scalars().all()

    print(f"Found {len(actions)} pending actions.")
    if not actions:
        print("No pending actions to execute.")
        return
    
    for action in actions:
        try:
            print(f"🚀 Running action: {action.action_type}")
            await run_user_action(action)

            action.status = "completed"
        except Exception as e:
            print(f"❌ Failed to run {action.action_type}: {str(e)}")
            action.status = "failed"

        await db.commit()
