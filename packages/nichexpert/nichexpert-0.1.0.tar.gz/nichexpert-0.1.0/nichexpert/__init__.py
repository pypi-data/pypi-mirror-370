import sys
from importlib.metadata import version


from . import plot as pl
from . import preprocess as pp
from . import trainer as tr
from . import analysis as al

# has to be done at the end, after everything has been imported
sys.modules.update({f"{__name__}.{m}": globals()[m] for m in ["tr", "pp", "pl", "al"]})

__version__ = version("nichexpert")

__all__ = ["__version__",  "tr", "pp", "pl", "al"]

