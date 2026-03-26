"""Popula os 16 estabelecimentos e o usuário admin padrão na primeira execução."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.establishment import Establishment
from app.models.user import User
from app.services.auth_service import hash_password

ESTABLISHMENTS = [
    (102, "GCBC", "Guacamole Balneário Camboriú", "Guacamole"),
    (103, "GCFL", "Guacamole Florianópolis", "Guacamole"),
    (104, "GCJB", "Guacamole Rio Jardim Botânico", "Guacamole"),
    (105, "DSFL", "Didge Florianópolis", "Didge"),
    (106, "DSJL", "Didge Joinville", "Didge"),
    (107, "GCPA", "Guacamole Porto Alegre", "Guacamole"),
    (108, "GCBT", "Guacamole Rio Barra da Tijuca", "Guacamole"),
    (109, "GCJL", "Guacamole Joinville", "Guacamole"),
    (110, "DSPA", "Didge Porto Alegre", "Didge"),
    (126, "GTNT", "Guacamole Taqueria Niterói", "Guacamole Taqueria"),
    (127, "HTUB", "Híbrida Tubarão", "Híbrida"),
    (135, "GTTJ", "Guacamole Taqueria Tijuca", "Guacamole Taqueria"),
    (139, "GTIN", "Guacamole Taqueria Ingleses", "Guacamole Taqueria"),
    (163, "GCNY", "Guacamole Rio New York", "Guacamole"),
    (170, "GTCN", "Guacamole Taqueria Canoas", "Guacamole Taqueria"),
    (177, "GTCO", "Guacamole Taqueria Copacabana", "Guacamole Taqueria"),
]


async def seed_establishments(db: AsyncSession) -> None:
    result = await db.execute(select(Establishment))
    existing = {e.id for e in result.scalars().all()}

    new_records = [
        Establishment(id=eid, sigla=sigla, name=name, brand=brand)
        for eid, sigla, name, brand in ESTABLISHMENTS
        if eid not in existing
    ]

    if new_records:
        db.add_all(new_records)
        await db.commit()
        print(f"[seed] {len(new_records)} estabelecimentos inseridos.")
    else:
        print("[seed] Estabelecimentos já cadastrados, nada a fazer.")


async def seed_admin_user(db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.email == "admin@queamais.com.br"))
    if result.scalar_one_or_none():
        return
    admin = User(
        name="Administrador",
        email="admin@queamais.com.br",
        password_hash=hash_password("queamais@2026"),
        role="admin",
    )
    db.add(admin)
    await db.commit()
    print("[seed] Usuário admin criado: admin@queamais.com.br / queamais@2026")
