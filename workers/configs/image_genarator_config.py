import random

class ImageGeneratorConstants:
    """Constants for image generation."""

    # Timeouts
    CLICK_TIMEOUT = 60
    DEFAULT_TIMEOUT = 10
    UPLOAD_CHECK_INTERVAL = 1
    MAX_UPLOAD_CHECK_TIME = 30

    # Sleep durations
    SLEEP_AFTER_FILE_SEND = random.randint(3, 6)
    SLEEP_AFTER_SCENE_UPLOAD = 8
    SLEEP_AFTER_STYLE_UPLOAD = 5
    SLEEP_AFTER_SUBMIT = random.randint(7, 10)
    SLEEP_AFTER_GENERATION_CHECK = 5
    SLEEP_BEFORE_SCROLL = 1
    SLEEP_FOR_PREPARE_UPLOAD = 10
    SLEEP_AFTER_DELETE = 1
    MAX_GENERATION_CHECK = 10
    # CSS Selectors (using stable attributes instead of classes where possible)
    # Note: Some selectors may still use classes, but we prefer stable attributes like type, accept, aria-label
    TEXTAREA_CLASS = "Describe your idea or roll the dice for prompt ideas"  # May need update if this changes
    # Button texts
    BTN_ADD_IMAGES = "Add Images"
    BTN_HIDE_IMAGES = "Hide Images"
    BTN_ASPECT_RATIO_ICON = "aspect_ratio"

    # Titles
    TITLE_SUBJECT = "Subject"
    TITLE_SCENE = "Scene"
    TITLE_STYLE = "Style"

    # Aspect ratios
    RATIO_SQUARE = "1:1"
    RATIO_VERTICAL = "9:16"
    RATIO_HORIZONTAL = "16:9"

    # File names
    FILE_THUMB = "image_thumb"
    FILE_PAGE_1 = "image_page_1"
    FILE_PAGE_2 = "image_page_2"
    FILE_NICHE_3 = "image_product_niche_3"
    FILE_NICHE_4 = "image_product_niche_4"
    FILE_NICHE_5 = "image_product_niche_5"

    # Max lines for image selection
    MAX_IMAGE_SELECTION = 2
