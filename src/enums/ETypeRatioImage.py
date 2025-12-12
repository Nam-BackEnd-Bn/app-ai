from enum import Enum
class ETypeRatioImage(Enum):
    SQUARE = "1:1"
    VERTICAL = "9:16"
    HORIZONTAL = "16:9"

    @classmethod
    def from_value(cls, value: str) -> 'ETypeRatioImage':
        return cls(value)