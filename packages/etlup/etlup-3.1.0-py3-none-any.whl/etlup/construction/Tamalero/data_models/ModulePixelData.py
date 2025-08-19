from pydantic import BaseModel, field_validator, model_validator, Field, AliasChoices, ConfigDict
import numpy as np
from typing import List, Optional

class ModulePixelDataV0(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pos_3: Optional[List[List[int]]] = Field(
        default=None,
        validation_alias=AliasChoices('3', 'U4'),
        serialization_alias="3"
    )
    pos_1: Optional[List[List[int]]] = Field(
        default=None,
        validation_alias=AliasChoices('1', 'U3'),
        serialization_alias="1"
    )
    pos_2: Optional[List[List[int]]] = Field(
        default=None,
        validation_alias=AliasChoices('2', 'U2'),
        serialization_alias="2"
    )
    pos_0: Optional[List[List[int]]] = Field(
        default=None,
        validation_alias=AliasChoices('0', 'U1'),
        serialization_alias="0"
    )

    # Read-only convenience properties matching old names
    @property
    def U4(self):
        return self.pos_3
    @property
    def U3(self):
        return self.pos_1
    @property
    def U2(self):
        return self.pos_2
    @property
    def U1(self):
        return self.pos_0

    @model_validator(mode='after')
    def at_least_one_required(self):
        if not any([self.pos_0, self.pos_1, self.pos_2, self.pos_3]):
            raise ValueError("At least one position must be provided")
        return self

    @field_validator('*')
    @classmethod
    def length_check(cls, v):
        if v is None: 
            return v
        v_arr = np.array(v)
        if v_arr.shape != (16,16):
            raise ValueError(f"Your array is not the correct shape, it should be 16x16, you gave: {v_arr.shape}")
        return v

    @model_validator(mode='before')
    @classmethod
    def coerce_int_keys_to_str(cls, value):
        # Accept both {"0": ...} and {0: ...}
        if isinstance(value, dict):
            return { str(k): v for k, v in value.items() }
        return value
