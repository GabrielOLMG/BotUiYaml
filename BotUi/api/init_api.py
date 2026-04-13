from fastapi import FastAPI
from BotUi.api.routes.debug import router as debug_router

# uvicorn BotUi.api.init_api:app --host 0.0.0.0 --port 8000
app = FastAPI(
    title="FastApi BotUi",
    version="0.1"
)
app.include_router(debug_router, prefix="/debug")
