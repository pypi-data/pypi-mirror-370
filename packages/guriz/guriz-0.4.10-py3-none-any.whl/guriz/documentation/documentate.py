from .registry import register_route

def documentate(method: str, path: str):
    def decorator(func):
        meta = {
            "method": method.upper(),
            "path": path,
            "handler": func.__name__,
            "request_model": func.__annotations__.get('request'),
            "response_model": func.__annotations__.get('return'),
        }
        register_route(meta)
        return func
    return decorator

import importlib.util
from pathlib import Path

def import_controllers_from(path="controllers"):
    """
    Importa todos os arquivos Python dentro da pasta de controllers para ativar os decorators.
    """
    base_path = Path(path)
    for file in base_path.glob("*.py"):
        module_name = file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
