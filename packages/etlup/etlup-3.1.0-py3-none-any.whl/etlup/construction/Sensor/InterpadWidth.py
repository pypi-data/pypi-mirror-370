from pydantic import ConfigDict, Field
from typing import Literal, Optional
import matplotlib.pyplot as plt

from ...example_formatter import NoIndent
from ..plot_utils import convert_fig_to_html_img
from .. import base_model as bm
from .data_models import InterpadWidthData
from ... import jinja_env

class InterpadWidthV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "component": "FBK_LF1_ROL_054",
                "type": "Sensor Interpad Width",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "UT",
                "user_created": "fsiviero",
                "version": "0.0",
                "data": {
                    "side": "B", 
                    "geometry": "1x1 LGAD",
                    "irradiation_level": 1E15,
                    "interpad_width": 1.1,
                }
            }
        ],
        'table': 'test',
        'component_types': ['Prototype LGAD'],
        'module_types': [],
        'description': 'Tests for QA-QC test structures'
    })

    type: Literal['Sensor Interpad Width']
    version: Literal["0.0"]
    component: str
    data: InterpadWidthData.InterpadWidthDataV0

    @classmethod
    def html_display(cls, row_data: dict) -> str:
        display_data = row_data['data']
        template = jinja_env.get_template('sensors_plot.html')
        return template.render(
            plot = None,
            display_data = display_data
        )