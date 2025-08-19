from pydantic import ConfigDict, model_validator
from typing import Optional, Union
from .. import base_model

class PrototypeEtroc(base_model.ComponentBase):
    model_config = ConfigDict(json_schema_extra={
        'component_type': 'Prototype ETROC',
    })

    wafer: Optional[int] = None
    row: Optional[int] = None
    column: Optional[int] = None
    efuse: Optional[str] = None
    version: Optional[str] = None
    batch: Optional[Union[int, str]] = None

    @model_validator(mode="after")
    def enforce_extra_field(self):          
        return self