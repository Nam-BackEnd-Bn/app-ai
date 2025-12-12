from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
    
class TaskAIImageVoiceCanvaInstagram(BaseModel):
    id: str
    version: int
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    
    # Sheet related fields
    sheetUrl: Optional[str] = None
    sheetName: Optional[str] = None
    sheetID: Optional[str] = None
    rowID: Optional[str] = None
    row: Optional[str] = None
    
    # Account and social fields
    accountSocial: Optional[str] = None
    
    # Image related fields
    typeRatioImage: Optional[Literal["16:9", "9:16", "1:1"]] = None
    accountAIImageInfo: Optional[str] = None
    accountEmailImage: Optional[str] = None
    accountAIImage: Optional[str] = None
    channelImage: Optional[str] = None
    
    # Image prompt and output fields
    promptThumbInput: Optional[str] = None
    thumbOutputUrl: Optional[str] = None
    promptPage1Input: Optional[str] = None
    page1OutputUrl: Optional[str] = None
    promptPage2Input: Optional[str] = None
    page2OutputUrl: Optional[str] = None
    promptNichePage3Input: Optional[str] = None
    nichePage3OutputUrl: Optional[str] = None
    promptNichePage4Input: Optional[str] = None
    nichePage4OutputUrl: Optional[str] = None
    promptNichePage5Input: Optional[str] = None
    nichePage5OutputUrl: Optional[str] = None
    
    # # Image subject fields (for image generation)
    # imageSubject1: Optional[str] = None
    # imageSubject2: Optional[str] = None
    # imageSubject3: Optional[str] = None
    # imageSubject4: Optional[str] = None
    # imageSubject5: Optional[str] = None
    # imageSubject6: Optional[str] = None
    
    # # Image scene fields (for image generation)
    # imageScene1: Optional[str] = None
    # imageScene2: Optional[str] = None
    # imageScene3: Optional[str] = None
    # imageScene4: Optional[str] = None
    # imageScene5: Optional[str] = None
    # imageScene6: Optional[str] = None
    
    # # Image style fields (for image generation)
    # imageStyle1: Optional[str] = None
    # imageStyle2: Optional[str] = None
    # imageStyle3: Optional[str] = None
    # imageStyle4: Optional[str] = None
    # imageStyle5: Optional[str] = None
    # imageStyle6: Optional[str] = None
    
    # Voice related fields
    channelVoice: Optional[str] = None
    accountAIVoice: Optional[str] = None
    accountAIVoiceInfo: Optional[str] = None
    accountEmailVoice: Optional[str] = None
    promptVoicePage1Input: Optional[str] = None
    voicePage1OutputUrl: Optional[str] = None
    promptVoicePage3456Input: Optional[str] = None
    voicePage3456OutputUrl: Optional[str] = None
    billetCharacterVoiceSpeaker1: Optional[str] = None
    billetCharacterVoiceSpeaker2: Optional[str] = None
    
    # Post and content fields
    typePost: Optional[Literal["text", "image", "video", "audio", "Reel"]] = None
    titlePool: Optional[str] = None
    pool1: Optional[str] = None
    pool2: Optional[str] = None
    pool3: Optional[str] = None
    textFirstPage2: Optional[str] = None
    textSecondPage2: Optional[str] = None
    textPage6: Optional[str] = None
    linkAddHistory: Optional[str] = None
    nicheLinkCategory: Optional[str] = None
    
    # Style and background fields
    styleName: Optional[str] = None
    backgroundForPage3: Optional[str] = None
    backgroundForPage4: Optional[str] = None
    backgroundForPage5: Optional[str] = None
    backgroundForPage6: Optional[str] = None
    
    # Effect and audio fields
    effectAudioThumbnail: Optional[str] = None
    effectAudioPage345: Optional[str] = None
    bgRemoveBackground345: Optional[str] = None
    
    # Font fields
    fontText1: Optional[str] = None
    fontText2: Optional[str] = None
    
    # Canva link fields
    linkCanvaScript: Optional[str] = None
    linkCanvaVideo: Optional[str] = None
    linkCanvaImageThumb: Optional[str] = None
    linkCanvaImage1: Optional[str] = None
    linkCanvaImage2: Optional[str] = None
    linkCanvaImage3: Optional[str] = None
    linkCanvaImage4: Optional[str] = None
    linkCanvaImage5: Optional[str] = None
    
    # Note field (TEXT type)
    note: Optional[str] = None
    
    # Status fields
    statusImage: Optional[str] = None
    statusVoice: Optional[str] = None
    statusCanva: Optional[str] = None
    
    # Audit fields
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
