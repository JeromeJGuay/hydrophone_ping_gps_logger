import time
import logging
import threading

from hydrophone_ping_gps_logger.common import BaseClient, NmeaData


class ShipNmeaClient(BaseClient):
    encoding = 'utf-8'
    baud_rate = 9600
    buffer_size = 1024
    timeout = 0.5


class ShipNmeaController:

    def __init__(self):
        self.client: ShipNmeaClient = None
        self.run_thread: threading.Thread = None

        self.is_running = False

        self.nmea_string: str = ""
        self.nmea_data = NmeaData("", "", "")

    def start(self, port: str, sampling_interval: int):
        self.client = ShipNmeaClient(port=port)

        if self.client.connect() == 1:  # client started.
            self.is_running = True
            self.run_thread = threading.Thread(
                target=self.run, name="ShipNmea", args=(sampling_interval,), daemon=True
            )
            self.run_thread.start()

    def stop(self):
        self.is_running = False
        logging.log(f"Ship nmea sampling stopped")
        if self.run_thread:
            self.run_thread.join()  # Wait for the thread to exit
        self.client.disconnect()

    def run(self, sampling_interval: int):
        """
        To be run as a separate thread from the main thread.
        """
        while self.is_running:
            self.nmea_string = self.client.read()

            #if self.nmea_string = "" FIXME disconnected ?
            # maybe raise error that can be catch in the main thread.

            if "$GPRMC" in self.nmea_string:
                self._unpack_gprmc()

            time.sleep(sampling_interval)

    def _unpack_gprmc(self):
        _split_string = self.nmea_string.split(",")
        self.nmea_data.date = _split_string[9]
        self.nmea_data.time = _split_string[1]
        self.nmea_data.latitude = _split_string[3] + _split_string[4]
        self.nmea_data.longitude = _split_string[5] + _split_string[6]