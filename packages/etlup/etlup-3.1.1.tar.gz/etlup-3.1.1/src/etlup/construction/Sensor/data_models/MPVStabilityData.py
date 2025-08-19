from pydantic import BaseModel, Field, AliasChoices, model_validator
from typing import Literal, Union, List, Optional

class MPVStabilityDataV0(BaseModel):
    side:     Union[None,Literal["A", "B"]] = Field(validation_alias=AliasChoices('side','Side'))
    geometry: Union[None,Literal["1x1 LGAD", "1x1 PIN", "1x2 PIN"]] = Field(validation_alias=AliasChoices('geometry','Geometry'))
    mpv:      Union[None,List[float]] = Field(validation_alias=AliasChoices('mpv','MPV'))
    time:     Union[None,List[float]] = Field(validation_alias=AliasChoices('time','Time'))
    mpv_stability: Union[None,float] = Field(validation_alias=AliasChoices('mpv_stability','MPV Stability'))
    
    @model_validator(mode='after')
    def same_lengths(self):
        if len(self.mpv) != len(self.time):
            raise ValueError(f'MPV and Time arrays should have the same lengths. Length of MPV, Length of Time = ({len(self.time)}, {len(self.mpv)})')
        return self