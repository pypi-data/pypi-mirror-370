from pydantic import BaseModel, Field, AliasChoices, model_validator
from typing import Literal, Union, List, Optional

class CurrentUniformityDataV0(BaseModel):
    current_uniformity: Union[None,Literal["A", "B", "C"]] = Field(validation_alias=AliasChoices('current_uniformity','Current Uniformity'))
    current:            Union[None,List[List[float]]] = Field(validation_alias=AliasChoices('current','Current'))
    voltage:            Union[None,List[List[float]]] = Field(validation_alias=AliasChoices('voltage','Voltage'))

    @model_validator(mode='after')
    def same_lengths(self):
        if len(self.current) != len(self.voltage):
            raise ValueError(f'Current and voltage arrays should have the same lengths. Length of Current, Length of Voltage = ({len(self.current)}, {len(self.voltage)})')
        return self
    
    @model_validator(mode='after')
    def max_length(self):
        if len(self.current) > 256 or len(self.voltage) > 256:
            raise ValueError(f'Length of Current, Length of Voltage = ({len(self.current)}, {len(self.voltage)}) one of these is longer than 256, the max number of arrays.')
        return self