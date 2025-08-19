from typing import Any, Optional
from pydantic import BaseModel, Field, AliasChoices, ConfigDict, field_validator, model_validator, ValidationError

class ComponentBase(BaseModel, str_strip_whitespace=True):
    model_config = ConfigDict(
        extra="allow",  # overwrite this for inherited models
    )

    serial_number: str = Field(
        ...,
        validation_alias=AliasChoices("serial_number","SerialNumber", "Serial Number", "SN"), 
        min_length=3, 
        coerce_numbers_to_str=True # This allows for a better error message of serial numbers that are just numbers
    )
    vendor: str = Field(..., validation_alias=AliasChoices("vendor", "Vendor"))
    etroc_serial_number: Optional[str] = Field(None, validation_alias=AliasChoices("ETROC Serial Number", "ETROCSerialNumber", "ETROC SN"))
    lgad_serial_number:  Optional[str] = Field(None, validation_alias=AliasChoices("LGAD Serial Number", "LGADSerialNumber", "LGAD SN"))
    
    @model_validator(mode="before")
    @classmethod
    def strip_field_whitespace(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = {key.strip(): value.strip() if isinstance(value, str) else value for key, value in data.items()}
        return data

    @field_validator('*', mode='before')
    def empty_str_to_none(cls, v):
        """
        To make it more user friendly and catch unsupplied serial numbers
        """
        if v == '':
            return None
        return v

    @model_validator(mode='after')
    def check_subassembly_registration(self):
        etroc_given = self.etroc_serial_number is not None
        lgad_given = self.lgad_serial_number is not None
        if etroc_given ^ lgad_given: #XOR logic is want, returns true when just one is given!
            raise ValueError("For subassembly component registration you need both etroc and lgad serial number fields.")
        return self
    
    @field_validator('serial_number')
    @classmethod
    def valid_serial_number(cls, v: str) -> str:
        if isinstance(v, str):
            # is enumerated
            if not v[-1].isdigit():
                raise ValueError(
                    f"The serial number '{v}' is not correctly formatted, serial numbers should be enumerated. Ensure the serial number ends with a numerical sequence, such as SN1, SN2, etc")
            # is a number
            if v.isdigit():
                raise ValueError(
                    f"Serial numbers cannot consist solely of numbers. Please include descriptive letters to make them more readable, such as 'MY-SN-123' instead of just '123'.")
            # needs a letter
            if not any(s.isalpha() for s in v):
                raise ValueError(
                    f"Serial numbers must include alphabetic characters to enhance readability. Please incorporate atleast one descriptive alphabetic character (A-Z)")    
            if ',' in v:
                raise ValueError("Commas cannot be in the serial number as this is used in search.")
            if '~' in v:
                raise ValueError("~ cannot be in the serial number as this is used in search.")
        return v

    @model_validator(mode="after")
    def enforce_extra_field(self):
        extra = self.model_extra
        if not extra:
            return self
        for key, value in extra.items():
            if value is None:
                raise ValueError(f"Every field needs to have a value (failed for column {key}), if you wish to leave it blank provide a dummy value or request an admin to make a special validator for this component type.")            
            elif isinstance(value, str) and not value.strip():
                raise ValueError(f"Every field needs to have a value (failed for column {key}), if you wish to leave it blank provide a dummy value or request an admin to make a special validator for this component type.")            
        return self