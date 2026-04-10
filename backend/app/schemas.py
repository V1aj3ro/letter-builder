from datetime import datetime, date
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
    position: str | None
    phone: str | None
    is_admin: bool
    is_approved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    position: str | None = None
    phone: str | None = None


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
    logo_path: str | None
    footer_banner_path: str | None
    signature_path: str | None
    template_ooo_path: str | None
    template_ip_path: str | None

    model_config = {"from_attributes": True}


class OrganizationUpdate(BaseModel):
    # ООО
    name: str | None = None
    short_name: str | None = None
    inn: str | None = None
    ogrn: str | None = None
    legal_address: str | None = None
    bank_name: str | None = None
    bik: str | None = None
    account: str | None = None
    corr_account: str | None = None
    phone: str | None = None
    signer_name: str | None = None
    signer_role: str | None = None
    # ИП
    ip_full_name: str | None = None
    ip_inn: str | None = None
    ip_ogrnip: str | None = None
    ip_legal_address: str | None = None
    ip_bank_name: str | None = None
    ip_bik: str | None = None
    ip_account: str | None = None
    ip_corr_account: str | None = None
    ip_phone: str | None = None
    ip_signer_name: str | None = None
    ip_signer_role: str | None = None


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
    default_recipient: RecipientOut | None = None
    letter_count: int = 0

    model_config = {"from_attributes": True}


class ProjectDetailOut(BaseModel):
    id: int
    name: str
    created_by: int
    created_at: datetime
    default_recipient: RecipientOut | None = None
    recipients: list[RecipientOut] = []

    model_config = {"from_attributes": True}


class ProjectRecipientAdd(BaseModel):
    recipient_id: int


class DefaultRecipientUpdate(BaseModel):
    recipient_id: int


# --- Letter ---
class LetterCreate(BaseModel):
    project_id: int
    recipient_id: int | None = None
    subject: str | None = None
    body: str | None = None
    letter_date: date | None = None
    sender_type: str = "ooo"


class LetterUpdate(BaseModel):
    recipient_id: int | None = None
    subject: str | None = None
    body: str | None = None
    letter_date: date | None = None
    sender_type: str | None = None


class LetterStatusUpdate(BaseModel):
    status: str


class LetterOut(BaseModel):
    id: int
    number: int
    letter_date: date
    project_id: int
    recipient_id: int | None
    created_by: int
    subject: str | None
    body: str | None
    sender_type: str
    status: str
    docx_path: str | None
    pdf_path: str | None
    created_at: datetime
    sent_at: datetime | None
    recipient: RecipientOut | None = None
    creator: UserOut | None = None

    model_config = {"from_attributes": True}
