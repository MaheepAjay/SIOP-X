from openai import OpenAI
from services.extractor.prompt_doc import MULTI_RULE_EXTRACTION_PROMPT
from core.config import settings
from api.utils.json_parser import safe_json_parse
from agents.utility.rule_storage_agent import store_rules_to_db
from sqlalchemy.ext.asyncio import AsyncSession  # ✅ use this not core.database
from typing import Optional


client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def compose_rules_from_document(
    document_text: str,
    source_doc: Optional[str] = None,
    db: Optional[AsyncSession] = None,
    company_id: Optional[str] = None,
    document_id: Optional[str] = None
):
    prompt = MULTI_RULE_EXTRACTION_PROMPT.replace("{document_content}", document_text[:4000])

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a supply chain rule extraction assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        rules = safe_json_parse(response.choices[0].message.content)
        if not isinstance(rules, list):
            rules = [rules]

        for rule in rules:
            rule["source_doc"] = source_doc or "unknown"
            rule["extracted_by"] = "gpt-4"

        # ✅ Store the rules into the database if context is present
        if db and company_id:
            await store_rules_to_db(
                rules=rules,
                company_id=company_id,
                document_id=document_id,
                source_doc=source_doc or "unknown",
                db=db
            )

        return rules

    except Exception as e:
        print(f"❌ Error extracting rules: {e}")
        raise RuntimeError(f"Rule extraction failed: {str(e)}")
