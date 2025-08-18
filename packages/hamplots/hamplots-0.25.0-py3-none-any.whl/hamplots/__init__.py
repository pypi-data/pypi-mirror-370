"""
    Standard Python initialiser handling imports from modules and version number
"""
from .datasources import *
from .analysers import *
from .runner import *

if __name__ == "__main__":
    from importlib.metadata import version
    try:
        __version__ = version("ham-plots")
    except:
        __version__ = ""
    print(f"Hamplots {__version__} by Dr Alan Robinson")
    get_args_and_run()


