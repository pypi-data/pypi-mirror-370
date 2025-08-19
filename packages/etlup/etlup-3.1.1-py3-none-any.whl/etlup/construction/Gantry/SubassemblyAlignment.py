from pydantic import ConfigDict
from typing import Literal
import matplotlib.pyplot as plt
import numpy as np

from ...example_formatter import NoIndent
from .. import base_model as bm
from ..plot_utils import convert_fig_to_html_img
from .data_models import Displacement

class SubassemblyAlignmentV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "compoenent": "PS0001",
                "type": "subassembly alignment",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "BU",
                "user_created": "hayden",
                "version": "0.0",
                "data": {
                    "target": NoIndent([639.141118, 287.244992, 64.009534,-0.048954]),
                    "actual": NoIndent([639.141118, 287.244992, 64.009534,-0.048954]),
                    "delta": NoIndent([639.141118, 287.244992, 64.009534,-0.048954])
                }
            },
        ],
        'table': 'assembly',
        'component_types': ['Production Subassembly', 'PreProduction Subassembly'],
        'module_types': [],
        'description': 'An assembly measurement for the relative alignment between the centers of the LGAD and ETROC'
    })
    type: Literal['subassembly alignment']
    version: Literal["0.0"]
    component: str
    data: Displacement.DisplacementV0  

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
        #have these be the default values and if the point goes outside it just zooms out with some wiggle room
        ax.set_xlim([-200, 200])
        ax.set_ylim([-200, 200])
        ax.set_title(f'ETROC+LGAD Alignment (um)') 
        
        ax.axhline(0, color='black', linewidth=1)
        ax.axvline(0, color='black', linewidth=1)
        return fig
    
    @classmethod
    def html_display(cls, row_data: dict):
        display_data = row_data["data"]
        fig = cls.plot(display_data)
        return convert_fig_to_html_img(fig)