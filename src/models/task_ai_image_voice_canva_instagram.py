"""Task AI Image Voice Canva Instagram model for database."""

from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
import uuid
from src.config.database import Base


class TaskAIImageVoiceCanvaInstagram(Base):
    """Task AI Image Voice Canva Instagram model representing a task in the database."""
    
    __tablename__ = 'tasks-ai-image-voice-canva-instagram'
    __table_args__ = {'quote': True}  # Quote table name to handle hyphens in MySQL
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    createdAt: Mapped[datetime] = mapped_column(DateTime(3), nullable=False, server_default=func.current_timestamp(3))
    updatedAt: Mapped[Optional[datetime]] = mapped_column(DateTime(3), nullable=True, onupdate=func.current_timestamp(3))
    
    # Sheet related fields
    sheetUrl: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sheetName: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sheetID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rowID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    row: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Account and social fields
    accountSocial: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Image related fields
    typeRatioImage: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    accountAIImageInfo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    accountEmailImage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    accountAIImage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    channelImage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Image prompt and output fields
    promptThumbInput: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    thumbOutputUrl: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    promptPage1Input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    page1OutputUrl: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    promptPage2Input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    page2OutputUrl: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    promptNichePage3Input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    nichePage3OutputUrl: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    promptNichePage4Input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    nichePage4OutputUrl: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    promptNichePage5Input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    nichePage5OutputUrl: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Voice related fields
    channelVoice: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    accountAIVoice: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    accountAIVoiceInfo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    accountEmailVoice: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    promptVoicePage1Input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    voicePage1OutputUrl: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    promptVoicePage3456Input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    voicePage3456OutputUrl: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    billetCharacterVoiceSpeaker1: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    billetCharacterVoiceSpeaker2: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Post and content fields
    typePost: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    titlePool: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pool1: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pool2: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pool3: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    textFirstPage2: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    textSecondPage2: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    textPage6: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkAddHistory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    nicheLinkCategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Style and background fields
    styleName: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    backgroundForPage3: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    backgroundForPage4: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    backgroundForPage5: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    backgroundForPage6: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Effect and audio fields
    effectAudioThumbnail: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    effectAudioPage345: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bgRemoveBackground345: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Font fields
    fontText1: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fontText2: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Canva link fields
    linkCanvaScript: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkCanvaVideo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkCanvaImageThumb: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkCanvaImage1: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkCanvaImage2: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkCanvaImage3: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkCanvaImage4: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkCanvaImage5: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Note field (TEXT type)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status fields
    statusImage: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    statusVoice: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    statusCanva: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Audit fields
    createdBy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    updatedBy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<TaskAIImageVoiceCanvaInstagram(id={self.id}, sheetName='{self.sheetName}', rowID='{self.rowID}')>"
    
    def to_dict(self):
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'version': self.version,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None,
            'sheetUrl': self.sheetUrl,
            'sheetName': self.sheetName,
            'sheetID': self.sheetID,
            'rowID': self.rowID,
            'row': self.row,
            'accountSocial': self.accountSocial,
            'typeRatioImage': self.typeRatioImage,
            'accountAIImageInfo': self.accountAIImageInfo,
            'accountEmailImage': self.accountEmailImage,
            'accountAIImage': self.accountAIImage,
            'channelImage': self.channelImage,
            'promptThumbInput': self.promptThumbInput,
            'thumbOutputUrl': self.thumbOutputUrl,
            'promptPage1Input': self.promptPage1Input,
            'page1OutputUrl': self.page1OutputUrl,
            'promptPage2Input': self.promptPage2Input,
            'page2OutputUrl': self.page2OutputUrl,
            'promptNichePage3Input': self.promptNichePage3Input,
            'nichePage3OutputUrl': self.nichePage3OutputUrl,
            'promptNichePage4Input': self.promptNichePage4Input,
            'nichePage4OutputUrl': self.nichePage4OutputUrl,
            'promptNichePage5Input': self.promptNichePage5Input,
            'nichePage5OutputUrl': self.nichePage5OutputUrl,
            'channelVoice': self.channelVoice,
            'accountAIVoice': self.accountAIVoice,
            'accountAIVoiceInfo': self.accountAIVoiceInfo,
            'accountEmailVoice': self.accountEmailVoice,
            'promptVoicePage1Input': self.promptVoicePage1Input,
            'voicePage1OutputUrl': self.voicePage1OutputUrl,
            'promptVoicePage3456Input': self.promptVoicePage3456Input,
            'voicePage3456OutputUrl': self.voicePage3456OutputUrl,
            'billetCharacterVoiceSpeaker1': self.billetCharacterVoiceSpeaker1,
            'billetCharacterVoiceSpeaker2': self.billetCharacterVoiceSpeaker2,
            'typePost': self.typePost,
            'titlePool': self.titlePool,
            'pool1': self.pool1,
            'pool2': self.pool2,
            'pool3': self.pool3,
            'textFirstPage2': self.textFirstPage2,
            'textSecondPage2': self.textSecondPage2,
            'textPage6': self.textPage6,
            'linkAddHistory': self.linkAddHistory,
            'nicheLinkCategory': self.nicheLinkCategory,
            'styleName': self.styleName,
            'backgroundForPage3': self.backgroundForPage3,
            'backgroundForPage4': self.backgroundForPage4,
            'backgroundForPage5': self.backgroundForPage5,
            'backgroundForPage6': self.backgroundForPage6,
            'effectAudioThumbnail': self.effectAudioThumbnail,
            'effectAudioPage345': self.effectAudioPage345,
            'bgRemoveBackground345': self.bgRemoveBackground345,
            'fontText1': self.fontText1,
            'fontText2': self.fontText2,
            'linkCanvaScript': self.linkCanvaScript,
            'linkCanvaVideo': self.linkCanvaVideo,
            'linkCanvaImageThumb': self.linkCanvaImageThumb,
            'linkCanvaImage1': self.linkCanvaImage1,
            'linkCanvaImage2': self.linkCanvaImage2,
            'linkCanvaImage3': self.linkCanvaImage3,
            'linkCanvaImage4': self.linkCanvaImage4,
            'linkCanvaImage5': self.linkCanvaImage5,
            'note': self.note,
            'statusImage': self.statusImage,
            'statusVoice': self.statusVoice,
            'statusCanva': self.statusCanva,
            'createdBy': self.createdBy,
            'updatedBy': self.updatedBy
        }

