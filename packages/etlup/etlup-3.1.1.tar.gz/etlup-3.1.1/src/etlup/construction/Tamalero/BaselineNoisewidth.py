from pydantic import ConfigDict
from typing import Literal
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
from ...example_formatter import NoIndent
from ..plot_utils import convert_fig_to_html_img
from ..  import base_model as bm
from .data_models import ModulePixelData
from matplotlib.patches import Polygon
from collections import namedtuple

class BaselineNoisewidthV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "module": "PBU0001",
                "version": "0.0",
                "type": "baseline",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "BU",
                "user_created": "hayden",
                "data": {
                    '3':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60),
                    '1':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60),
                    '2':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60),
                    '0':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60)
                }
            }, 
            {
                "module": "PBU0001",
                "version": "0.0",
                "type": "noisewidth",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "BU",
                "user_created": "hayden",
                "data": {
                    '3':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60),
                    '1':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60),
                    '2':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60),
                    '0':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60)
                }
            },    
        ],
        'table': 'test',
        'component_types': [],
        'module_types': ['Production', 'PreProduction', 'Digital', 'Prototype', 'Fake Production'],
        'description': 'Baseline / Noisewidth for a module. Each position follows the standard of this module pcb version in this lablog, it should never change again: https://bu.nebraskadetectorlab.com/submission/4879'
    })
    type: Literal['baseline', 'noisewidth']
    version: Literal["0.0"]
    module: str
    data: ModulePixelData.ModulePixelDataV0

    @staticmethod
    def plot(pixel_data, test_type = "baseline"):
        """Plot all 4 16x16 arrays (3, 2, 1, 0) in a 2x2 subplot layout"""
        fig, axs = plt.subplots(2, 2, figsize=(20, 16), gridspec_kw={'wspace': 0.2, 'hspace': 0.2})

        vmin = 0 if test_type == "noisewidth" else min([np.min(matrix) for matrix in pixel_data.values() if matrix])
        vmax = 16 if test_type == "noisewidth" else max([np.max(matrix) for matrix in pixel_data.values() if matrix])

        pos_matrices = ModulePixelData.ModulePixelDataV0.model_validate(pixel_data)
        Position = namedtuple("Position", ["pos", "matrix", "invert_x", "invert_y", "ax"])
        positions = [
            Position(pos='3', matrix=pos_matrices.pos_3, invert_x=True,  invert_y=True,  ax=axs[0, 0]),
            Position(pos='1', matrix=pos_matrices.pos_1, invert_x=True,  invert_y=True,  ax=axs[0, 1]),
            Position(pos='2', matrix=pos_matrices.pos_2, invert_x=False, invert_y=False, ax=axs[1, 0]),
            Position(pos='0', matrix=pos_matrices.pos_0, invert_x=False, invert_y=False, ax=axs[1, 1]),
        ]
        images = []
        for pos, matrix, invert_x, invert_y, ax in positions:
            if matrix is not None:
                matrix = np.array(matrix)
                im = ax.matshow(matrix, vmin=vmin, vmax=vmax)
                images.append(im)
                for row in range(16):
                    for col in range(16):
                        #       x,   y
                        ax.text(col, row, int(matrix[row,col]), ha="center", va="center", color="w", fontsize=10)
                
                ax.set_xlabel('Column')
                ax.set_ylabel('Row')
                if invert_x:
                    ax.invert_xaxis()
                if invert_y:
                    ax.invert_yaxis()

                ax.minorticks_off()
                ax.xaxis.set_ticks_position('bottom')
                ax.xaxis.set_label_position('bottom')
                ax.text(0.0, 1.01, pos, 
                        ha="left", 
                        va="bottom", 
                        transform=ax.transAxes, 
                        fontsize=18, 
                        fontweight = "bold")
                ax.text(0.1, 1.01, 
                        fr"$<\mu>$ = {np.round(np.mean(matrix), 2)}, $\sigma$ = {np.round(np.std(matrix), 2)} ", 
                        ha="left", 
                        va="bottom", 
                        transform=ax.transAxes, 
                        fontsize=18)

            else:
                # Handle the case where matrix is None
                ax.set_title(f'{pos} (No Data)', fontsize=18, fontweight='bold')
                ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=16, color='gray')
                ax.set_xlim(0, 15)
                ax.set_ylim(0, 15)
                ax.set_xticks([])
                ax.set_yticks([])
        
        cbar = fig.colorbar(images[0], ax=axs) # first position
        cbar.set_label(test_type.capitalize(), fontsize = 34)

        fig.text(0.08, 0.92, "CMS", fontsize=42, ha="left", va="bottom", fontweight='bold')
        fig.text(0.155, 0.924, "ETL Preliminary", fontsize=34, ha="left", va="bottom", style='italic')
        
        # Add black triangle to top right corner as overlay (after layout is finalized)
        offset = 0.1
        size = 0.05
        # Top-right corner, rotated 90 degrees (counter-clockwise)
        triangle_x = [0.95  - offset, 0.95  - offset, 0.95  - offset - size]
        triangle_y = [0.95        , 0.95  - size,   0.95       ]
        
        triangle = Polygon(list(zip(triangle_x, triangle_y)), 
                          closed=True, 
                          transform=fig.transFigure, 
                          facecolor='black', 
                          edgecolor='black',
                          zorder=1000,
                          clip_on=False)
        fig.add_artist(triangle)
        fig.suptitle(f"Orientation: sensor side up, you are looking on the sensors", 
                     fontsize=18, fontweight='bold', y=0.04)
        return fig
    
    def _db_validation(self, session, models):
        """Perform database validation to check the provided module has positions in the provided data"""

        # Query the module by serial number
        # TODO: Add your validation logic here
        # Example: 
        module = session.query(models.Module).filter(models.Module.serial_number == self.module).first()
        if not module:
            raise ValueError(f"This module {self.module} not found in database")
        if not module.components:
            raise ValueError(f"This module does not have any components. Please contact an admin.")
        
        # Get the positions that have data provided
        provided_positions = []
        if self.data.pos_3 is not None:
            provided_positions.append(3)
        if self.data.pos_1 is not None:
            provided_positions.append(1)
        if self.data.pos_2 is not None:
            provided_positions.append(2)
        if self.data.pos_0 is not None:
            provided_positions.append(0)
        
        # Check if the provided positions match the component positions in the database
        db_positions = [comp.component_pos for comp in module.components]
        for position in provided_positions:
            if position not in db_positions:
                raise ValueError(f"Position {position} provided in data but no component found at this position in the database for module {self.module}")

    @classmethod
    def html_display(cls, row_data: dict):
        fig = cls.plot(row_data['data'], test_type = row_data['type'])
        return convert_fig_to_html_img(fig)
