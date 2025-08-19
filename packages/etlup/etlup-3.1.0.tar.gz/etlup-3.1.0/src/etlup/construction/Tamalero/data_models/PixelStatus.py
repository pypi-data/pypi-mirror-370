from pydantic import BaseModel, field_validator
import numpy as np
from typing import List

class PixelStatusV0(BaseModel):
    pixel_map: List[List[int]]

    @field_validator('pixel_map')
    @classmethod
    def length_check(cls, v):
        v_arr = np.array(v)
        if v_arr.shape != (16,16):
            raise ValueError(f"Your array is not the correct shape, it should be 16x16, you gave: {v_arr.shape}")
        return v