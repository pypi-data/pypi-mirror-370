from pydantic import TypeAdapter
from typing import Any
from .base_model import ComponentBase
from .ETROCs.prototype_etroc import PrototypeEtroc
# Special Component Types with Extra Validation
component_type_adapters = {
    'ETROC2': PrototypeEtroc
}

#alternatively I could have prod_comp_type_adapters and use ID so if name changes its ok