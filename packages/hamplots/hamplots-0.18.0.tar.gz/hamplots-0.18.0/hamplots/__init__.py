"""
    Standard Python initialiser handling imports from modules and version number
"""
from .datasources import *
from .analysers import *

from importlib.metadata import version
try:
    __version__ = version("ham-plots")
except:
    __version__ = ""



if __name__ == "__main__":
    print(f"\nHamplots {__version__} by Dr Alan Robinson G1OJS\n\n")

