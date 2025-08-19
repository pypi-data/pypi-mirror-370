from pydantic import BaseModel
from typing import Literal, Union, List, Optional

class InterpadResistanceDataV0(BaseModel):
    interpad_resistance_GOhm: float