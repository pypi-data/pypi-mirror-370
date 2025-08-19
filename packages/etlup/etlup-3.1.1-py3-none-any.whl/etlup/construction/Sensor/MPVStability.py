from pydantic import ConfigDict, Field
from typing import Literal, Optional
import matplotlib.pyplot as plt

from ...example_formatter import NoIndent
from ..plot_utils import convert_fig_to_html_img
from .. import base_model as bm
from .data_models import MPVStabilityData
from ... import jinja_env

class MPVStabilityV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "component": "FBK_LF1_ROL_054",
                "type": "Sensor MPV Stability",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "UT",
                "user_created": "fsiviero",
                "version": "0.0",
                "data": {
                    "side": "B", 
                    "geometry": "1x1 LGAD",
                    "mpv": [1,2,3,4,5],
                    "time": [1,2,3,4,5],
                    "mpv_stability": 0.2
                }
            }
        ],
        'table': 'test',
        'component_types': ['Prototype LGAD'],
        'module_types': [],
        'description': 'Tests for QA-QC test structures'
    })

    type: Literal['Sensor MPV Stability']
    version: Literal["0.0"]
    component: str
    data: MPVStabilityData.MPVStabilityDataV0

    @classmethod
    def html_display(cls, row_data: dict) -> str:
        display_data = row_data['data']
        fig, ax = plt.subplots(figsize=(10, 6))
        if display_data["time"] is not None and display_data["mpv"] is not None:
            ax.plot(display_data["time"], display_data["mpv"], marker='o', color='black')
            ax.set_xlabel('Time')
            ax.set_ylabel('MPV')
            ax.set_title(f'MPV Stability')
            ax.grid(True)

        template = jinja_env.get_template('sensors_plot.html')
        display_data.pop("time")
        display_data.pop("mpv")
        return template.render(
            plot = convert_fig_to_html_img(fig),
            display_data = display_data
        )