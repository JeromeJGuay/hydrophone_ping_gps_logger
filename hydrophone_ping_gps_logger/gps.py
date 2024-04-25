"""
Only looks for RMC nmea strings.
"""
import time
import logging
import threading
from dataclasses import dataclass

import pynmea2

from hydrophone_ping_gps_logger.common import BaseClient

GPS_REFRESH_RATE = 0.001


@dataclass
class NmeaData:
    date: str
    time: str
    latitude: str
    longitude: str

    def __str__(self):
        return f'{self.date}, {self.time}, {self.latitude}, {self.longitude}'


class GpsClient(BaseClient): # new class for logging `__class__`
    pass


class GpsController:
    def __init__(self):
        self.client: GpsClient = None
        self.run_thread: threading.Thread = None

        self.is_connected = False
        self.is_running = False

        self.nmea_msg: pynmea2.talker.TalkerSentence = None
        self.nmea_data = NmeaData("", "", "", "")

    def connect(self, port: str, baudrate: int):
        self.client = GpsClient(port=port, baudrate=baudrate)

        if self.client.connect() == 1:  # client connected started.
            self.is_connected = True
            self.run_thread = threading.Thread(
                target=self.run, name="GPS", daemon=True
            )
            self.run_thread.start()

    def disconnect(self):
        self.is_running = False
        logging.info(f"GPS sampling stopped")
        if self.run_thread:
            self.run_thread.join()  # Wait for the thread to exit
        self.client.disconnect()
        self.is_connected = False

    def run(self):
        """
        To be run as a separate thread from the main thread.
        """
        self.is_running = True

        while self.is_running:

            nmea_string = self.client.read()

            if nmea_string:
                try:
                    msg = pynmea2.parse(nmea_string)
                except pynmea2.nmea.ParseError: # FIXME
                    logging.warning("pynmea2 Parsing Error")
                    continue
                #True heading HDT msg.heading
                if msg.sentence_type == "RMC":  # GARMIN & SMALL

                    self.nmea_data.date = str(msg.datestamp)
                    self.nmea_data.time = str(msg.timestamp)
                    self.nmea_data.latitude = msg.lat + " " + msg.lat_dir
                    self.nmea_data.longitude = msg.lon + " " + msg.lon_dir

            time.sleep(GPS_REFRESH_RATE)
