from pydantic import BaseModel, Field, AliasChoices, model_validator
from typing import Literal, Union, List, Optional

class TimeResolutionDataV0(BaseModel):
    side:              Union[None,Literal["A", "B"]] = Field(validation_alias=AliasChoices('side','Side'))
    geometry:          Union[None,Literal["1x1 LGAD", "1x1 PIN", "1x2 PIN"]] = Field(validation_alias=AliasChoices('geometry','geometry'))
    irradiation_level: Union[None, float]      = Field(validation_alias=AliasChoices('irradiation_level','Irradiation Level'))
    measuring_temperature: Union[None, float]      = Field(validation_alias=AliasChoices('measuring_temperature','Measuring Temperature'))
    time_resolution:   Union[None,List[float]] = Field(validation_alias=AliasChoices('time_resolution','Time Resolution'))
    voltage:           Union[None,List[float]] = Field(validation_alias=AliasChoices('voltage','Voltage'))
    
    @model_validator(mode='after')
    def same_lengths(self):
        if len(self.time_resolution) != len(self.voltage):
            raise ValueError(f'Time Resolution and Voltage arrays should have the same lengths. Length of Time Resolution, Length of Voltage = ({len(self.time_resolution)}, {len(self.voltage)})')
        return self