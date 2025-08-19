from pydantic import ConfigDict, Field
from typing import Literal, Optional
import matplotlib.pyplot as plt

from ...example_formatter import NoIndent
from ..plot_utils import convert_fig_to_html_img
from .. import base_model as bm
from .data_models import CurrentUniformityData
from ... import jinja_env

class CurrentUniformityV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "component": "FBK_LF1_ROL_054",
                "type": "Sensor Current Uniformity",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "Universita e INFN Torino",
                "user_created": "fsiviero",
                "version": "0.0",
                "data": {
                    "current_uniformity": "A",
                    "current": [[1,2,3,4,5],[2,3,4,5,6],[3,4,5,6,7],[4,5,6,7,8],[5,6,7,8,9]],
                    "voltage": [[1,2,3,4,5],[2,3,4,5,6],[3,4,5,6,7],[4,5,6,7,8],[5,6,7,8,9]]
                }
            }
        ],
        'table': 'test',
        'component_types': ['Prototype LGAD'],
        'module_types': [],
        'description': 'LGAD current uniformity test'
    })

    type: Literal['Sensor Current Uniformity']
    version: Literal["0.0"]
    component: str
    data: CurrentUniformityData.CurrentUniformityDataV0

    @classmethod
    def html_display(cls, row_data: dict) -> str:
        display_data = row_data['data']
        fig, ax = plt.subplots(figsize=(10, 6))
        if display_data["current"] is not None and display_data["voltage"] is not None:
            for c, v in zip(display_data["current"], display_data["voltage"]):
                ax.plot(c, v)
            ax.set_xlabel('Current')
            ax.set_ylabel('Voltage')
            ax.set_title(f'Current vs Voltage')
            ax.grid(True)

        template = jinja_env.get_template('sensors_plot.html')
        display_data.pop("current")
        display_data.pop("voltage")
        return template.render(
            plot = convert_fig_to_html_img(fig),
            display_data = display_data
        )