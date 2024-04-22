import time
import logging
import threading

from hydrophone_ping_gps_logger.common import BaseClient


class TransponderClient(BaseClient): # new class for logging `__class__`
    pass


class TransponderController:
    open_command: str = ""  # hexa
    close_command: str = ""  # hexa
    open_close_delay = 0.01

    def __init__(self):
        self.client: TransponderClient = None
        self.is_connected = False

    def start(self, port: str, baudrate=9600):
        self.client = TransponderClient(port=port, baudrate=baudrate)
        if self.client.connect() == 1:
            self.is_connected = True

    def stop(self):
        self.client.disconnect()
        self.is_connected = False

    def ping(self):
        self.send_open_command()
        time.sleep(self.open_close_delay) #fIXME
        self.send_close_command()

    def send_close_command(self):
        self.client.write(self.close_command)

    def send_open_command(self):
        self.client.write(self.open_command)

