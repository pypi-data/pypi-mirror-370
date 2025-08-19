from pydantic import ConfigDict, Field
from typing import Literal, Optional
import matplotlib.pyplot as plt

from ...example_formatter import NoIndent
from ..plot_utils import convert_fig_to_html_img
from .. import base_model as bm
from .data_models import SensorIVData
from ... import jinja_env

class SensorIVV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "component": "FBK_LF1_ROL_054",
                "type": "Sensor IV - ETL Site",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "UT",
                "user_created": "fsiviero",
                "version": "0.0",
                "data": {
                    "leakage_current_uA": 158.176,
                    "breakdown_voltage_V": 282.0,
                    "category": "BAD", 
                    "gain_category": "C",
                    "current": NoIndent([1.7981099942332435e-9, 2.1325199384136795e-9,2.3892399170222234e-9,2.6674600306364482e-9,2.9917699428949618e-9,3.3739500082674567e-9,3.8820999748168106e-9,4.47047021623348e-9,5.163700134147575e-9,5.982729867071157e-9,6.888820180961375e-9,7.861340023396224e-9,8.972140363994185e-9,9.177109738800482e-9,1.1357499829500739e-8,1.3345699656497345e-8,1.591829956737456e-8,1.9567799824926624e-8,2.4187400526898273e-8,2.9501000753384687e-8,4.2371500086346714e-8,5.5717400755384006e-6,0.000025144199753412977,0.000034218599466839805,0.000040536098822485656,0.00004414160139276646,0.000045468401367543265,0.00005196220081415959,0.00006523320189444348,0.00007574760093120858,0.00008891220204532146,0.00011379199713701382,0.00013335900439415127,0.00015114799316506833,0.0001657230022829026,0.00018318099319003522,0.00020124799630139023,0.00021330300660338253,0.00022421199537348002,0.00023484700068365782,0.00024567899527028203,0.00025691199698485434,0.0002710630069486797,0.00028676798683591187,0.0003011419903486967,0.00031354298698715866,0.0003255319898016751,0.00033718798658810556,0.00034998898627236485,0.00037184200482442975,0.0003914310073014349,0.0004061759973410517,0.00042100698919966817,0.0004358369915280491,0.0004506719997152686,0.00046582298818975687,0.0004808040102943778,0.0004961600061506033,0.0005116279935464263,0.0005280390032567084,0.000550133001524955,0.000574567005969584], max_length=40),
                    "voltage": NoIndent([0.0,2.0,4.0,6.0,8.0,10.0,12.0,14.0,16.0,18.0,20.0,22.0,23.0,25.0,26.0,28.0,30.0,32.0,34.0,36.0,38.0,40.0,41.0,43.0,45.0,47.0,49.0,50.0,55.0,60.0,65.0,70.0,75.0,80.0,85.0,90.0,95.0,100.0,105.0,110.0,115.0,120.0,125.0,130.0,135.0,140.0,145.0,150.0,155.0,160.0,165.0,170.0,175.0,180.0,185.0,190.0,195.0,200.0,205.0,210.0,215.0,220.0,225.0,230.0,235.0,240.0,245.0,250.0,255.0,260.0,265.0,270.0,275.0,280.0], max_length=40),
                }
            }
        ],
        'table': 'test',
        'component_types': ['Prototype LGAD'],
        'module_types': [],
        'description': 'IV curves and other QC info of the sensors recieved from a vendor and tested by ETL sensor experts'
    })

    type: Literal['Sensor IV - ETL Site', 'Sensor IV - Vendor']
    version: Literal["0.0"]
    component: str
    data: SensorIVData.SensorIVDataV0

    @classmethod
    def html_display(cls, row_data: dict) -> str:
        display_data = row_data['data']
        fig, ax = plt.subplots(figsize=(10, 6))
        if display_data["voltage"] is not None and display_data["current"] is not None:
            ax.plot(display_data["voltage"], display_data["current"], label='IV Curve', marker='o')
            if display_data["breakdown_voltage_V"] is not None:
                ax.axvline(x=display_data["breakdown_voltage_V"], color='green', linestyle='--', label=f'Breakdown Voltage: {display_data["breakdown_voltage_V"]} V')
            ax.set_xlabel('Voltage (V)')
            ax.set_ylabel('Current (A)')
            if display_data["category"] is not None:
                ax.set_title(f'IV Curve - Category: {display_data["category"]}')
            else: 
                ax.set_title(f'IV Curve')
            ax.legend()
            ax.grid(True)
            ax.set_yscale('log')

        template = jinja_env.get_template('sensors_plot.html')
        display_data.pop("voltage")
        display_data.pop("current")
        return template.render(
            plot = convert_fig_to_html_img(fig),
            display_data = display_data
        )