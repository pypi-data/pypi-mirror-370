# SPDX-FileCopyrightText: 2024-present Hayden Swanson <hayden_swanson22@yahoo.com>
#
# SPDX-License-Identifier: MIT
from jinja2 import Environment, PackageLoader, select_autoescape

from matplotlib import use as pltuse
pltuse("agg")

jinja_env = Environment(
    loader=PackageLoader(__name__),
    autoescape=select_autoescape()
)

from .upload import Session, get_model, now_utc, localize_datetime

try:
    # this is for the package
    import etlup.construction.Tamalero as tamalero
    import etlup.construction.Sensor as sensor
    import etlup.construction.Gantry as gantry

    __all__ = [
        'Session', 
        'get_model', 
        'jinja_env', 
        'now_utc', 
        'localize_datetime',
        'tamalero',
        'sensor',
        'gantry'
    ]
except ModuleNotFoundError as e:
    # the web app doesnt need any of the above stuff!
    pass


