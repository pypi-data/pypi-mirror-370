from pydantic import ConfigDict, Field
from typing import Literal, Optional
import matplotlib.pyplot as plt

from ...example_formatter import NoIndent
from ..plot_utils import convert_fig_to_html_img
from .. import base_model as bm
from .data_models import GainLayerUniformityData
from ... import jinja_env

class GainLayerUniformityV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "component": "FBK_LF1_ROL_054",
                "type": "Sensor Gain Layer Uniformity",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "Universita e INFN Torino",
                "user_created": "fsiviero",
                "version": "0.0",
                "data": {
                    "gain_layer_uniformity": "A",
                    "capacitance": [[1],[2],[3],[4],[5]],
                    "voltage": [[1],[2],[3],[4],[5]]
                }
            }
        ],
        'table': 'test',
        'component_types': ['Prototype LGAD'],
        'module_types': [],
        'description': 'LGAD gain layer uniformity test'
    })

    type: Literal['Sensor Gain Layer Uniformity']
    version: Literal["0.0"]
    component: str
    data: GainLayerUniformityData.GainLayerUniformityDataV0

    @classmethod
    def html_display(cls, row_data: dict) -> str:
        display_data = row_data['data']
        fig, ax = plt.subplots(figsize=(10, 6))
        if display_data["capacitance"] is not None and display_data["voltage"] is not None:
            for c, v in zip(display_data["capacitance"], display_data["voltage"]):
                ax.plot(c, v)
            ax.set_xlabel('Capacitance (pF)')
            ax.set_ylabel('Voltage')
            ax.set_title(f'Capacitance vs Voltage')
            ax.grid(True)

        template = jinja_env.get_template('sensors_plot.html')
        display_data.pop("capacitance")
        display_data.pop("voltage")
        return template.render(
            plot = convert_fig_to_html_img(fig),
            display_data = display_data
        )