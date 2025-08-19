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
    from types import SimpleNamespace
    import etlup.construction.Tamalero as _tamalero
    import etlup.construction.Sensor as _sensor
    import etlup.construction.Gantry as _gantry

    tests = SimpleNamespace()
    tests.tamalero = _tamalero
    tests.sensor = _sensor

    assembly = SimpleNamespace()
    assembly.gantry = _gantry
    __all__ = [
        'Session', 
        'get_model', 
        'jinja_env', 
        'tests', 
        'assembly', 
        'now_utc', 
        'localize_datetime'
    ]
except ModuleNotFoundError as e:
    # the web app doesnt need any of the above stuff!
    pass


