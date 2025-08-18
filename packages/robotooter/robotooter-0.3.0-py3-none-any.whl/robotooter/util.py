import importlib
import inspect
import os
import pkgutil
from abc import ABCMeta
from pathlib import Path
from typing import Type, TypeVar, Union

import requests

T = TypeVar('T')


def load_included(package_path: str, expected_klass: Type, ending: str) -> dict[str, Type]:
    included = {}

    # Import the main package
    package = importlib.import_module(package_path)

    # Get all submodules in the package
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        try:
            # Import each submodule
            submodule = importlib.import_module(modname)

            # Look for filter classes in this submodule
            for name, obj in inspect.getmembers(submodule, inspect.isclass):
                if (issubclass(obj, expected_klass) and
                        obj is not expected_klass and
                        name.endswith(ending)):
                    included[name] = obj

        except ImportError as e:
            print(f"Failed to import {modname}: {e}")
            continue

    return included


def load_list(names: list[str], expected_type: Union[Type[T], ABCMeta]) -> dict[str, Type[T]]:
    klasses = {}
    for name in names:
        components = name.split('.')
        # Import the module containing the class
        module_path = '.'.join(components[:-1])
        class_name = components[-1]

        mod = importlib.import_module(module_path)
        klass = getattr(mod, class_name)
        if not issubclass(klass, expected_type):
            raise TypeError(f"{klass} is not a {expected_type.__name__}")
        klasses[klass.__name__] = klass
    return klasses


def download_sources(source_file_path: Path, output_directory: Path) -> None:
    if not os.path.exists(source_file_path):
        raise FileNotFoundError(f"{source_file_path} not found")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)

    with open(source_file_path, "r") as source_file:
        for line in source_file:
            url = line.strip()
            try:
                response = requests.get(url)
                output_name = url.split("/")[-1]
                with open(os.path.join(output_directory, output_name), "w") as output_file:
                    output_file.write(response.text)
            except Exception as e:
                print(f"Failed to download {url}: {e}")
