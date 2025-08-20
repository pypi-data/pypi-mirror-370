from enum import StrEnum


class MessageStatusType(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class TrafficType(StrEnum):
    OUTGOING = "OUTGOING"
    INCOMING = "INCOMING"


class AttachmentType(StrEnum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    DOCUMENT = "document" 