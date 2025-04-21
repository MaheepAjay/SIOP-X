from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine
from api.routes.document_upload import router as embedding_router
from api.routes.chat_router import router as chat_router
from api.routes.forecast_router import router as forecast
from api.routes import document_upload
from api.routes.chat_router import router as embed_router
from models import forecasts, segmentation_rule




app = FastAPI()


@app.on_event("startup")
async def startup_event():
    try:
        # Instead of engine.begin(), try a simple test
        async with engine.connect() as conn:
            print("✅ Connected to async DB.")
    except Exception as e:
        print("❌ Could not connect to DB at startup:", str(e))



# Allow frontend during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⛔ Replace with specific domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SIOP-X backend is up!"}

app.include_router(document_upload.router, prefix="/api/v1/documents")
app.include_router(embedding_router, prefix="/api/v1/embeddings")
app.include_router(chat_router)
app.include_router(embed_router, prefix="/api/v1", tags=["Embeddings"])
app.include_router(forecast, prefix="/forecast", tags=["Forecasting"])


