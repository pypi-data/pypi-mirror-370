
import importlib
from pathlib import Path


def auto_import_modules_from_folder(package: str, folder: str):
    for file in Path(folder).glob("*.py"):
        if file.name.startswith("_"):
            continue
        module_name = f"{package}.{file.stem}"
        importlib.import_module(module_name)


