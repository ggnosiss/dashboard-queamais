"""Integração com a API do SIG Queamais."""
import asyncio
from datetime import datetime
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.establishment import Establishment
from app.models.erp_snapshot import ErpSnapshot

ERP_BASE_URL = "https://sig.queamais.com/api/report/mediaAcumulado"

INFOS = ["CMV", "CMO", "Fat", "FatSalao", "FatDelivery"]
TIPOS = ["realizado", "orcado"]

INFO_TO_FIELD = {
    ("Fat", "realizado"): "fat_realizado",
    ("Fat", "orcado"): "fat_orcado",
    ("FatSalao", "realizado"): "fat_salao_realizado",
    ("FatSalao", "orcado"): "fat_salao_orcado",
    ("FatDelivery", "realizado"): "fat_delivery_realizado",
    ("FatDelivery", "orcado"): "fat_delivery_orcado",
    ("CMV", "realizado"): "cmv_realizado",
    ("CMV", "orcado"): "cmv_orcado",
    ("CMO", "realizado"): "cmo_realizado",
    ("CMO", "orcado"): "cmo_orcado",
}


async def _fetch_indicator(
    client: httpx.AsyncClient,
    establishment_id: int,
    info: str,
    tipo: str,
    months: int,
) -> float | None:
    try:
        resp = await client.get(
            ERP_BASE_URL,
            params={"e": establishment_id, "info": info, "tipo": tipo, "ultimosMeses": months},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        # A API retorna um número ou objeto; normalizar para float
        if isinstance(data, (int, float)):
            return float(data)
        if isinstance(data, dict):
            # Tentar extrair valor principal
            for key in ("media_do_periodo", "value", "media", "resultado", "total"):
                if key in data:
                    return float(data[key])
        return None
    except Exception as exc:
        print(f"[ERP] Erro ao buscar {info}/{tipo} para estabelecimento {establishment_id}: {exc}")
        return None


async def sync_establishment(
    db: AsyncSession,
    establishment: Establishment,
    months: int = 3,
) -> ErpSnapshot:
    """Busca todos os indicadores ERP e salva/atualiza o snapshot."""
    now = datetime.utcnow()

    async with httpx.AsyncClient() as client:
        tasks = {
            (info, tipo): _fetch_indicator(client, establishment.id, info, tipo, months)
            for info in INFOS
            for tipo in TIPOS
        }
        results = await asyncio.gather(*tasks.values())

    values: dict[str, float | None] = {}
    for (info, tipo), result in zip(tasks.keys(), results):
        field = INFO_TO_FIELD[(info, tipo)]
        values[field] = result

    # Remover snapshot anterior do mesmo mês/janela
    await db.execute(
        delete(ErpSnapshot).where(
            ErpSnapshot.establishment_id == establishment.id,
            ErpSnapshot.ref_month == now.month,
            ErpSnapshot.ref_year == now.year,
            ErpSnapshot.months_window == months,
        )
    )

    snapshot = ErpSnapshot(
        establishment_id=establishment.id,
        ref_month=now.month,
        ref_year=now.year,
        months_window=months,
        synced_at=now,
        **values,
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return snapshot


async def sync_all(db: AsyncSession, months: int = 3) -> list[ErpSnapshot]:
    """Sincroniza todos os estabelecimentos em paralelo."""
    result = await db.execute(select(Establishment))
    establishments = result.scalars().all()

    snapshots = await asyncio.gather(
        *[sync_establishment(db, e, months) for e in establishments],
        return_exceptions=True,
    )
    return [s for s in snapshots if isinstance(s, ErpSnapshot)]
