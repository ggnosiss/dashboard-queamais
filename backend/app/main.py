from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables, AsyncSessionLocal
from app.seed import seed_establishments
from app.scheduler import setup_scheduler
from app.routers import establishments, erp, ads, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    async with AsyncSessionLocal() as db:
        await seed_establishments(db)
    setup_scheduler(app)
    yield
    # Shutdown — nada a limpar por ora


app = FastAPI(
    title="Dashboard de Marketing — API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8050", "http://localhost"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(establishments.router)
app.include_router(erp.router)
app.include_router(ads.router)
app.include_router(dashboard.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
