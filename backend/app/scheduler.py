"""Agendamento de sincronizações automáticas com APScheduler."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import date, timedelta

scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")


def setup_scheduler(app):
    """Registra os jobs e inicia o scheduler junto com o FastAPI."""

    @scheduler.scheduled_job(CronTrigger(hour=3, minute=0))
    async def daily_erp_sync():
        from app.database import AsyncSessionLocal
        from app.services.erp_service import sync_all as erp_sync_all
        async with AsyncSessionLocal() as db:
            count = await erp_sync_all(db, months=3)
            print(f"[scheduler] ERP sync: {count} snapshots atualizados.")

    @scheduler.scheduled_job(CronTrigger(hour=4, minute=0))
    async def daily_ads_sync():
        from app.database import AsyncSessionLocal
        from app.services.meta_service import sync_all as meta_sync
        from app.services.google_ads_service import sync_all as google_sync
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=6)  # últimos 7 dias
        async with AsyncSessionLocal() as db:
            meta_count = await meta_sync(db, start_date, end_date)
            google_count = await google_sync(db, start_date, end_date)
            print(f"[scheduler] Ads sync: Meta={meta_count}, Google={google_count} registros.")

    scheduler.start()
    return scheduler
