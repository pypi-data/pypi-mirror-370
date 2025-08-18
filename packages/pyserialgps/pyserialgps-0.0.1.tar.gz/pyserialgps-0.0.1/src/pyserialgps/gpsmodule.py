#!/usr/bin/venv python
# Copyright 2025 - 2025, Antonio Vázquez Blanco and the pyserialgps contributors
# SPDX-License-Identifier: GPL-3.0-only

import serial
import pynmea2
from serial.tools.list_ports_common import ListPortInfo


class GpsModule():
    def __init__(self, port: str | ListPortInfo, baudrate=9600):
        if type(port) == ListPortInfo:
            port = port.device
        self._serial = serial.Serial()
        self._serial.port = port
        self._serial.baudrate = baudrate

    @property
    def port(self):
        return self._serial.port

    @property
    def baudrate(self):
        return self._serial.baudrate

    @property
    def is_open(self):
        return self._serial.is_open

    def open(self):
        if not self.is_open:
            self._serial.open()

    def close(self):
        self._serial.close()

    def __enter__(self):
        return self._serial.__enter__()

    def __exit__(self, *args, **kwargs):
        return self._serial.__exit__()

    def read(self):
        line = self._serial.readline()
        string = line.decode('ascii', errors='replace').strip()
        msg = pynmea2.parse(string)
        return msg

    def __repr__(self):
        return f"GpsModule(port={self.port}, baudrate={self.baudrate})"
