from typing_extensions import Literal
from pydantic import ConfigDict
import numpy as np
import matplotlib.pyplot as plt

from ...example_formatter import NoIndent
from ..plot_utils import convert_fig_to_html_img
from .. import base_model
from .data_models import Displacement

class PickAndPlaceSurveyV0(base_model.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "module": "PBU0001",
                "component": "PE0001",
                "component_pos": 1, 
                "version": "0.0",
                "type": "pick and place survey precure",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "BU",
                "user_created": "hayden",
                "data": {
                    "target": NoIndent([639.141118, 287.244992, 64.009534,-0.048954]),
                    "actual": NoIndent([639.141118, 287.244992, 64.009534,-0.048954]),
                    "delta": NoIndent([639.141118, 287.244992, 64.009534,-0.048954])
                }
            },
            {
                "module": "PBU0001",
                "component": "PE0001",
                "component_pos": 1, 
                "version": "0.0",
                "type": "pick and place survey postcure",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "BU",
                "user_created": "hayden",
                "data": {
                    "target": NoIndent([639.141118, 287.244992, 64.009534,-0.048954]),
                    "actual": NoIndent([639.141118, 287.244992, 64.009534,-0.048954]),
                    "delta": NoIndent([639.141118, 287.244992, 64.009534,-0.048954])
                }
            }
        ],
        'table': 'assembly',
        'component_types': ['Production Subassembly', 'PreProduction Subassembly', 'Ghost ETROC'],
        'module_types': ['PreProduction', 'Production', 'Digital'],
        'description': 'Gantry assembly step to measure the position of the subassemblies on the module (either before curing or after curing)'
    })
    type: Literal['pick and place survey precure', 'pick and place survey postcure']
    module: str
    component: str
    component_pos: int
    data: Displacement.DisplacementV0
    version: Literal["0.0"]
    
    @staticmethod
    def plot(delta_vector: list):
        """
        A vector like [dX (um), dY (um), dZ (um), dRot (degrees)]
        """
        assy_data = np.array(delta_vector)
        fig, ax = plt.subplots(figsize=(4, 4))
        # add your plot command here
        ax.plot(assy_data[0]*1000, assy_data[1]*1000, 'o') # 'o' specifies points
        ax.set_xlabel('dx')
        ax.set_ylabel('dy')
        ax.grid()

        ax.set_title(f'Pick and Place Alignment (um)') 
        ax.set_xlim([-20, 20])
        ax.set_ylim([-20, 20])                

        ax.axhline(0, color='black', linewidth=1)
        ax.axvline(0, color='black', linewidth=1)
        return fig
    
    @classmethod
    def html_display(cls, row_data: dict):
        display_data = row_data["data"]
        fig = cls.plot(display_data['delta'])
        return convert_fig_to_html_img(fig)