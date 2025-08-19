from pydantic import BaseModel, Field, AliasChoices, model_validator
from typing import Literal, Union, List, Optional

class CurrentStabilityDataV0(BaseModel):
    # vgl_V: Optional[List[float]] = None
    current_stability: Union[None,Literal["A", "B", "C"]]
    current: Union[None,List[float]] = Field(validation_alias=AliasChoices('current','Current'))
    time: Union[None,List[float]] = Field(validation_alias=AliasChoices('time','Time'))
    
    @model_validator(mode='after')
    def same_lengths(self):
        if len(self.current) != len(self.time):
            raise ValueError(f'Current and Time arrays should have the same lengths. Length of Current, Length of Time = ({len(self.current)}, {len(self.time)})')
        return self