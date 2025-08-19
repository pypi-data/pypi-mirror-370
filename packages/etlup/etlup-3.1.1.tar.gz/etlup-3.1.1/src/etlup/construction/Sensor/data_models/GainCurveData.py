from pydantic import BaseModel, Field, AliasChoices, model_validator
from typing import Literal, Union, List, Optional

class GainCurveDataV0(BaseModel):
    side:            Union[None,Literal["A", "B"]] = Field(validation_alias=AliasChoices('side','Side'))
    geometry:        Union[None,Literal["1x1 LGAD", "1x1 PIN", "1x2 PIN"]] = Field(validation_alias=AliasChoices('geometry','Geometry'))

    gain: Union[None,List[float]] = Field(validation_alias=AliasChoices('gain','Gain'))
    voltage: Union[None,List[float]] = Field(validation_alias=AliasChoices('voltage','Voltage'))
    
    @model_validator(mode='after')
    def same_lengths(self):
        if len(self.gain) != len(self.voltage):
            raise ValueError(f'Voltage and Gain arrays should have the same lengths. Length of Gain, Length of Voltage = ({len(self.gain)}, {len(self.voltage)})')
        return self