from yousign3.constants import Document, Signature, \
    Field, Font, DeliveryMode, Signer
from typing import Optional, List

from pydantic import BaseModel, EmailStr, HttpUrl


class Info(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    locale: str = 'en'
    phone_number: Optional[str] = None


class CustomText(BaseModel):
    request_subject: Optional[str] = None
    request_body: Optional[str] = None
    reminder_subject: Optional[str] = None
    reminder_body: Optional[str] = None


class RedirectURL(BaseModel):
    success: Optional[HttpUrl] = None
    error: Optional[HttpUrl] = None
    decline: Optional[HttpUrl] = None


class DocumentData(BaseModel):
    nature: Document.Nature
    name: str = 'Unnamed'
    id: Optional[str] = None
    filename: Optional[str] = None
    sha256: Optional[str] = None
    is_protected: Optional[bool] = None
    is_signed: Optional[bool] = None
    is_locked: Optional[bool] = None
    created_at: Optional[str] = None
    total_pages: Optional[int] = None
    initials: Optional[str] = None
    content_type: Optional[str] = None
    total_anchors: Optional[int] = None


class SignerData(BaseModel):
    class SmsNotification(BaseModel):
        class OtpMessage(BaseModel):
            custom_text: Optional[str] = None
        otp_message: OtpMessage

    class EmailNotification(BaseModel):
        disabled: List[str] = []
    info: Info
    signature_level: Signature.Level
    signature_authentication_mode: Signature.AuthenticationMode = Signature.AuthenticationMode.NONE
    id: Optional[str] = None
    status: Optional[Signer.Status] = None
    signature_link: Optional[str] = None
    signature_link_expiration_date: Optional[str] = None
    signature_image_preview: Optional[str] = None
    redirect_urls: Optional[RedirectURL] = None
    custom_text: Optional[CustomText] = None
    delivery_mode: Optional[DeliveryMode] = None
    identification_attestation_id:  Optional[str] = None
    sms_notification: Optional[SmsNotification] = None
    email_notification: Optional[EmailNotification] = None
    pre_identity_verification_required: Optional[bool] = None
    fields: Optional[List['FieldData']] = None


class SignatureData(BaseModel):
    name: str
    delivery_mode: DeliveryMode

    class EmailNotification(BaseModel):
        class Sender(BaseModel):
            type: str
            custom_name: Optional[str] = None
        sender: Sender
        custom_note: Optional[str] = None

    id: Optional[str] = None
    status: Optional[Signature.Status] = None
    created_at: Optional[str] = None
    ordered_signers: Optional[bool] = None
    ordered_approvers: Optional[bool] = None
    source: Optional[str] = None
    email_custom_note: Optional[str] = None
    timezone: Optional[str] = None
    reminder_settings: Optional[str] = None
    expiration_date: Optional[str] = None
    external_id: Optional[str] = None
    branding_id: Optional[str] = None
    custom_experience_id: Optional[str] = None
    workspace_id: Optional[str] = None
    audit_trail_locale: Optional[str] = None
    signers_allowed_to_decline: Optional[bool] = None
    bulk_send_batch_id: Optional[str] = None

    email_notification: Optional[EmailNotification] = None
    data: Optional[str] = None


class FontVariantData(BaseModel):
    bold: bool = False
    italic: bool = False


class FontData(BaseModel):
    family: Font.Family
    color: str
    size: int
    variant: FontVariantData


class RadioData(BaseModel):
    x: int
    y: int
    size: int
    default_checked: bool = False
    name: Optional[str] = None


class FieldData(BaseModel):
    type: str
    x: int
    y: int = 0
    page: int = 1
    reason: Optional[str] = None
    mention: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    document_id: Optional[str] = None
    signer_id: Optional[str] = None
    font: Optional[FontData] = None
    name: Optional[str] = None
    max_length: Optional[int] = None
    question: Optional[str] = None
    instruction: Optional[str] = None
    optional: Optional[bool] = None
    default_value: Optional[bool] = None
    read_only: Optional[bool] = None
    size: Optional[int] = None
    checked: Optional[bool] = None
    radios: Optional[List[RadioData]] = None
    text: Optional[str] = None
