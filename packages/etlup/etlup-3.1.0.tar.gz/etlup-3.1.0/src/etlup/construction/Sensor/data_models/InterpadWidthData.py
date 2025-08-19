from pydantic import BaseModel, Field, AliasChoices, model_validator
from typing import Literal, Union, List, Optional

class InterpadWidthDataV0(BaseModel):
    side:              Union[None,Literal["A", "B"]] = Field(validation_alias=AliasChoices('side','Side'))
    geometry:          Union[None,Literal["1x1 LGAD", "1x1 PIN", "1x2 PIN"]] = Field(validation_alias=AliasChoices('geometry','Geometry'))
    irradiation_level: Union[None, float] = Field(validation_alias=AliasChoices('irradiation_level','Irradiation Level'))
    interpad_width:    Union[None, float] = Field(validation_alias=AliasChoices('interpad_width','Interpad Width'))
 