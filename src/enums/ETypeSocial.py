from enum import Enum


class ETypeSocial(Enum):
    INSTAGRAM = "Instagram"
    FACEBOOK = "Facebook"
    TIKTOK = "TikTok"
    TWITTER = "Twitter"
    YOUTUBE = "YouTube"
    LINKEDIN = "LinkedIn"
    
    @classmethod
    def from_value(cls, value: str) -> 'ETypeSocial':
        return cls(value)
