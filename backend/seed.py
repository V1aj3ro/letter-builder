"""
Seed script — fills the database with test data.

Usage (inside the backend container or locally with DB running):
    python seed.py

Or via docker compose:
    docker compose exec letters-backend python seed.py
"""
import asyncio
import os
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://letters:letters@localhost:5432/letters",
)

engine = create_async_engine(DATABASE_URL)
Session = async_sessionmaker(engine, expire_on_commit=False)

# Import models after engine is set up
from app.models import Organization, User, Recipient, Project, ProjectRecipient, Letter
from app.auth import hash_password


ORG = {
    "name": "Общество с ограниченной ответственностью «СтройДемо»",
    "short_name": "ООО «СтройДемо»",
    "inn": "7701234567",
    "ogrn": "1027700000001",
    "legal_address": "125009, г. Москва, ул. Тверская, д. 1, офис 100",
    "bank_name": "ПАО «Сбербанк России»",
    "bik": "044525225",
    "account": "40702810000000012345",
    "corr_account": "30101810400000000225",
    "phone": "+7 (495) 123-45-67",
    "signer_name": "Дьяченко О.Н.",
    "signer_role": "Директор",
}

USERS = [
    {
        "email": "admin@demo.ru",
        "password": "admin123",
        "full_name": "Дьяченко Олег Николаевич",
        "position": "Директор",
        "phone": "+7 (495) 123-45-67",
        "is_admin": True,
        "is_approved": True,
    },
    {
        "email": "ivanov@demo.ru",
        "password": "user123",
        "full_name": "Иванов Иван Иванович",
        "position": "Главный инженер",
        "phone": "+7 (495) 123-45-68",
        "is_admin": False,
        "is_approved": True,
    },
    {
        "email": "petrova@demo.ru",
        "password": "user123",
        "full_name": "Петрова Мария Сергеевна",
        "position": "Инженер-проектировщик",
        "phone": "+7 (495) 123-45-69",
        "is_admin": False,
        "is_approved": True,
    },
    {
        "email": "pending@demo.ru",
        "password": "user123",
        "full_name": "Сидоров Алексей Петрович",
        "position": "Менеджер",
        "phone": None,
        "is_admin": False,
        "is_approved": False,  # ожидает одобрения
    },
]

RECIPIENTS = [
    "ООО «АльфаСтрой»\nГенеральному директору\nКузнецову А.В.",
    "АО «БетаПроект»\nГенеральному директору\nМихайлову С.П.",
    "ООО «ГаммаДевелопмент»\nДиректору по строительству\nЛебедеву К.И.",
    "ПАО «ДельтаГрупп»\nПредседателю правления\nНовикову Д.А.",
    "ООО «ЭпсилонСтройСервис»\nДиректору\nФёдорову В.Н.",
    "Администрация городского округа\nГлаве администрации\nСмирнову П.В.",
]

PROJECTS = [
    {
        "name": "ЖК «Солнечный берег» — корпус А",
        "recipients": [0, 1, 5],
        "default_recipient": 0,
    },
    {
        "name": "БЦ «Горизонт» — реконструкция",
        "recipients": [1, 2, 3],
        "default_recipient": 1,
    },
    {
        "name": "Дорожная инфраструктура — ул. Центральная",
        "recipients": [3, 4, 5],
        "default_recipient": 5,
    },
    {
        "name": "Торговый центр «Меркурий»",
        "recipients": [0, 2, 4],
        "default_recipient": 2,
    },
]

LETTERS = [
    {
        "project": 0,
        "recipient": 0,
        "subject": "О запросе коммерческого предложения на поставку арматуры",
        "body": """<p>Уважаемый Александр Викторович,</p>
<p>В рамках реализации проекта жилого комплекса «Солнечный берег» просим Вас предоставить коммерческое предложение на поставку арматуры класса A500С диаметром 12–32 мм в объёме <strong>250 тонн</strong>.</p>
<p>Требования к поставке:</p>
<ul>
<li>Срок поставки — не более 14 рабочих дней с момента заключения договора</li>
<li>Место доставки — строительная площадка по адресу: г. Москва, ул. Речная, д. 15</li>
<li>Наличие сертификатов качества на всю партию</li>
</ul>
<p>Коммерческое предложение просим направить до 25.04.2026 по реквизитам, указанным в настоящем письме.</p>
<p>По всем вопросам обращайтесь к нашему инженеру: Иванов Иван Иванович, +7 (495) 123-45-68.</p>""",
        "status": "sent",
        "days_ago": 10,
        "creator": 1,
    },
    {
        "project": 0,
        "recipient": 1,
        "subject": "О согласовании проектной документации",
        "body": """<p>Уважаемый Сергей Петрович,</p>
<p>Направляем на согласование проектную документацию по разделу «Конструктивные решения» (КР) для объекта ЖК «Солнечный берег», корпус А.</p>
<p>Просим рассмотреть документацию и предоставить заключение в срок до <strong>20.04.2026</strong>.</p>
<p>Комплект документации прилагается на 47 листах.</p>""",
        "status": "sent",
        "days_ago": 5,
        "creator": 0,
    },
    {
        "project": 1,
        "recipient": 3,
        "subject": "О переносе сроков производства работ",
        "body": """<p>Уважаемый Дмитрий Александрович,</p>
<p>В связи с неблагоприятными погодными условиями в период с 01.04.2026 по 07.04.2026, а также задержкой поставки металлоконструкций, уведомляем Вас о переносе сроков выполнения монтажных работ на объекте БЦ «Горизонт».</p>
<p>Новые сроки:</p>
<ul>
<li>Начало монтажа металлоконструкций — 15.04.2026 (было: 08.04.2026)</li>
<li>Окончание монтажных работ — 30.05.2026 (было: 23.05.2026)</li>
</ul>
<p>Данный перенос не повлечёт изменения итоговой даты сдачи объекта.</p>""",
        "status": "sent",
        "days_ago": 3,
        "creator": 1,
    },
    {
        "project": 2,
        "recipient": 5,
        "subject": "О получении разрешения на производство земляных работ",
        "body": """<p>Уважаемый Павел Валерьевич,</p>
<p>Просим Вас выдать разрешение на производство земляных работ на участке ул. Центральная в соответствии с проектом благоустройства № 2026-ДИ-017.</p>
<p>К настоящему письму прилагаем:</p>
<ul>
<li>Схему производства земляных работ</li>
<li>График проведения работ</li>
<li>Договор страхования ответственности</li>
</ul>""",
        "status": "draft",
        "days_ago": 1,
        "creator": 2,
    },
    {
        "project": 3,
        "recipient": 2,
        "subject": "О предоставлении технических условий на подключение к тепловым сетям",
        "body": """<p>Уважаемый Константин Игоревич,</p>
<p>В рамках проектирования торгового центра «Меркурий» (общая площадь — 12 500 м²) просим предоставить технические условия на подключение к тепловым сетям.</p>
<p>Ориентировочная тепловая нагрузка — <strong>2,8 МВт</strong>.</p>
<p>Адрес объекта: г. Москва, Садовое кольцо, д. 42.</p>""",
        "status": "draft",
        "days_ago": 0,
        "creator": 0,
    },
]


async def seed():
    async with Session() as db:
        # ── Organization ──────────────────────────────
        result = await db.execute(select(Organization).where(Organization.id == 1))
        org = result.scalar_one_or_none()
        if not org:
            org = Organization(id=1)
            db.add(org)
        for k, v in ORG.items():
            setattr(org, k, v)
        await db.commit()
        print("✓ Organization")

        # ── Users ─────────────────────────────────────
        users = []
        for u in USERS:
            result = await db.execute(select(User).where(User.email == u["email"]))
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    email=u["email"],
                    hashed_password=hash_password(u["password"]),
                    full_name=u["full_name"],
                    position=u["position"],
                    phone=u["phone"],
                    is_admin=u["is_admin"],
                    is_approved=u["is_approved"],
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
                print(f"  + User {user.email}")
            else:
                print(f"  ~ User {user.email} already exists")
            users.append(user)
        print(f"✓ Users ({len(users)})")

        # ── Recipients ────────────────────────────────
        recipients = []
        for name in RECIPIENTS:
            result = await db.execute(select(Recipient).where(Recipient.name == name))
            r = result.scalar_one_or_none()
            if not r:
                r = Recipient(name=name)
                db.add(r)
                await db.commit()
                await db.refresh(r)
                print(f"  + Recipient {r.name[:40]}...")
            recipients.append(r)
        print(f"✓ Recipients ({len(recipients)})")

        # ── Projects ──────────────────────────────────
        projects = []
        for pd in PROJECTS:
            result = await db.execute(select(Project).where(Project.name == pd["name"]))
            p = result.scalar_one_or_none()
            if not p:
                p = Project(
                    name=pd["name"],
                    created_by=users[0].id,
                    default_recipient_id=recipients[pd["default_recipient"]].id,
                )
                db.add(p)
                await db.commit()
                await db.refresh(p)

                # Link recipients
                for ri in pd["recipients"]:
                    link = ProjectRecipient(project_id=p.id, recipient_id=recipients[ri].id)
                    db.add(link)
                await db.commit()
                print(f"  + Project '{p.name}'")
            projects.append(p)
        print(f"✓ Projects ({len(projects)})")

        # ── Letters ───────────────────────────────────
        # Reset sequence so numbers start fresh only if no letters exist
        count = (await db.execute(text("SELECT COUNT(*) FROM letters"))).scalar()
        if count == 0:
            await db.execute(text("SELECT setval('letter_number_seq', 1, false)"))

        for ld in LETTERS:
            project = projects[ld["project"]]
            recipient = recipients[ld["recipient"]]
            creator = users[ld["creator"]]

            # Check if letter with this subject already exists
            result = await db.execute(
                select(Letter).where(
                    Letter.project_id == project.id,
                    Letter.subject == ld["subject"],
                )
            )
            if result.scalar_one_or_none():
                print(f"  ~ Letter '{ld['subject'][:40]}...' already exists")
                continue

            number = (await db.execute(text("SELECT nextval('letter_number_seq')"))).scalar()
            letter_date = date.today() - timedelta(days=ld["days_ago"])

            letter = Letter(
                number=number,
                project_id=project.id,
                recipient_id=recipient.id,
                created_by=creator.id,
                subject=ld["subject"],
                body=ld["body"],
                status=ld["status"],
                letter_date=letter_date,
            )
            db.add(letter)
            await db.commit()
            print(f"  + Letter №{number} '{ld['subject'][:45]}...'")

        print("✓ Letters")
        print()
        print("═" * 50)
        print("Seed complete. Test accounts:")
        for u in USERS:
            role = "admin" if u["is_admin"] else ("pending" if not u["is_approved"] else "user")
            print(f"  {u['email']:30s}  pw: {u['password']}  [{role}]")


if __name__ == "__main__":
    asyncio.run(seed())
