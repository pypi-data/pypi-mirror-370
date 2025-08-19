#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from pathlib import Path

from .logger import logger
from .template import *


class DriverType(Enum):
    blind             = '窗帘'
    light             = '灯'
    thermostat        = '温控'
    tv                = '电视'
    projector         = '投影仪'
    media_player      = '媒体播放机'
    dvd               = 'DVD机'
    keypad_proxy      = '按键'
    camera            = '摄像头'
    irsensor          = '人体感应'
    watersensor       = '水位感应'
    doorsensor        = '门感应'
    receiver          = '功放'
    relay             = '继电器'
    remote_controller = '遥控器'
    power_sequencer   = '电源时序器'

    @staticmethod
    def get_values():
        return {x.value for x in DriverType.__members__.values()}


class DriverCreator:
    def __init__(self):
        self.encoding = 'utf-8'

    def get_driver_py(self):
        return TEMPLATE_PY

    def get_driver_xml(self, name: str, driver_type: DriverType):
        return TEMPLATE_XML.format(
            name=name,
            driver_type=driver_type.name.lower(),
            driver_type_upper=driver_type.name.upper(),
        )

    def write_to_file(self, path: Path, content: str, overwrite: bool = True):
        if not overwrite and path.exists(path):
            logger.warning(f'{path} 已存在, 跳过创建')
            return

        with open(path, 'w', encoding=self.encoding) as f:
            f.write(content)

    def create(self, path: str, name: str, driver_type: str):
        try:
            _driver_type = DriverType(driver_type)
        except ValueError:
            raise ValueError(f'"{driver_type}" 不是合法的驱动类型, 应为 {set({x.value for x in DriverType.__members__.values()})} 中的一个')

        _path = Path(path, name)

        # 创建目录
        if not _path.exists():
            _path.mkdir(parents=True)

        # 写入代码
        self.write_to_file(_path.joinpath('driver.py'), self.get_driver_py())
        self.write_to_file(_path.joinpath('driver.xml'), self.get_driver_xml(name, _driver_type))
