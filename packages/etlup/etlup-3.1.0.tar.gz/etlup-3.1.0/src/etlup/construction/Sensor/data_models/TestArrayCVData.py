from pydantic import BaseModel, Field, AliasChoices, model_validator
from typing import Literal, Union, List, Optional

class TestArrayCVDataV0(BaseModel):
    vgl:             Union[None,float] = Field(validation_alias=AliasChoices('vgl_V','vgl'))
    vbulk:           Union[None,float] = Field(validation_alias=AliasChoices('vbulk_V','vbulk'))
    side:            Union[None,Literal["A", "B"]] = Field(validation_alias=AliasChoices('side','Side'))
    geometry:        Union[None,Literal["1x1 LGAD", "1x1 PIN", "1x2 PIN"]] = Field(validation_alias=AliasChoices('geometry','Geometry'))
    gain_category:   Union[None,Literal["A", "B", "C"]] = Field(validation_alias=AliasChoices('gain_category','Gain Category'))

    voltage: Union[None,List[float]] = Field(validation_alias=AliasChoices('voltage','Voltage'))
    capacitance: Union[None,List[float]] = Field(validation_alias=AliasChoices('capacitance','Capacitance'))
    
    @model_validator(mode='after')
    def same_lengths(self):
        if len(self.voltage) != len(self.capacitance):
            raise ValueError(f'Voltage and Capacitance arrays should have the same lengths. Length of Voltage, Length of Capacitance = ({len(self.voltage)}, {len(self.capacitance)})')
        return self