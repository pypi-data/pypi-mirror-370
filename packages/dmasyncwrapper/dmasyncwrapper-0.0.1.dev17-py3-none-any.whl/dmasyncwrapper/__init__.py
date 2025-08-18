# -*- coding: UTF-8 -*-
import dmPython

from dmasyncwrapper.connection import Connection
from dmasyncwrapper.cursor import Cursor
from dmasyncwrapper.pooling import Pool
from dmasyncwrapper.utils import close, close_all, init, with_dm

__all__ = (
    'Pool',
    'Connection',
    'Cursor',

    # Utils
    'init',
    'close',
    'close_all',
    'with_dm',
)

__version__ = '0.0.1-dev17'


def __getattr__(name):
    return getattr(dmPython, name)
