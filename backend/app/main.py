import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from alembic.config import Config
from alembic import command

from .routers import auth, profile, organization, projects, recipients, letters, users, onlyoffice


def _run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run sync Alembic in a thread — avoids conflicts with the running event loop
    await asyncio.to_thread(_run_migrations)
    yield


app = FastAPI(title="Letter Builder API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(organization.router, prefix="/api/organization", tags=["organization"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(recipients.router, prefix="/api/recipients", tags=["recipients"])
app.include_router(letters.router, prefix="/api/letters", tags=["letters"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(onlyoffice.router, prefix="/api/onlyoffice", tags=["onlyoffice"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
