#!/usr/bin/venv python
# Copyright 2025 - 2025, Antonio Vázquez Blanco and the pyserialgps contributors
# SPDX-License-Identifier: GPL-3.0-only

from typing import Generator
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo
from .gpsmodule import GpsModule


def _serial_config(dev: ListPortInfo):
    # G-Mouse VK-162
    if dev.vid == 0x1546 and dev.pid == 0x01a7:
        return (dev, 9600)
    # GlobalSat ND-100S
    if dev.vid == 0x067B and dev.pid == 0x2303:
        return (dev, 4800)
    return None


def list_modules() -> Generator[GpsModule, None, None]:
    for port in comports():
        cfg = _serial_config(port)
        if cfg is not None:
            p, b = cfg
            yield GpsModule(p, b)
