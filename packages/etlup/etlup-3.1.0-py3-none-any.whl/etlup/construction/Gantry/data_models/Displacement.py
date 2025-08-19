from pydantic import BaseModel, field_validator
from typing import List

class DisplacementV0(BaseModel):
    target: List[float]
    actual: List[float]
    delta: List[float]

    @field_validator('*')
    @classmethod
    def length_check(cls, v):
        if len(v) != 4:
            raise ValueError("The required length is 4 for target, actual and delta. It is [x, y, z, rot]")
        return v