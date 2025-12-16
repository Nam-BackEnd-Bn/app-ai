from enum import Enum


class EFolderImageAI(Enum):
    SCENE = "Scene"
    STYLE = "Style"
    SUBJECT = "Subject"


class ETypeRatioImage(Enum):
    Square = "Square"
    Vertical = "Vertical"
    Horizontal = "Horizontal"


class EStatusTaskAI(Enum):
    Spending = "Spending"
    Executing = "Executing"
    Error = "Error"
    Done = "Done"
