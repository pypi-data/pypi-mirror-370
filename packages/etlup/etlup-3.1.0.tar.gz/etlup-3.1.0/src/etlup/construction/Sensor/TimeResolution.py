from pydantic import ConfigDict, Field
from typing import Literal, Optional
import matplotlib.pyplot as plt

from ...example_formatter import NoIndent
from ..plot_utils import convert_fig_to_html_img
from .. import base_model as bm
from .data_models import TimeResolutionData
from ... import jinja_env

class TimeResolutionV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "component": "FBK_LF1_ROL_054",
                "type": "Sensor Time Resolution",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "UT",
                "user_created": "fsiviero",
                "version": "0.0",
                "data": {
                    "irradiation_level": 1E15,
                    "side": "B", 
                    "geometry": "1x2 PIN",
                    "measuring_temperature": -20,
                    "time_resolution": [1,2,3,4,5],
                    "voltage": [1,2,3,4,5],
                }
            }
        ],
        'table': 'test',
        'component_types': ['Prototype LGAD'],
        'module_types': [],
        'description': 'Tests for QA-QC test structures'
    })

    type: Literal['Sensor Time Resolution']
    version: Literal["0.0"]
    component: str
    data: TimeResolutionData.TimeResolutionDataV0

    @classmethod
    def html_display(cls, row_data: dict) -> str:
        display_data = row_data['data']
        fig, ax = plt.subplots(figsize=(10, 6))
        if display_data["voltage"] is not None and display_data["time_resolution"] is not None:
            ax.plot(display_data["voltage"], display_data["time_resolution"], marker='o', color='red')
            ax.set_xlabel('Voltage')
            ax.set_ylabel('Time Resolution')
            ax.set_title(f'Voltage vs Time Resolution')
            ax.grid(True)

        template = jinja_env.get_template('sensors_plot.html')
        display_data.pop("voltage")
        display_data.pop("time_resolution")
        return template.render(
            plot = convert_fig_to_html_img(fig),
            display_data = display_data
        )