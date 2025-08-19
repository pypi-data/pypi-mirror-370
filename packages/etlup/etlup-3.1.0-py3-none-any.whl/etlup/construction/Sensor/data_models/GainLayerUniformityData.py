from pydantic import BaseModel, Field, AliasChoices, model_validator
from typing import Literal, Union, List, Optional

class GainLayerUniformityDataV0(BaseModel):
    gain_layer_uniformity: Union[None,Literal["A", "B", "C"]] = Field(validation_alias=AliasChoices('gain_layer_uniformity','Gain Layer Uniformity'))
    capacitance:           Union[None,List[List[float]]] = Field(validation_alias=AliasChoices('capacitance','Capacitance'))
    voltage:               Union[None,List[List[float]]] = Field(validation_alias=AliasChoices('voltage','Voltage'))

    @model_validator(mode='after')
    def same_lengths(self):
        if len(self.capacitance) != len(self.voltage):
            raise ValueError(f'Gain Layer Uniformity and voltage arrays should have the same lengths. Length of Current, Length of Voltage = ({len(self.current)}, {len(self.voltage)})')
        return self
    
    @model_validator(mode='after')
    def max_length(self):
        if len(self.capacitance) > 256 or len(self.voltage) > 256:
            raise ValueError(f'Length of Gain Layer Uniformity, Length of Voltage = ({len(self.gain_layer_uniformity)}, {len(self.voltage)}) one of these is longer than 256, the max number of arrays.')
        return self