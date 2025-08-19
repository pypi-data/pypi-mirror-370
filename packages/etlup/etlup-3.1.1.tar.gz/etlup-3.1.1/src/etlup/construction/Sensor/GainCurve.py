from pydantic import ConfigDict, Field
from typing import Literal, Optional
import matplotlib.pyplot as plt

from ...example_formatter import NoIndent
from ..plot_utils import convert_fig_to_html_img
from .. import base_model as bm
from .data_models import GainCurveData
from ... import jinja_env

class GainCurveV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "component": "FBK_LF1_ROL_054",
                "type": "Sensor Gain Curve",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "UT",
                "user_created": "fsiviero",
                "version": "0.0",
                "data": {
                    "side": "A", 
                    "geometry": "1x2 PIN",
                    "gain": [1, 2, 3, 4, 5],
                    "voltage": [1, 2, 3, 4, 5]
                }
            }
        ],
        'table': 'test',
        'component_types': ['Prototype LGAD'],
        'module_types': [],
        'description': 'Tests for QA-QC test structures'
    })

    type: Literal['Sensor Gain Curve']
    version: Literal["0.0"]
    component: str
    data: GainCurveData.GainCurveDataV0

    @classmethod
    def html_display(cls, row_data: dict) -> str:
        display_data = row_data['data']
        fig, ax = plt.subplots(figsize=(10, 6))
        if display_data["gain"] is not None and display_data["voltage"] is not None:
            ax.plot(display_data["gain"], display_data["voltage"], marker='o', color='purple')
            ax.set_xlabel('Gain')
            ax.set_ylabel('Voltage')
            ax.set_title(f'Gain vs Voltage')
            ax.grid(True)

        template = jinja_env.get_template('sensors_plot.html')
        display_data.pop("gain")
        display_data.pop("voltage")
        return template.render(
            plot = convert_fig_to_html_img(fig),
            display_data = display_data
        )