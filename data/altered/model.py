from pydantic import BaseModel
from enum import Enum

class Energy(Enum):
    NONE = "none"
    EXO = "exo"
    ENDO = "endo"

class Met(BaseModel):
    name: str
    coef: float

class Rxn(BaseModel):
    name: str
    subs: list[Met]
    prod: list[Met]
    energy: Energy
    reversible: bool 
