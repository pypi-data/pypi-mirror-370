from enum import StrEnum


class ChannelSource(StrEnum):
    WAHA_WHATSAPP = "waha_whatsapp"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"


class ChannelStatus(StrEnum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE" 