import time
import datetime
import logging
import threading

from pathlib import Path
from dataclasses import dataclass

import wmi

from garmin_client import Garmin19xHvsClient
from transponder_client import TransponderClient

GARMIN_19XHVS_SAMPLING_RATE = 1/20

GARMIN_19XHVS_DEVICE_NAME = ""
TRANSPONDER_DEVICE_NAME = ""


def scan_usb_devices():
    """Todo test"""
    usb_devices = {}
    for d in wmi.WMI().Win32_PhysicalMedia():
        _name = d.name
        if _name:
            usb_devices[_name] = d.path
    return usb_devices


@dataclass
class PingData:
    timestamp: str
    latitude: str
    longitude: str
    depth: str


class Controller:

    def __init__(self):
        ### user input
        self.output_directory_path: str = None
        self.transponder_depth: float = None
        self.ping_interval: int = None
        self.ship_name: str = None
        self.number_of_pings: int = None
        self.start_delay_seconds: int = None
        ###

        self.garmin_19x_hvs_client: Garmin19xHvsClient = None
        self.garmin_19x_hvs_thread: threading.Thread = None
        self.is_pinging = False # FIXME CHANGE NAME

        self.transponder_client: TransponderClient = None

        self.ping_thread: threading.Thread = None

        self.output_filename: str = None
        self.ping_data: PingData = None

    def init_ping_file(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

        Path(self.output_directory_path).mkdir(parents=True, exist_ok=True)
        self.output_filename = Path(self.output_directory_path).joinpath(f"{timestamp}.ping")

        with open(self.output_filename, "w") as f:
            f.write(f"# ship_ame: {self.ship_name}\n")
            f.write(f"# ping_rate: {self.ping_interval}\n")
            f.write(f"# number_of_pings: {self.number_of_pings}\n")
            f.write(f"# start_delay_seconds: {self.start_delay_seconds}\n")
            pass

    def write_data_to_ping_file(self):
        with open(self.output_filename, "a") as f:
            f.write(f"{self.ping_data.timestamp},{self.ping_data.latitude},"
                    f"{self.ping_data.longitude},{self.ping_data.depth}\n")

    def connect_garmin_19x_hvs(self):
        _usb_devices = scan_usb_devices()
        if GARMIN_19XHVS_DEVICE_NAME in _usb_devices:
            # FIXME this won't work. usb_devices is probably a tuple
            #    Maybe we need a list of devices.
            #    Maybe not.
            logging.log("Garming 19x hvs found in USB devices")

            self.garmin_19x_hvs_client = Garmin19xHvsClient(
                port=_usb_devices[GARMIN_19XHVS_DEVICE_NAME],
                sampling_interval=GARMIN_19XHVS_SAMPLING_RATE
            )
        else:
            logging.error("Garming 19x Hvs not found in USB devices")

    def connect_transponder(self):
        _usb_devices = scan_usb_devices()
        if TRANSPONDER_DEVICE_NAME in _usb_devices:
            logging.log("Transponder found in USB devices")
            self.transponder_client = TransponderClient(
                port=_usb_devices[TRANSPONDER_DEVICE_NAME],
            )
        else:
            logging.error("Transponder not found in USB devices")

    def start_garmin_19x_hvs(self):
        self.garmin_19x_hvs_thread = threading.Thread("garmin_thread", self.garmin_19x_hvs_client.run, daemon=True)

    def start_transponder(self):
        #FIMXE


    def run(self):
        self.connect_garmin_19x_hvs()
        self.connect_transponder()

        if self.garmin_19x_hvs_client.serial.is_open and self.transponder_client.serial.is_open:
            self.start_garmin_19x_hvs()
            # WAIT FOR START DELAY
            self.ping_thread = threading.Thread("ping_thread", self._run, daemon=True)


    def _run(self):










