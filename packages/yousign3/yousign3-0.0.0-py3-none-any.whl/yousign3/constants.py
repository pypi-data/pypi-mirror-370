from enum import StrEnum


class DeliveryMode(StrEnum):
    NONE = 'none',
    EMAIL = 'email'


class Field:
    class Type(StrEnum):
        SIGNATURE = 'signature'
        MENTION = 'mention'
        TEXT = 'text'
        CHECKBOX = 'checkbox'
        RADIO_GROUP = 'radio_group'
        READ_ONLY = 'read_only_text'


class Signer:
    class Status(StrEnum):
        INITIATED = 'initiated'
        DECLINED = 'declined'
        NOTIFIED = 'notified'
        VERIFIED = 'verified'
        PROCESSING = 'processing'
        CONSENT_GIVEN = 'consent_given'
        SIGNED = 'signed'
        ABORTED = 'aborted'
        ERROR = 'error'


class Signature:
    class Level(StrEnum):
        ELECTRONIC = 'electronic_signature'
        ADVANCE_ELECTORNIC = 'advanced_electronic_signature'
        QUALIFIED_ELECTRONIC = 'qualified_electronic_signature'

    class AuthenticationMode(StrEnum):
        NONE = 'no_otp'
        OTP_EMAIL = 'otp_email'
        OTP_SMS = 'otp_sms'

    class Status(StrEnum):
        DRAFT = 'draft'
        ONGOING = 'ongoin'
        DONE = 'done'
        DELETED = 'deleted'
        EXPIRED = 'expired'
        CANCEL = 'canceled'
        APPROVAL = 'approval'
        REJECTED = 'rejected'
        DECLINED = 'declined'


class Document:
    class Nature(StrEnum):
        ATTACHMENT = 'attachment'
        SIGNABLE = 'signable_document'


class Font:
    class Family(StrEnum):
        INCONSOLATA = 'Inconsolata'
        OPEN_SANS = 'Open Sans'
        LATO = 'Lato'
        RALEWAY = 'Raleway'
        MERRIWEATHER = 'Merriweather'
        EB_GARAMOND = 'EB Garamond'
        COMIC_NEUE = 'Comic Neue'
        MONACO = 'Monaco'
        HELVETICA = 'Helvetica'
        COURIER = 'Courier'
        TIMES_ROMAN = 'Times Roman'
