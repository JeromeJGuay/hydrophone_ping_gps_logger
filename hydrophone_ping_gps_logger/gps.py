"""
Only looks for RMC nmea strings.
"""
import time
import logging
import threading

import pynmea2

from hydrophone_ping_gps_logger.common import BaseClient, NmeaData


GPS_REFRESH_RATE = 0.001

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

    def start(self, port: str, baudrate: int):
        self.client = GpsClient(port=port, baudrate=baudrate)

        if self.client.connect() == 1:  # client connected started.
            self.is_connected = True
            self.is_running = True
            self.run_thread = threading.Thread(
                target=self.run, name="GPS", daemon=True
            )
            self.run_thread.start()

    def stop(self):
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
        while self.is_running:

            nmea_string = self.client.read()

            if nmea_string:
                msg = pynmea2.parse(nmea_string)

                if msg.sentence_type == "RMC":  # GARMIN & SMALL
                    self.nmea_data.date = msg.datestamp
                    self.nmea_data.time = msg.timestamp
                    self.nmea_data.latitude = msg.lat + " " + msg.lat_dir
                    self.nmea_data.longitude = msg.lon + " " + msg.lon_dir

            time.sleep(GPS_REFRESH_RATE)
