import importlib
import pkgutil
import sys
from . import generated

__all__ = []

# Iterate over all modules in the generated package
for finder, name, ispkg in pkgutil.iter_modules(generated.__path__):
    # Import the module from generated
    module = importlib.import_module(f"{generated.__name__}.{name}")
    
    # Expose it as if it were a direct submodule of rdfc_proto
    sys.modules[f"{__name__}.{name}"] = module
    globals()[name] = module
    __all__.append(name)
    
sys.path.append("./generated")
