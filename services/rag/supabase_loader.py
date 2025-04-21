from core.config import settings
from supabase import create_client

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE)

def list_documents(bucket_name: str = "documents"):
    response = supabase.storage.from_(bucket_name).list()
    return [doc['name'] for doc in response]

def download_document(file_name: str, bucket_name: str = "documents"):
    return supabase.storage.from_(bucket_name).download(file_name).decode("utf-8", errors="ignore")
