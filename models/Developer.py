from pydantic import BaseModel
from typing import List

from .Skill import Skill
from .Experience import Experience
from .Languages import Language

class Developer(BaseModel):
    id: int
    name: str
    country: str
    age: int
    skills: List[Skill]
    experience: List[Experience]
    languages: List[Language]