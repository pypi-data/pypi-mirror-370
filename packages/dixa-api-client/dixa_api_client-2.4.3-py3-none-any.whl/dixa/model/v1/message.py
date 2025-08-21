from typing import List, Literal, Optional, TypedDict, Union


class Attachment(TypedDict):
    prettyName: str
    url: str


Direction = Literal["Inbound", "Outbound"]


class CallRecordingAttributes(TypedDict):
    duration: Optional[int]
    recording: str
    _type: Literal["CallRecordingAttributes"]


class HtmlContent(TypedDict):
    value: str
    _type: Literal["Html"]


class TextContent(TypedDict):
    value: str
    _type: Literal["Text"]


Content = Union[HtmlContent, TextContent]


class EmailContent(TypedDict):
    content: Content


class EmailContact(TypedDict):
    email: str
    name: str


class File(TypedDict):
    prettyName: str
    url: str


class _ChatAttributesRequired(TypedDict):
    isAutomated: bool
    _type: Literal["ChatAttributes"]


class _ChatAttributesOptional(TypedDict, total=False):
    attachments: List[Attachment]
    content: Content
    direction: Direction


class ChatAttributes(_ChatAttributesRequired, _ChatAttributesOptional):
    pass


class _ContactFormAttributesRequired(TypedDict):
    isAutoReply: bool
    _type: Literal["ContactFormAttributes"]


class _ContactFormAttributesOptional(TypedDict, total=False):
    attachments: List[Attachment]
    bcc: List[EmailContact]
    cc: List[EmailContact]
    deliveryFailureReason: str
    direction: Direction
    emailContent: EmailContent
    from_: EmailContact
    inlineImages: List[File]
    originalContentUrl: File
    replyDefaultToEmails: List[EmailContact]
    to: List[EmailContact]


class ContactFormAttributes(
    _ContactFormAttributesRequired, _ContactFormAttributesOptional
):
    pass


class _EmailAttributesRequired(TypedDict):
    from_: EmailContact
    isAutoReply: bool
    _type: Literal["EmailAttributes"]


class _EmailAttributesOptional(TypedDict, total=False):
    attachments: List[Attachment]
    bcc: List[EmailContact]
    cc: List[EmailContact]
    deliveryFailureReason: str
    direction: Direction
    emailContent: EmailContent
    inlineImages: List[File]
    originalContentUrl: File
    replyDefaultToEmails: List[EmailContact]
    to: List[EmailContact]


class EmailAttributes(_EmailAttributesRequired, _EmailAttributesOptional):
    pass


class _FacebookMessengerAttributesRequired(TypedDict):
    _type: Literal["FacebookMessengerAttributes"]


class _FacebookMessengerAttributesOptional(TypedDict, total=False):
    attachments: List[Attachment]
    content: Content
    direction: Direction


class FacebookMessengerAttributes(
    _FacebookMessengerAttributesRequired, _FacebookMessengerAttributesOptional
):
    pass


class _GenericAttributesRequired(TypedDict):
    _type: Literal["GenericAttributes"]


class _GenericAttributesOptional(TypedDict, total=False):
    attachments: List[Attachment]
    content: Content
    direction: Direction


class GenericAttributes(_GenericAttributesRequired, _GenericAttributesOptional):
    pass


class _PhoneAttributesRequired(TypedDict):
    from_: str
    to: str
    _type: Literal["PhoneAttributes"]


class _PhoneAttributesOptional(TypedDict, total=False):
    direction: Direction
    duration: int


class PhoneAttributes(_PhoneAttributesRequired, _PhoneAttributesOptional):
    pass


class _SmsAttributesRequired(TypedDict):
    _type: Literal["SmsAttributes"]


class _SmsAttributesOptional(TypedDict, total=False):
    attachments: List[Attachment]
    content: Content
    direction: Direction


class SmsAttributes(_SmsAttributesRequired, _SmsAttributesOptional):
    pass


class _TwitterAttributesRequired(TypedDict):
    _type: Literal["TwitterAttributes"]


class _TwitterAttributesOptional(TypedDict, total=False):
    attachments: List[Attachment]
    content: Content
    direction: Direction


class TwitterAttributes(_TwitterAttributesRequired, _TwitterAttributesOptional):
    pass


class _WhatsAppAttributesRequired(TypedDict):
    _type: Literal["WhatsAppAttributes"]


class _WhatsAppAttributesOptional(TypedDict, total=False):
    attachments: List[Attachment]
    content: Content
    direction: Direction


class WhatsAppAttributes(_WhatsAppAttributesRequired, _WhatsAppAttributesOptional):
    pass


MessageAttributes = Union[
    CallRecordingAttributes,
    ChatAttributes,
    ContactFormAttributes,
    EmailAttributes,
    FacebookMessengerAttributes,
    GenericAttributes,
    PhoneAttributes,
    SmsAttributes,
    TwitterAttributes,
    WhatsAppAttributes,
]


class Message(TypedDict):
    id: str
    authorId: str
    externalId: Optional[str]
    createdAt: str
    attributes: MessageAttributes
