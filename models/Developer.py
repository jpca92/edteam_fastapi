from pydantic import BaseModel, Field
from typing import List

from .Skill import Skill
from .Experience import Experience
from .Languages import Language

class Developer(BaseModel):
    id: int = Field(gt=0)
    name: str
    country: str
    age: int = Field(gt=0)
    skills: List[Skill]
    experience: List[Experience]
    languages: List[Language]
