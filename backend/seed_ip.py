"""
Fill IP (Individual Entrepreneur) fields for the organization.

Usage:
    docker compose exec letters-backend python seed_ip.py
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://letters:letters@localhost:5432/letters",
)

engine = create_async_engine(DATABASE_URL)
Session = async_sessionmaker(engine, expire_on_commit=False)

from app.models import Organization

IP_DATA = {
    "ip_full_name":      "Дьяченко Олег Николаевич",
    "ip_inn":            "770112345678",
    "ip_ogrnip":         "312770000012345",
    "ip_legal_address":  "125009, г. Москва, ул. Тверская, д. 1",
    "ip_bank_name":      "ПАО «Сбербанк России»",
    "ip_bik":            "044525225",
    "ip_account":        "40802810000000067890",
    "ip_corr_account":   "30101810400000000225",
    "ip_phone":          "+7 (495) 123-45-67",
    "ip_signer_name":    "Дьяченко О.Н.",
    "ip_signer_role":    "Индивидуальный предприниматель",
}


async def seed_ip():
    async with Session() as db:
        result = await db.execute(select(Organization).where(Organization.id == 1))
        org = result.scalar_one_or_none()
        if not org:
            org = Organization(id=1)
            db.add(org)

        for k, v in IP_DATA.items():
            setattr(org, k, v)

        await db.commit()
        print("✓ IP fields updated:")
        for k, v in IP_DATA.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    asyncio.run(seed_ip())
