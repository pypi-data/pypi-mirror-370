from pydantic import ConfigDict, field_validator, ValidationError
from typing import Literal, Optional
from pydantic import BaseModel
from typing import Literal, Optional
from ... import jinja_env
from pathlib import Path
from io import BytesIO
import base64
from .. import base_model as bm

try:
    from application import the_config
    from webdav3.client import Client #for cloud talking webdav is old but it works for CERNbox
    CERNBOX_CLIENT_DETAILS = {
        'webdav_hostname': the_config.WEBDAV_HOSTNAME,
        'webdav_login': the_config.WEBDAV_LOGIN,
        'webdav_password': the_config.WEBDAV_PASSWORD
    }
except ModuleNotFoundError as e:
    CERNBOX_CLIENT_DETAILS = None

class ImageData(BaseModel):
    cernbox_img_path: str
    comment: str
    bias: Optional[int] = None

    @field_validator("cernbox_img_path")
    @classmethod
    def check_img_exists(cls, v):
        if CERNBOX_CLIENT_DETAILS is None:
            return v
        v_path = Path(v)
        cernbox_relative_path = v_path.relative_to("/eos/project/e/etl-construction-app-storage/")
        client = Client(CERNBOX_CLIENT_DETAILS)
        if not client.check(str(cernbox_relative_path)):
            raise ValueError(f"This file ({cernbox_relative_path}) does not exist in the cernbox. The cernbox is the one for the web app, contact an admin to upload.")
        return v

class TestByImageV0(bm.ConstructionBaseV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "component": "ET2.01-PT-NH21",
                "type": "IV Scan Image",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "FL",
                "user_created": "hswanson",
                "version": "0.0",
                "data": {
                    "cernbox_img_path": "/eos/project/e/etl-construction-app-storage/TedTestResults/IV_Curve/IV_second_PT_NH_19_20_21_22.png",
                    "comment": "this result was goods",
                    "bias": 123
                }
            }
        ],
        'table': 'test',
        'component_types': ['Prototype Hybrid'],
        'module_types': [],
        'description': 'IV curves from teds presentation: https://indico.cern.ch/event/1566730/contributions/6599657/attachments/3099619/5491873/Summary-of-bump-bonding-study-July2025.pdf'
    })

    type: Literal['IV Scan Image', "Baseline and Noisewidth Histogram Image", "Baseline and Noisewidth Image", "Time Resolution - Bias Voltage Scan Image"]
    version: Literal["0.0"]
    component: str
    data: ImageData

    @classmethod
    def html_display(cls, row_data: dict) -> str:
        if CERNBOX_CLIENT_DETAILS is None:
            raise NotImplementedError("This feature for this test is only for the web app, sorry!")
        
        display_data = row_data['data']
        if display_data["cernbox_img_path"] is not None:
            # the path should be obtained by copying the "fuse path" on cernbox
            eos_fuse_path = Path(display_data["cernbox_img_path"])
            cernbox_relative_path = str(
                eos_fuse_path.relative_to("/eos/project/e/etl-construction-app-storage/"))
            
            client = Client(CERNBOX_CLIENT_DETAILS)
            buff = BytesIO()
            client.download_from(
                remote_path = cernbox_relative_path, 
                buff = buff)
            buff.seek(0)
            encoded_img = base64.b64encode(buff.getvalue()).decode('utf-8')
            img_html = f'<img src="data:image/png;base64,{encoded_img}" alt="IV Scan Image">'
        else:
            img_html = "Resource image path not provided in test data"

        template = jinja_env.get_template('test_by_image.html')
        return template.render(
            display_data = display_data,
            img_html = img_html
        )