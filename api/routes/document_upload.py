from typing import List
from fastapi import APIRouter, Query, UploadFile, File, HTTPException, Depends
from sqlalchemy import UUID, select
from agents.utility.rule_composer_agent import compose_rules_from_document
from agents.utility.rule_storage_agent import store_rules_to_db
from models.analysis_agent import UserAction
from models.document_rules import DocumentRules
from services.file_uploader import upload_document_to_supabase
from core.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_session
from agents.utility.action_generator import generate_user_actions_from_rules
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from services.rag.chunkembed import chunk_and_store_embeddings


router = APIRouter()

    # 📦 Input schema
class RuleInput(BaseModel):
    id: Optional[str]
    domain: Optional[str]
    rule_type: Optional[str]
    method: Optional[str]
    segment: Optional[str]
    logic: Optional[str]
    frequency: Optional[str]

class ActionGenerationInput(BaseModel):
    company_id: str
    document_id: Optional[str] = None
    rules: List[RuleInput]

# Define ActionRequest schema
class ActionRequest(BaseModel):
    company_id: str
    document_id: Optional[str] = None
    rules: List[RuleInput]




@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    uploaded_paths = []

    for file in files:
        file_path = upload_document_to_supabase(file, file.filename)
        if not file_path:
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename}")
        uploaded_paths.append({"filename": file.filename, "supabase_path": file_path})

    return {
        "message": f"{len(uploaded_paths)} file(s) uploaded successfully.",
        "files": uploaded_paths
    }

import traceback

@router.post("/extract-rules")
async def extract_rules(files: List[UploadFile] = File(...), db: AsyncSession = Depends(get_async_session), company_id: str = "c596d0b0-598f-48bd-9a4a-85db7b1d7eb5"):
    extracted_results = []

    for file in files:
        try:
            content = (await file.read()).decode("utf-8", errors="ignore")
            rules = await compose_rules_from_document(content, source_doc=file.filename,db=db, company_id=company_id)
            extracted_results.append({
                "filename": file.filename,
                "rules": rules
            })
        except Exception as e:
            traceback.print_exc()  # 👈 Print full traceback
            raise HTTPException(status_code=500, detail=f"Failed to process {file.filename}: {str(e)}")

    return {
        "message": f"{len(extracted_results)} file(s) processed",
        "results": extracted_results
    }

\


@router.post("/upload-extract-store")
async def upload_extract_store(
    file: UploadFile = File(...),
    company_id: str = "f6e92b9b-8b9e-4d31-bf28-5e74271e661a",  # Replace with real auth context or user input
    db: AsyncSession = Depends(get_async_session)
):
    try:
        # Step 1: Read file content
        content = (await file.read()).decode("utf-8", errors="ignore")

        # Step 2: Extract + Store Rules
        rules = await compose_rules_from_document(
            document_text=content,
            source_doc=file.filename,
            company_id=company_id,
            document_id=None,
            db=db
        )

        return {
            "message": f"{len(rules)} rule(s) extracted and stored successfully.",
            "filename": file.filename,
            "rules": rules
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")



# 🚀 Generate User Actions from Extracted Rules
@router.post("/generate-actions/from-db")
async def generate_actions_from_stored_rules(
    company_id: UUID = Query(..., description="Company UUID"),
    document_id: Optional[UUID] = Query(None, description="Document UUID"),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        # 🔍 1. Fetch rules from the DB
        query = select(DocumentRules).where(DocumentRules.company_id == company_id)
        if document_id:
            query = query.where(DocumentRules.document_id == document_id)
            
        result = await db.execute(query)
        rules = result.scalars().all()

        if not rules:
            raise HTTPException(status_code=404, detail="No rules found for this company/document.")

        # 🔁 2. Convert to dicts for action generator
        rule_dicts = [
            {
                "id": str(rule.id),
                "domain": rule.domain,
                "rule_type": rule.rule_type,
                "method": rule.method,
                "segment": rule.segment,
                "frequency": rule.frequency,
                "logic": rule.logic,
            }
            for rule in rules
        ]

        # ⚙️ 3. Generate actions
        actions = await generate_user_actions_from_rules(
            rules=rule_dicts,
            company_id=str(company_id),
            document_id=str(document_id) if document_id else None,
            db=db
        )

        return {
            "message": f"{len(actions)} user action(s) created.",
            "actions": [
                {
                    "id": str(a.id),
                    "action_type": a.action_type,
                    "description": a.description,
                    "target_segment": a.target_segment,
                    "trigger_type": a.trigger_type,
                    "frequency": a.frequency,
                    "created_at": a.created_at.isoformat()
                } for a in actions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate actions: {str(e)}")
    



  

@router.post("/chunkembeddings")
async def upload_and_chunk_embeddings(
    file: UploadFile = File(...),
    document_id: Optional[UUID] = None
):
    if document_id is None:
        raise HTTPException(status_code=400, detail="document_id is required")

    try:
        content = (await file.read()).decode("utf-8", errors="ignore")
        chunk_and_store_embeddings(text=content, document_id=str(document_id))
        return {
            "message": f"Chunks embedded and stored for document {document_id}",
            "filename": file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
