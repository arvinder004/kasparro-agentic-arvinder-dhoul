from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ProductData(BaseModel):
    name: str
    concentration: str
    skin_type: List[str]
    ingredients: List[str]
    benefits: List[str]
    how_to_use: str
    side_effects: str
    price: int

class Section(BaseModel):
    heading: str
    content: str | List[Dict]

class PageOutput(BaseModel):
    page_type: str
    sections: List[Section]
    meta_tags: List[str]
    