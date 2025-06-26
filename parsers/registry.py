import importlib
import pkgutil
from parsers.base_parser import BaseParser

def load_parsers():
    parsers = {}
    package = 'parsers'

    for _, modname, _ in pkgutil.iter_modules([package]):
        if modname in ("base_parser", "registry", "__init__"):
            continue

        module = importlib.import_module(f"{package}.{modname}")
        for item_name in dir(module):
            obj = getattr(module, item_name)
            if isinstance(obj, type) and issubclass(obj, BaseParser) and obj is not BaseParser:
                instance = obj()
                parsers[instance.channel.lower()] = instance

    return parsers
