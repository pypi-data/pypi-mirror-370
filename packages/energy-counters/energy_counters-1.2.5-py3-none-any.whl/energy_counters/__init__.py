"""
Energy Counters Library

A Python library for reading data from various electrical energy counters
including Carlo Gavazzi, Contrel, Diris, Lovato, RedZ, and Schneider devices.

Usage:
    import energy_counters
    from energ_counters import carlo_gavazzi
    from energy_counters.carlo_gavazzi import em530
"""

__version__ = "1.2.5"
__author__ = "nobrega8"
__email__ = "afonsognobrega@gmail.com"

# Import submodules to make them available
from . import carlo_gavazzi
from . import contrel  
from . import diris
from . import lovato
from . import redz
from . import schneider
from . import common

__all__ = [
    'carlo_gavazzi',
    'contrel', 
    'diris',
    'lovato',
    'redz', 
    'schneider',
    'common'
]
