from pydantic import ConfigDict
from typing import Literal
import matplotlib.pyplot as plt

from ...example_formatter import NoIndent
from ..plot_utils import convert_fig_to_html_img
from .. import base_model as bm
from .data_models import fake_data_module

class FakeTestModuleV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "module": "PBU0001",
                "component": "TYL4U001",
                "component_pos": 2,
                "type": "Fake ETL Test 6",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "BU",
                "user_created": "hswanson",
                "version": "0.0",
                "data": {
                    "crazy_name": "yabba dabba doo",
                    "crazy_array": NoIndent([1,23,4,21,234,5,2,22,3,2,2,3442], max_length=4), 
                    "another_crazy_array": NoIndent([1,23,4,21,234,5,2,22,3,2,2,3442], max_length=4),
                }
            }
        ],
        'table': 'test',
        'component_types': ['Fake ETROC', 'Fake LGAD', 'Fake Subassembly'],
        'module_types': ['Fake Production'],
        'description': 'A phony tests for testing the database uploads'
    })

    type: Literal['Fake ETL Test 6', 'Fake ETL Test 7', 'Fake ETL Test 8', 'Fake ETL Test 9', 'Fake ETL Test 10']
    version: Literal["0.0"]
    module: str
    component: str
    component_pos: int
    data: fake_data_module.FakeDataModuleV0

    #easier to probably get it in this class but cannot if we are doing cacheing buisness!
    @staticmethod
    def plot(crazy_name, crazy_array, another_crazy_array):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(crazy_array, another_crazy_array, label='Crazy Curve', marker='o')
        ax.set_xlabel('Counting')
        ax.set_ylabel('A random array')
        ax.set_title(f'Fake Test - crazy_name: {crazy_name}')
        ax.legend()
        ax.grid(True)
        return fig

    @classmethod
    def html_display(cls, row_data: dict):
        display_data = row_data["data"]
        fig = cls.plot(
            display_data['crazy_name'],
            display_data['crazy_array'],
            display_data['another_crazy_array'],
        )
        return convert_fig_to_html_img(fig)