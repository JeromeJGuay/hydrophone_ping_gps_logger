import time
import serial
import logging

class Garmin19xHvsClient:
    """
    Garmin 19xHvs Maximum refresh rate is 20 Hz.
    """
    encoding = 'utf-8'
    baude_rate = 9600
    buffer_size = 1024
    timeout = 0.5  # Fixme Maybe reduce it to 0.1 ?

    def __init__(self, port: str, sampling_interval: int):
        """

        :param port:
        :param sampling_interval: In seconds
        """
        self.port = port
        self.sampling_interval = sampling_interval

        self.nmea_string: str = None

        self.serial: serial.Serial = None
        self.is_running = False

    def start_client(self):
        try:
            self.serial = serial.Serial(port=self.port, baudrate=self.baude_rate, timeout=self.timeout)
            logging.log("Garmin19xHvs Client started")
            return 1
        except serial.serialutil.SerialException:
            logging.error("Could not connect Garmin 19x Hvs client")
            return 0

    def close_client(self):
        self.serial.close()
        logging.log("Garmin19xHvs Client closed")

    def read_nmea_string(self):
        try:
            self.nmea_string = self.serial.readline(size=self.buffer_size).decode(self.encoding)
            logging.log(f"NMEA String: {self.nmea_string}")
        except serial.SerialTimeoutException:
            self.nmea_string = None
            logging.warning(f"NMEA String: None")

    def run(self):
        """
        To be run as a separate thread from the main thread.
        """
        if self.start_client() == 1: # client started.
            self.is_running = True
            while self.is_running:
                self.read_nmea_string()
                time.sleep(self.sampling_interval)
            self.close_client()

    def stop(self):
        self.is_running = False
        logging.log(f"Garmin 19x Hvs sampling stopped")
