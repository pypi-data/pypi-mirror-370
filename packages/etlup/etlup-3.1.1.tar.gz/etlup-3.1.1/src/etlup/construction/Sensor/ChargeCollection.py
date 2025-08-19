from pydantic import ConfigDict, Field
from typing import Literal, Optional
import matplotlib.pyplot as plt

from ...example_formatter import NoIndent
from ..plot_utils import convert_fig_to_html_img
from .. import base_model as bm
from .data_models import ChargeCollectionData
from ... import jinja_env  # relative to the top-level package "etlup"

class ChargeCollectionV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "component": "FBK_LF1_ROL_054",
                "type": "Sensor Charge Collection",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "UT",
                "user_created": "fsiviero",
                "version": "0.0",
                "data": {
                    "irradiation_level": 1E15,
                    "side": "B", 
                    "geometry": "1x2 PIN",
                    "measuring_temperature": -20,
                    "charge": [1,2,3,4,5],
                    "voltage": [1,2,3,4,5],
                }
            }
        ],
        'table': 'test',
        'component_types': ['Prototype LGAD'],
        'module_types': [],
        'description': 'Tests for QA-QC test structures'
    })

    type: Literal['Sensor Charge Collection']
    version: Literal["0.0"]
    component: str
    data: ChargeCollectionData.ChargeCollectionDataV0

    @classmethod
    def html_display(cls, row_data: dict) -> str:
        display_data = row_data['data']
        fig, ax = plt.subplots(figsize=(10, 6))
        if display_data["voltage"] is not None and display_data["charge"] is not None:
            ax.plot(display_data["voltage"], display_data["charge"], marker='o', color='green')
            ax.set_xlabel('Voltage')
            ax.set_ylabel('Charge')
            ax.set_title(f'Charge vs Voltage')
            ax.grid(True)

        template = jinja_env.get_template('sensors_plot.html')
        display_data.pop("voltage")
        display_data.pop("charge")
        return template.render(
            plot = convert_fig_to_html_img(fig),
            display_data = display_data
        )
