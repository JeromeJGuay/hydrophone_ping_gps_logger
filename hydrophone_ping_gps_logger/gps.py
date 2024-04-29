"""
Only looks for RMC nmea strings.
"""
import time
import serial
import logging
import threading
from dataclasses import dataclass

import pynmea2

GPS_REFRESH_RATE = 0.001


@dataclass
class NmeaData:
    date: str = ""
    time: str = ""
    latitude: str = ""
    longitude: str = ""
    heading: str = ""

    def __str__(self):
        return f'{self.date}, {self.time}, {self.latitude}, {self.longitude}'

    def clear(self):
        self.date = ""
        self.time = ""
        self.latitude = ""
        self.longitude = ""
        self.heading = ""


class GpsClient:
    encoding = 'utf-8'
    buffer_size = 1024
    timeout = 0.5

    def __init__(self, port: str, baudrate: int):
        """
        :param port: Usb port address (path)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial: serial.Serial = None
        self.serial_input_buffer: str = ""

        self.client_name = str(self.__class__).split('.')[-1][:-2]  # for logging purposes

    def connect(self):
        """

        :return: `1` if connected else `0`
        """
        try:
            self.serial = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
            self.serial.readline()  # clears input buffer
            logging.info(f"[{self.client_name}] Client connected")
            return 1
        except serial.serialutil.SerialException:
            logging.error(f"[{self.client_name}] Could not connect")
            return 0

    def disconnect(self):
        self.serial.close()
        logging.info(f"[{self.client_name}] Client closed")

    def read(self) -> str:
        try:
            self.serial_input_buffer = self.serial.readline().decode(self.encoding).strip("\n")
            logging.debug(f"[{self.client_name}] Serial input buffer: {self.serial_input_buffer}")
        except serial.SerialTimeoutException:
            self.serial_input_buffer = ""
            logging.warning(f"[{self.client_name}] (Timeout) Serial Disconnected")
            # Raise ERROR FIXME
        except UnicodeDecodeError:
            self.serial_input_buffer = ""
            logging.warning(f"[{self.client_name}] (Decode Error)")
            # Raise ERROR FIXME

        return self.serial_input_buffer

    def write(self, msg: str):
        try:
            self.serial.write(msg.encode(self.encoding))
            logging.info(f"[{self.client_name}] Serial write: {msg}")
        except serial.serialutil.SerialException:
            logging.warning(f"[{self.client_name}] Serial write failed")



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

        self.nmea_data.clear()
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
                if msg.sentence_type == "RMC":  # GARMIN & SMALL

                    self.nmea_data.date = str(msg.datestamp)
                    self.nmea_data.time = str(msg.timestamp)
                    self.nmea_data.latitude = msg.lat + " " + msg.lat_dir
                    self.nmea_data.longitude = msg.lon + " " + msg.lon_dir

                elif msg.sentence_type == "HDT":
                    self.nmea_data.heading = msg.heading

            time.sleep(GPS_REFRESH_RATE)
