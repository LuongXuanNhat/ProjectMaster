from dataclasses import dataclass
from enum import Enum


class Sentiment(float, Enum):
    NEGATIVE = 0.0 # Tiêu cực
    NEUTRAL = 0.5 # Trung tính: Không rõ ràng
    POSITIVE = 1.0 # Tích cực


@dataclass
class Label:
    name: str
    value: Sentiment


# 5 loại nhãn
LABEL_NAMES = [
    "Food quality",
    "Price",
    "Service quality",
    "Hygiene and safety",
    "Atmosphere",
]