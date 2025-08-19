from dataclasses import dataclass, field
from uuid import uuid4
import yousign.constants as ys_const
from yousign.constants import Document, Signature, Field, Font
from typing import Optional, List


@dataclass
class Info:
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    locale: str = 'en'


@dataclass
class DocumentData:
    nature: Document.Nature
    name: str = 'Unnamed'
    id: Optional[uuid4] = None
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


@dataclass
class SignerData:
    info: Info
    signature_level: ys_const.Signature.Level
    signature_authentication_mode: Signature.AuthenticationMode = field(
        default=Signature.AuthenticationMode.NONE)
    id: Optional[uuid4] = None
    status: Optional[ys_const.Signer.Status] = None
    signature_link: Optional[str] = None
    signature_link_expiration_date: Optional[str] = None
    signature_image_preview: Optional[str] = None
    redirect_urls: Optional[str] = None
    custom_text: Optional[str] = None
    delivery_mode: Optional[ys_const.DeliveryMode] = None
    identification_attestation_id:  Optional[str] = None
    sms_notification: Optional[str] = None
    email_notification: Optional[str] = None
    pre_identity_verification_required: Optional[str] = None
    fields: Optional[List['FieldData']] = None


@dataclass
class SignatureData:
    name: str
    delivery_mode: ys_const.DeliveryMode

    id: Optional[uuid4] = None
    status: Optional[ys_const.Signature.Status] = None
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
    email_notification: Optional[str] = None
    data: Optional[str] = None


@dataclass
class FontVariantData:
    bold: bool = False
    italic: bool = False


@dataclass
class FontData:
    family: Font.Family
    color: str
    size: int
    variant: FontVariantData


@dataclass
class RadioData:
    x: int
    y: int
    size: int
    default_checked: bool = False
    name: Optional[str] = None


@dataclass
class FieldData:
    type: str
    x: int
    y: int = 0
    page: int = 1
    reason: Optional[int] = None
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
