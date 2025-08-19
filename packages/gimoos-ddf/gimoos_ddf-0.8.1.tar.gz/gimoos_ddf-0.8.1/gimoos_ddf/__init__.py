#!/usr/bin/env python
# -*- coding: utf-8 -*-
from importlib.metadata import version

from .interface import _C4 as _C4
from .interface import C4 as C4
from .interface import StateChangeMode as StateChangeMode
from .interface import SharedData as SharedData
from .interface import PersistData as PersistData

from .logger import logger as logger
from .create import DriverType as DriverType

__version__ = version(__name__)

__all__ = [
    '_C4',
    'C4',
    'StateChangeMode',
    'SharedData',
    'PersistData',
    'logger',
    'DriverType',
]
