from pydantic import ConfigDict
from .. import base_model as bm
from .data_models import InterpadResistanceData
from typing import Literal
from ... import jinja_env

class InterpadResistanceV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "component": "FBK_LF1_ROL_054",
                "type": "Sensor Interpad Resistance",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "Universita e INFN Torino",
                "user_created": "fsiviero",
                "version": "0.0",
                "data": {
                    "interpad_resistance_GOhm": 0.1,
                }
            }
        ],
        'table': 'test',
        'component_types': ['Prototype LGAD'],
        'module_types': [],
        'description': 'LGAD interpad resistance test'
    })

    type: Literal['Sensor Interpad Resistance']
    version: Literal["0.0"]
    component: str
    data: InterpadResistanceData.InterpadResistanceDataV0

    @classmethod
    def html_display(cls, row_data: dict) -> str:
        display_data = row_data['data']
        template = jinja_env.get_template('sensors_plot.html')
        return template.render(
            plot = None,
            display_data = display_data
        )