from supabase import create_client
from core.config import settings
import uuid

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE)

def upload_document_to_supabase(file, filename: str, bucket: str = "documents"):
    file_id = str(uuid.uuid4())
    path = f"{file_id}_{filename}"

    content = file.file.read()

    try:
        supabase.storage.from_(bucket).upload(path, content, {
            "content-type": file.content_type
        })
        return path
    except Exception as e:
        print(f"[UPLOAD ERROR] {e}")
        return None
