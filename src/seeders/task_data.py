"""Sample task data creation."""

import uuid
import random
from sqlalchemy.orm import Session
from src.models.task_ai_image_voice_canva_instagram import TaskAIImageVoiceCanvaInstagram


def truncate_string(value: str, max_length: int = 50) -> str:
    """
    Truncate string to fit within max_length.
    
    Args:
        value: String to truncate
        max_length: Maximum length (default: 50)
        
    Returns:
        Truncated string
    """
    if value is None:
        return None
    return value[:max_length] if len(value) > max_length else value


def create_task_sample_data(session: Session, count: int = 10, force: bool = False):
    """Create sample task data.
    
    Args:
        session: Database session
        count: Number of tasks to create
        force: If True, create tasks even if they already exist
    """
    try:
        # Check if tasks already exist
        existing_tasks = session.query(TaskAIImageVoiceCanvaInstagram).count()
        
        if existing_tasks > 0 and not force:
            print(f"Tasks already exist ({existing_tasks} records). Skipping creation.")
            print("To force creation, use force=True")
            return
        
        if force and existing_tasks > 0:
            print(f"Force mode: Creating {count} new tasks (existing: {existing_tasks})")
        
        # Sample data pools for generating fake data
        sheet_names = ["Content Plan Q1", "Social Media Tasks", "Video Production", "Instagram Posts", "Marketing Campaign"]
        account_socials = ["@tech_lifestyle", "@fitness_motivation", "@food_blogger", "@travel_diary", "@fashion_style"]
        type_ratios = ["16:9", "9:16", "1:1", "4:5"]
        channels = ["Instagram", "TikTok", "YouTube", "Facebook", "Twitter"]
        type_posts = ["Reel", "Story", "Post", "Carousel", "IGTV"]
        statuses = ["Pending", "In Progress", "Completed", "Failed"]
        niches = ["Tech", "Fitness", "Food", "Travel", "Fashion", "Lifestyle"]
        styles = ["Modern", "Vintage", "Minimalist", "Bold", "Elegant"]
        fonts = ["Arial", "Roboto", "Montserrat", "Open Sans", "Poppins"]
        backgrounds = ["Gradient", "Solid", "Pattern", "Image", "Transparent"]
        effects = ["Fade", "Zoom", "Slide", "None", "Blur"]
        
        tasks = []
        
        for i in range(count):
            task_id = str(uuid.uuid4())
            sheet_id = f"SHEET{random.randint(1000, 9999)}"
            row_id = f"ROW{random.randint(1, 100)}"
            row_num = str(random.randint(1, 100))
            
            # Generate fake URLs
            base_url = "https://example.com"
            sheet_url = f"{base_url}/sheets/{sheet_id}"
            thumb_url = f"{base_url}/images/thumb_{random.randint(1000, 9999)}.jpg"
            page1_url = f"{base_url}/images/page1_{random.randint(1000, 9999)}.jpg"
            page2_url = f"{base_url}/images/page2_{random.randint(1000, 9999)}.jpg"
            page3_url = f"{base_url}/images/page3_{random.randint(1000, 9999)}.jpg"
            page4_url = f"{base_url}/images/page4_{random.randint(1000, 9999)}.jpg"
            page5_url = f"{base_url}/images/page5_{random.randint(1000, 9999)}.jpg"
            voice1_url = f"{base_url}/audio/voice1_{random.randint(1000, 9999)}.mp3"
            voice3456_url = f"{base_url}/audio/voice3456_{random.randint(1000, 9999)}.mp3"
            canva_script = f"{base_url}/canva/script_{random.randint(1000, 9999)}.js"
            canva_video = f"{base_url}/canva/video_{random.randint(1000, 9999)}.mp4"
            
            # Generate short prompts (max 40 chars to allow for suffixes)
            short_prompts = [
                f"{random.choice(niches).lower()} themed",
                f"{random.choice(['modern', 'vintage'])} style",
                f"{random.choice(['health', 'tech'])} content",
                f"{random.choice(['thumb', 'banner'])} design",
                f"{random.choice(['IG', 'TT', 'YT'])} platform"
            ]
            
            # Truncate all values to fit VARCHAR(50) limits
            task = TaskAIImageVoiceCanvaInstagram(
                id=task_id,
                version=1,
                sheetUrl=truncate_string(sheet_url, 50),
                sheetName=truncate_string(random.choice(sheet_names), 50),
                sheetID=truncate_string(sheet_id, 50),
                rowID=truncate_string(row_id, 50),
                row=truncate_string(row_num, 50),
                accountSocial=truncate_string(random.choice(account_socials), 50),
                typeRatioImage=truncate_string(random.choice(type_ratios), 20),
                accountAIImageInfo=truncate_string(f"AI_IMG_{random.randint(100, 999)}", 50),
                accountEmailImage=truncate_string(f"img{random.randint(1, 10)}@ex.com", 50),
                accountAIImage=truncate_string(f"ai_acc_{random.randint(1, 5)}", 50),
                channelImage=truncate_string(random.choice(channels), 50),
                promptThumbInput=truncate_string(random.choice(short_prompts) + " thumb", 50),
                thumbOutputUrl=truncate_string(thumb_url, 50),
                promptPage1Input=truncate_string(random.choice(short_prompts) + " p1", 50),
                page1OutputUrl=truncate_string(page1_url, 50),
                promptPage2Input=truncate_string(random.choice(short_prompts) + " p2", 50),
                page2OutputUrl=truncate_string(page2_url, 50),
                promptNichePage3Input=truncate_string(random.choice(short_prompts) + f" {random.choice(niches)[:5]} p3", 50),
                nichePage3OutputUrl=truncate_string(page3_url, 50),
                promptNichePage4Input=truncate_string(random.choice(short_prompts) + f" {random.choice(niches)[:5]} p4", 50),
                nichePage4OutputUrl=truncate_string(page4_url, 50),
                promptNichePage5Input=truncate_string(random.choice(short_prompts) + f" {random.choice(niches)[:5]} p5", 50),
                nichePage5OutputUrl=truncate_string(page5_url, 50),
                channelVoice=truncate_string(random.choice(channels), 50),
                accountAIVoice=truncate_string(f"ai_voice_{random.randint(1, 5)}", 50),
                accountAIVoiceInfo=truncate_string(f"VOICE_{random.randint(100, 999)}", 50),
                accountEmailVoice=truncate_string(f"voice{random.randint(1, 10)}@ex.com", 50),
                promptVoicePage1Input=truncate_string(random.choice(short_prompts) + " v1", 50),
                voicePage1OutputUrl=truncate_string(voice1_url, 50),
                promptVoicePage3456Input=truncate_string(random.choice(short_prompts) + " v3456", 50),
                voicePage3456OutputUrl=truncate_string(voice3456_url, 50),
                billetCharacterVoiceSpeaker1=truncate_string(f"Spk_{random.choice(['M', 'F'])}_1", 50),
                billetCharacterVoiceSpeaker2=truncate_string(f"Spk_{random.choice(['M', 'F'])}_2", 50),
                typePost=truncate_string(random.choice(type_posts), 50),
                titlePool=truncate_string(f"Title Pool {random.randint(1, 10)}", 50),
                pool1=truncate_string(f"Pool1 Opt{random.randint(1, 5)}", 50),
                pool2=truncate_string(f"Pool2 Opt{random.randint(1, 5)}", 50),
                pool3=truncate_string(f"Pool3 Opt{random.randint(1, 5)}", 50),
                textFirstPage2=truncate_string(f"Text1 p2 {random.choice(niches)[:10]}", 50),
                textSecondPage2=truncate_string(f"Text2 p2 {random.choice(niches)[:10]}", 50),
                textPage6=truncate_string(f"Text p6 {random.choice(niches)[:15]}", 50),
                linkAddHistory=truncate_string(f"{base_url}/h/{random.randint(1000, 9999)}", 50),
                nicheLinkCategory=truncate_string(random.choice(niches), 50),
                styleName=truncate_string(random.choice(styles), 50),
                backgroundForPage3=truncate_string(random.choice(backgrounds), 50),
                backgroundForPage4=truncate_string(random.choice(backgrounds), 50),
                backgroundForPage5=truncate_string(random.choice(backgrounds), 50),
                backgroundForPage6=truncate_string(random.choice(backgrounds), 50),
                effectAudioThumbnail=truncate_string(random.choice(effects), 50),
                effectAudioPage345=truncate_string(random.choice(effects), 50),
                bgRemoveBackground345=truncate_string(random.choice(["Yes", "No", "Auto"]), 50),
                fontText1=truncate_string(random.choice(fonts), 50),
                fontText2=truncate_string(random.choice(fonts), 50),
                linkCanvaScript=truncate_string(canva_script, 50),
                linkCanvaVideo=truncate_string(canva_video, 50),
                linkCanvaImageThumb=truncate_string(f"{base_url}/c/t_{random.randint(1000, 9999)}.jpg", 50),
                linkCanvaImage1=truncate_string(f"{base_url}/c/i1_{random.randint(1000, 9999)}.jpg", 50),
                linkCanvaImage2=truncate_string(f"{base_url}/c/i2_{random.randint(1000, 9999)}.jpg", 50),
                linkCanvaImage3=truncate_string(f"{base_url}/c/i3_{random.randint(1000, 9999)}.jpg", 50),
                linkCanvaImage4=truncate_string(f"{base_url}/c/i4_{random.randint(1000, 9999)}.jpg", 50),
                linkCanvaImage5=truncate_string(f"{base_url}/c/i5_{random.randint(1000, 9999)}.jpg", 50),
                note=f"Sample note for task {i+1}. This is a test task with fake data for {random.choice(niches)} niche.",
                statusImage=truncate_string(random.choice(statuses), 20),
                statusVoice=truncate_string(random.choice(statuses), 20),
                statusCanva=truncate_string(random.choice(statuses), 20),
                createdBy=truncate_string(f"user_{random.randint(1, 5)}", 50),
                updatedBy=truncate_string(f"user_{random.randint(1, 5)}", 50) if random.random() > 0.3 else None
            )
            
            tasks.append(task)
        
        # Bulk insert
        try:
            session.add_all(tasks)
            session.commit()
            print(f"Successfully created {count} task sample records!")
            return tasks
        except Exception as commit_error:
            session.rollback()
            print(f"Error committing task data: {commit_error}")
            raise
        
    except Exception as e:
        session.rollback()
        print(f"Error creating task sample data: {e}")
        import traceback
        traceback.print_exc()
        raise

