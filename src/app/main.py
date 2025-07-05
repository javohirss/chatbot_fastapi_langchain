from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.app.routers.auth import router as auth_router
from src.app.routers.chat import router as chat_router
from src.app.routers.admin import router as admin_router

app = FastAPI()


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_index():
    return FileResponse("src/app/static/index.html")


app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(admin_router)

app.mount("/static", StaticFiles(directory="src/app/static"), name="static")