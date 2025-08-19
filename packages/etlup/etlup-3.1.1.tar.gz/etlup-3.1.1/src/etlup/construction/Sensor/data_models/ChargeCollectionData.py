from pydantic import BaseModel, Field, AliasChoices, model_validator
from typing import Literal, Union, List, Optional

class ChargeCollectionDataV0(BaseModel):
    side:              Union[None,Literal["A", "B"]] = Field(validation_alias=AliasChoices('side','Side'))
    geometry:          Union[None,Literal["1x1 LGAD", "1x1 PIN", "1x2 PIN"]] = Field(validation_alias=AliasChoices('geometry','Geometry'))
    irradiation_level: Union[None, float]      = Field(validation_alias=AliasChoices('irradiation_level','Irradiation Level'))
    measuring_temperature: Union[None, float]      = Field(validation_alias=AliasChoices('measuring_temperature','Measuring Temperature'))
    voltage:           Union[None,List[float]] = Field(validation_alias=AliasChoices('voltage','Voltage'))
    charge:   Union[None,List[float]] = Field(validation_alias=AliasChoices('charge','Charge'))

    @model_validator(mode='after')
    def same_lengths(self):
        if len(self.charge) != len(self.voltage):
            raise ValueError(f'Charge and Voltage arrays should have the same lengths. Length of Charge, Length of Voltage = ({len(self.charge)}, {len(self.voltage)})')
        return self