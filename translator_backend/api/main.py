from api.routes.translator_api import router as translator_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(translator_router)