from pydantic import ConfigDict, field_validator
from typing import Literal, List
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
from ...example_formatter import NoIndent
from ..plot_utils import convert_fig_to_html_img
from ..  import base_model as bm
from .data_models import PixelStatus

class ModuleETROCStatusV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "module": "PBU0001",
                "component": "PE0001",
                "component_pos": 1,
                "version": "0.0",
                "type": "module etroc status",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "BU",
                "user_created": "hayden",
                "data": {
                    'pixel_map':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60)
                }
            }   
        ],
        'table': 'test',
        'component_types': ['Production ETROC', 'PreProduction ETROC', 'ETROC'],
        'module_types': ['Production', 'PreProduction'],
        'description': 'A test that checks the status for each pixel in the 16x16 array of an ETROC on a MODULE	'
    })
    type: Literal['module etroc status']
    version: Literal["0.0"]
    module: str
    component: str
    component_pos: int
    data: PixelStatus.PixelStatusV0
 
    @staticmethod
    def plot(pixel_status_matrix):
        test_data = np.array(pixel_status_matrix)
        fig, ax = plt.subplots()
        # Define  a colormap
        cmap = colors.ListedColormap(['red', 'green'])
        bounds = [0,0.5,1]
        norm = colors.BoundaryNorm(bounds, cmap.N)

        # Plotting part
        ax.imshow(test_data, cmap=cmap, norm=norm)
        ax.set_xticks(np.arange(test_data.shape[1]))
        ax.set_yticks(np.arange(test_data.shape[0]))
        for i in range(test_data.shape[0]):
            for j in range(test_data.shape[1]):
                ax.text(j, i, int(test_data[i, j]), ha='center', va='center', color='w')
        return fig
    
    @classmethod
    def html_display(cls, row_data: dict) -> str:
        display_data = row_data['data']
        fig = cls.plot(display_data['pixel_map'])
        return convert_fig_to_html_img(fig)