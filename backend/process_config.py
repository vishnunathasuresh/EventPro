from dataclasses import dataclass
from pyclbr import Class
from backend.config import CONFIG
from PIL import Image, ImageDraw, ImageFont




@dataclass
class NameConfig:
    coordinates: list[int]
    size: str
    height: int = 10

@dataclass
class ClassDivisionConfig:
    coordinates: list[int]
    size: str
    height: int = 10

@dataclass
class CategoryEventConfig:
    coordinates: list[int]
    size: str
    height: int = 10

@dataclass
class DateConfig:
    coordinates: list[int]
    size: str
    height: int = 10

@dataclass
class PrizeConfig: 
    coordinates: list[int]
    size: str
    height: int = 10

@dataclass
class FontConfig:
    ttf: str
    big: int
    medium: int
    small: int


@dataclass
class Config:
    sample_certificate: str
    font: FontConfig
    font_color: str
    name: NameConfig
    class_division: ClassDivisionConfig
    category_event: CategoryEventConfig
    date: DateConfig
    prize: PrizeConfig


