from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# --- Auth ---
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PendingResponse(BaseModel):
    message: str


# --- User ---
class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    position: Optional[str]
    phone: Optional[str]
    is_admin: bool
    is_approved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class UserRoleUpdate(BaseModel):
    is_admin: bool


# --- Organization ---
class OrganizationOut(BaseModel):
    id: int
    # ООО
    name: str
    short_name: str
    inn: str
    ogrn: str
    legal_address: str
    bank_name: str
    bik: str
    account: str
    corr_account: str
    phone: str
    signer_name: str
    signer_role: str
    # ИП
    ip_full_name: str
    ip_inn: str
    ip_ogrnip: str
    ip_legal_address: str
    ip_bank_name: str
    ip_bik: str
    ip_account: str
    ip_corr_account: str
    ip_phone: str
    ip_signer_name: str
    ip_signer_role: str
    # Файлы
    logo_path: Optional[str]
    footer_banner_path: Optional[str]
    signature_path: Optional[str]

    model_config = {"from_attributes": True}


class OrganizationUpdate(BaseModel):
    # ООО
    name: Optional[str] = None
    short_name: Optional[str] = None
    inn: Optional[str] = None
    ogrn: Optional[str] = None
    legal_address: Optional[str] = None
    bank_name: Optional[str] = None
    bik: Optional[str] = None
    account: Optional[str] = None
    corr_account: Optional[str] = None
    phone: Optional[str] = None
    signer_name: Optional[str] = None
    signer_role: Optional[str] = None
    # ИП
    ip_full_name: Optional[str] = None
    ip_inn: Optional[str] = None
    ip_ogrnip: Optional[str] = None
    ip_legal_address: Optional[str] = None
    ip_bank_name: Optional[str] = None
    ip_bik: Optional[str] = None
    ip_account: Optional[str] = None
    ip_corr_account: Optional[str] = None
    ip_phone: Optional[str] = None
    ip_signer_name: Optional[str] = None
    ip_signer_role: Optional[str] = None


# --- Recipient ---
class RecipientCreate(BaseModel):
    name: str


class RecipientUpdate(BaseModel):
    name: str


class RecipientOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Project ---
class ProjectCreate(BaseModel):
    name: str


class ProjectUpdate(BaseModel):
    name: str


class ProjectOut(BaseModel):
    id: int
    name: str
    created_by: int
    created_at: datetime
    default_recipient: Optional[RecipientOut] = None
    letter_count: int = 0

    model_config = {"from_attributes": True}


class ProjectDetailOut(BaseModel):
    id: int
    name: str
    created_by: int
    created_at: datetime
    default_recipient: Optional[RecipientOut] = None
    recipients: List[RecipientOut] = []

    model_config = {"from_attributes": True}


class ProjectRecipientAdd(BaseModel):
    recipient_id: int


class DefaultRecipientUpdate(BaseModel):
    recipient_id: int


# --- Letter ---
class LetterCreate(BaseModel):
    project_id: int
    recipient_id: Optional[int] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    letter_date: Optional[date] = None
    sender_type: str = "ooo"


class LetterUpdate(BaseModel):
    recipient_id: Optional[int] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    letter_date: Optional[date] = None
    sender_type: Optional[str] = None


class LetterStatusUpdate(BaseModel):
    status: str


class LetterOut(BaseModel):
    id: int
    number: int
    letter_date: date
    project_id: int
    recipient_id: Optional[int]
    created_by: int
    subject: Optional[str]
    body: Optional[str]
    sender_type: str
    status: str
    docx_path: Optional[str]
    pdf_path: Optional[str]
    created_at: datetime
    sent_at: Optional[datetime]
    recipient: Optional[RecipientOut] = None
    creator: Optional[UserOut] = None

    model_config = {"from_attributes": True}
