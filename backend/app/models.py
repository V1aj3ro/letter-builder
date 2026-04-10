from datetime import datetime, date
from sqlalchemy import Integer, String, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    # ООО реквизиты
    name: Mapped[str] = mapped_column(String(500), default="")
    short_name: Mapped[str] = mapped_column(String(200), default="")
    inn: Mapped[str] = mapped_column(String(20), default="")
    ogrn: Mapped[str] = mapped_column(String(20), default="")
    legal_address: Mapped[str] = mapped_column(String(500), default="")
    bank_name: Mapped[str] = mapped_column(String(300), default="")
    bik: Mapped[str] = mapped_column(String(20), default="")
    account: Mapped[str] = mapped_column(String(30), default="")
    corr_account: Mapped[str] = mapped_column(String(30), default="")
    phone: Mapped[str] = mapped_column(String(50), default="")
    signer_name: Mapped[str] = mapped_column(String(200), default="")
    signer_role: Mapped[str] = mapped_column(String(200), default="")
    # ИП реквизиты
    ip_full_name: Mapped[str] = mapped_column(String(300), default="")
    ip_inn: Mapped[str] = mapped_column(String(20), default="")
    ip_ogrnip: Mapped[str] = mapped_column(String(20), default="")
    ip_legal_address: Mapped[str] = mapped_column(String(500), default="")
    ip_bank_name: Mapped[str] = mapped_column(String(300), default="")
    ip_bik: Mapped[str] = mapped_column(String(20), default="")
    ip_account: Mapped[str] = mapped_column(String(30), default="")
    ip_corr_account: Mapped[str] = mapped_column(String(30), default="")
    ip_phone: Mapped[str] = mapped_column(String(50), default="")
    ip_signer_name: Mapped[str] = mapped_column(String(200), default="")
    ip_signer_role: Mapped[str] = mapped_column(String(200), default="")
    # Файлы
    logo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    footer_banner_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    signature_path: Mapped[str | None] = mapped_column(String(500), nullable=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(300), nullable=False)
    position: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    projects: Mapped[list["Project"]] = relationship("Project", back_populates="creator")
    letters: Mapped[list["Letter"]] = relationship("Letter", back_populates="creator")


class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    letters: Mapped[list["Letter"]] = relationship("Letter", back_populates="recipient")
    project_links: Mapped[list["ProjectRecipient"]] = relationship("ProjectRecipient", back_populates="recipient")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    default_recipient_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("recipients.id", ondelete="SET NULL"), nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    creator: Mapped["User"] = relationship("User", back_populates="projects")
    default_recipient: Mapped["Recipient | None"] = relationship("Recipient", foreign_keys=[default_recipient_id])
    recipient_links: Mapped[list["ProjectRecipient"]] = relationship("ProjectRecipient", back_populates="project", cascade="all, delete-orphan")
    letters: Mapped[list["Letter"]] = relationship("Letter", back_populates="project", cascade="all, delete-orphan")


class ProjectRecipient(Base):
    __tablename__ = "project_recipients"

    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipients.id", ondelete="CASCADE"), primary_key=True)

    project: Mapped["Project"] = relationship("Project", back_populates="recipient_links")
    recipient: Mapped["Recipient"] = relationship("Recipient", back_populates="project_links")


class Letter(Base):
    __tablename__ = "letters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    letter_date: Mapped[date] = mapped_column(Date, default=date.today)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    recipient_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("recipients.id", ondelete="SET NULL"), nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    sender_type: Mapped[str] = mapped_column(String(10), default="ooo")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    docx_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="letters")
    recipient: Mapped["Recipient | None"] = relationship("Recipient", back_populates="letters")
    creator: Mapped["User"] = relationship("User", back_populates="letters")
