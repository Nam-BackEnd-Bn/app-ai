"""Task service for business logic."""

from typing import List, Optional, Dict
from src.repositories.task_ai_image_voice_canva_instagram_repository import TaskAIImageVoiceCanvaInstagramRepository
from src.models.task_ai_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram
from datetime import datetime
from random import choice
from pydantic import BaseModel
class TaskAIImageVoiceCanvaInstagramResponse(BaseModel):
    id: str
    version: int
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    sheetUrl: Optional[str] = None
    sheetName: Optional[str] = None
    sheetID: Optional[str] = None
    rowID: Optional[str] = None
    row: Optional[str] = None
    accountSocial: Optional[str] = None
    typeRatioImage: Optional[str] = None
    accountAIImageInfo: Optional[str] = None
    accountEmailImage: Optional[str] = None
    accountAIImage: Optional[str] = None
    channelImage: Optional[str] = None
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
    typePost: Optional[str] = None
    titlePool: Optional[str] = None
    pool1: Optional[str] = None
    pool2: Optional[str] = None
    pool3: Optional[str] = None
    textFirstPage2: Optional[str] = None
    textSecondPage2: Optional[str] = None
    textPage6: Optional[str] = None
    linkAddHistory: Optional[str] = None
    nicheLinkCategory: Optional[str] = None
    styleName: Optional[str] = None
    backgroundForPage3: Optional[str] = None
    backgroundForPage4: Optional[str] = None
    backgroundForPage5: Optional[str] = None
    backgroundForPage6: Optional[str] = None
    effectAudioThumbnail: Optional[str] = None
    effectAudioPage345: Optional[str] = None
    bgRemoveBackground345: Optional[str] = None
    fontText1: Optional[str] = None
    fontText2: Optional[str] = None
    linkCanvaScript: Optional[str] = None
    linkCanvaVideo: Optional[str] = None
    linkCanvaImageThumb: Optional[str] = None
    linkCanvaImage1: Optional[str] = None
    linkCanvaImage2: Optional[str] = None
    linkCanvaImage3: Optional[str] = None
    linkCanvaImage4: Optional[str] = None
    linkCanvaImage5: Optional[str] = None
    note: Optional[str] = None
    statusImage: Optional[str] = None
    statusVoice: Optional[str] = None
    statusCanva: Optional[str] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    promptFlowInputs: Optional[List[Dict]] = None

class TaskAIImageVoiceCanvaInstagramService:
    """Service for task-related business logic."""

    def __init__(self, repository: TaskAIImageVoiceCanvaInstagramRepository):
        """
        Initialize service with repository.
        
        Args:
            repository: TaskAIImageVoiceCanvaInstagramRepository instance
        """
        self.repository = repository

    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task dictionary or None if not found
        """
        task = self.repository.get_by_id(task_id)
        return task.to_dict() if task else None

    def get_all_tasks(self, page: int = 1, per_page: int = 10) -> Dict:
        """
        Get paginated list of tasks.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            
        Returns:
            Dictionary with tasks, total count, and pagination info
        """
        tasks, total = self.repository.get_paginated(page, per_page)

        return {
            'tasks': [task.to_dict() for task in tasks],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
        }

    def get_task_by_account_social(self) -> Optional[List]:
        return [
            TaskAIImageVoiceCanvaInstagramResponse(
                id="1", # TODO: Change to UUID
                version=1,
                sheetUrl="https://docs.google.com/spreadsheets/d/1234567890/edit#gid=0",
                sheetName="Sheet1",
                sheetID="1234567890",
                rowID="1",
                row="1",
                accountSocial="00000000-0000-0000-0000-000000000000", # TODO: Change to UUID
                typeRatioImage="16:9",
                accountAIImageInfo="AI_IMG_123",
                accountEmailImage="img123@ex.com",
                accountAIImage="ai_acc_123",
                channelImage="Instagram",
                # Generate random meaning prompt for thumbnail and pages
                promptThumbInput=choice([
                    "A peaceful sunrise over misty mountains",
                    "An astronaut exploring an underwater city",
                    "Colorful autumn leaves falling in a forest",
                    "A cozy reading nook by a rainy window",
                    "Futuristic city skyline at night"
                ]),
                thumbOutputUrl="",
                promptPage1Input=choice([
                    "A close-up shot of a mechanical wristwatch",
                    "A vibrant street food market at dusk",
                    "Abstract art with blue and gold tones",
                    "A dog and a cat playing in a garden",
                    "A detailed macro of dew on a spiderweb"
                ]),
                page1OutputUrl="",
                promptPage2Input=choice([
                    "A wise old man telling stories to children",
                    "A magical forest illuminated by glowing plants",
                    "Vintage bicycle leaning against a red brick wall",
                    "A bustling metropolitan subway platform",
                    "A tranquil zen garden with raked sand"
                ]),
                page2OutputUrl="",
                promptNichePage3Input=choice([
                    "Minimalist workspace with natural light",
                    "A surfer catching a wave at golden hour",
                    "An enchanted castle floating in the sky",
                    "Exotic birds perched among tropical flowers",
                    "Snow-capped peaks reflected in a lake"
                ]),
                nichePage3OutputUrl="",
                promptNichePage4Input=choice([
                    "A steaming bowl of ramen on a wooden table",
                    "Cyberpunk city streets with neon signs",
                    "Children flying kites in an open field",
                    "A creative artist painting a mural",
                    "Night sky full of shooting stars over calm ocean"
                ]),
                nichePage4OutputUrl="",
                promptNichePage5Input=choice([
                    "A vintage record player and vinyls",
                    "A mountain biker on a winding forest trail",
                    "Close-up of delicate cherry blossoms",
                    "A friendly robot serving tea",
                    "Glowing lanterns floating into the night sky"
                ]),
                nichePage5OutputUrl="",
                channelVoice="TikTok",
                accountAIVoice="AI_VOICE_123",
                accountAIVoiceInfo="AI_VOICE_INFO_123",
                accountEmailVoice="voice123@ex.com",
                promptVoicePage1Input="""Speaker 1: No waylook who it is! Feels like a whole era just passed   
Speaker 2: Right? And perfect timing theres a pug quiz thats got me obsessed.  
Speaker 1: Oh no. What did those wrinkly troublemakers do now?
...!
""",
                voicePage1OutputUrl="",
                promptVoicePage3456Input="""
Speaker 1: No waylook who it is! Feels like a whole era just passed   
Speaker 2: Right? And perfect timing theres a pug quiz thats got me obsessed.  
Speaker 1: Oh no. What did those wrinkly troublemakers do now?   
...!
""",
                voicePage3456OutputUrl="",
                billetCharacterVoiceSpeaker1="Speaker 1",
                billetCharacterVoiceSpeaker2="Speaker 2",
                typePost="Reel",
                titlePool="Title pool",
                pool1="Pool 1",
                pool2="Pool 2",
                pool3="Pool 3",
                textFirstPage2="Text first page 2",
                textSecondPage2="Text second page 2",
                textPage6="Text page 6",
                linkAddHistory="https://example.com/addhistory",
                nicheLinkCategory="Niche link category",
                styleName="Style name",
                backgroundForPage3="Background for page 3",
                backgroundForPage4="Background for page 4",
                backgroundForPage5="Background for page 5",
                backgroundForPage6="Background for page 6",
                effectAudioThumbnail="Effect audio thumbnail",
                effectAudioPage345="Effect audio page 345",
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
                promptFlowInputs=[
                    {
                        # 'video': 'A graceful contemporary dance on a minimalist stage with soft white and blue lighting. A female dancer in flowing fabric performs slow, expressive movements with spins and leaps. Camera uses slow dolly-in and side angles, shallow depth of field. Clean background, emotional mood, cinematic look, 4K, high detail, smooth slow-motion segments.',
                        'video': '',
                        'thumbnail': 'Children flying kites in an open field'
                    },
                    # {
                    #     'video': 'A high-energy street dance performance at night in a neon-lit city. A single dancer performs sharp hip-hop and popping moves, dynamic footwork, smooth transitions. Camera starts with a wide shot, then tracks forward and circles the dancer. Realistic lighting, rain reflections on the ground, cinematic motion blur, 4K, 60fps, ultra-smooth movement.',
                    #     'thumbnail': 'A high-energy street dance performance at night in a neon-lit city. A single dancer performs sharp hip-hop and popping moves, dynamic footwork, smooth transitions. Camera starts with a wide shot, then tracks forward and circles the dancer. Realistic lighting, rain reflections on the ground, cinematic motion blur, 4K, 60fps, ultra-smooth movement.',
                    # },
                ]
            )
        ]
