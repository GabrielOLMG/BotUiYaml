from fastapi import FastAPI
from BotUiManager.api.routes.debug import router as debug_router
from BotUiManager.api.routes.jobs import router as jobs_router
from BotUiManager.api.routes.step import router as step_router

app = FastAPI(
    title="FastApi BotUi",
    version="0.1"
)

app.include_router(jobs_router)
app.include_router(step_router)


# app.include_router(debug_router, prefix="/debug")