import importlib
import inspect
import pkgutil
import os
from typing import Union, Annotated, get_args
from pydantic import Field, TypeAdapter

def get_classes_in_module(module):
    return inspect.getmembers(module, inspect.isclass)

def pkg_from__name__(name):
    split_package = name.split('.')
    return '.'.join(split_package[:-1]) #shaves off the module name of this file (validator) to get pkg

def import_model_modules(package_path:str, root_package:str):
    """
    package_path is the path to the package to start iterating
    root_package is the for example 'pgk.subpkg' string to do a relative import from
    """
    all_modules = []
    #package_path = os.path.dirname(__file__)
    for _, pkg_name, ispkg in pkgutil.iter_modules([package_path]):
        #do not import any modules, the first directory should be package like Gantry, Tamalero, etc...
        if not ispkg:
            continue
        for _, mod_name, is_modpkg in pkgutil.iter_modules([os.path.join(package_path, pkg_name)]):
            if is_modpkg:
                continue
            #we only want the MODULES in this directory (python modules withe the construction models of different versions)
            all_modules.append(importlib.import_module(f".{pkg_name}.{mod_name}", package=root_package))
    return all_modules

def get_all_base_models(root_base_model_name):
    from . import base_model

    all_base_models = []
    for cls_name, cls in get_classes_in_module(base_model):
        if root_base_model_name in cls_name:
            all_base_models.append(cls)
    return tuple(all_base_models)

def get_first_and_later_model_versions():
    """
    Gets all models but groups the first versions and the later versions of the models
    """
    package_path = os.path.dirname(__file__)
    root_package = pkg_from__name__(__name__)

    first_versions = [] #same base class and model version number
    later_versions = []
    for mod in import_model_modules(package_path, root_package): #loop through all modules (specific tree structure)
        for _, cls in get_classes_in_module(mod):
            if issubclass(cls, get_all_base_models('ConstructionBase')):
                version_num = float(get_args(cls.model_fields['version'].annotation)[0])
                if version_num == 0:
                    first_versions.append(cls)
                elif float(version_num) > 0:
                    later_versions.append(cls)
    return first_versions, later_versions

def get_adapters():
    #https://github.com/pydantic/pydantic/discussions/4950

    first_versions, later_versions = get_first_and_later_model_versions()
    if not first_versions:
        raise ValueError("No first version of models found")

    FirstModelsUnion = Union[tuple(first_versions)]
    ModelV0s = Annotated[FirstModelsUnion, Field(discriminator="type")]
    if not later_versions:
        return TypeAdapter(ModelV0s), TypeAdapter(list[ModelV0s])

    ModelByVersionUnion = Union[tuple([ModelV0s] + later_versions)]
    ModelByVersion = Annotated[ModelByVersionUnion, Field(discriminator="version")]

    return TypeAdapter(ModelByVersion), TypeAdapter(list[ModelByVersion])

ConstrModel, ConstrArrModel = get_adapters()

#Load and dump to json like:
# validated_cong = ConstrCongAdapter.validate_python(self._constrs)
# json_str = ConstrCongAdapter.dump_json(validated_cong, indent=4)


