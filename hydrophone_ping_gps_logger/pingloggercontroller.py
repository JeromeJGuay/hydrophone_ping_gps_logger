import time
import datetime
import logging
import threading

from dataclasses import dataclass

from pathlib import Path

from hydrophone_ping_gps_logger.garmin19xhvs import Garmin19xHvsController
# from hydrophone_ping_gps_logger.ship_nmea_client import ShipNmeaController
from hydrophone_ping_gps_logger.transponder import TransponderController


GARMIN_19XHVS_SAMPLING_INTERVAL = 1/20
#SHIP_NMEA_SAMPLING_INTERVAL = 1/20


@dataclass
class PingRunParameters:
    output_directory_path: str = None
    ship_name: str = None
    transponder_depth: float = None
    ping_interval: int = None
    number_of_pings: int = None
    start_delay_seconds: int = None


class PingLoggerController:  # Fixme change name

    def __init__(self):

        self.garmin_19x_hvs_controller = Garmin19xHvsController()
        self.transponder_controller = TransponderController()
        self.ping_run_thread: threading.Thread = None

        self.is_running = False  # FIXME CHANGE NAME

        self.ping_run_parameters: PingRunParameters = None

        self.output_filename: str = None

    def connect_garmin_19x_hvs(self, port):
        self.garmin_19x_hvs_controller.start(port=port, sampling_interval=GARMIN_19XHVS_SAMPLING_INTERVAL)

    def connect_transponder(self, port):
        self.transponder_controller.start(port=port)

    def start_ping_run(self, run_parameters: PingRunParameters):
        if self.is_running:
            logging.warning("Already running")
            return

        self.ping_run_parameters = run_parameters

        if self.ping_run_parameters.number_of_pings == 0:
            self.ping_run_parameters.number_of_pings = 1e10 # basically infinite ?

        if self.garmin_19x_hvs_controller.is_connected and self.transponder_controller.is_connected:
            if self.garmin_19x_hvs_controller.is_running:

                self.is_running = True

                self.init_ping_file()

                self.ping_run_thread = threading.Thread(target=self._ping_run, name="ping_thread", daemon=True)
                self.ping_run_thread.start()
        else:
            logging.warning("Devices not connected")

    def _ping_run(self):
        _count = 0

        logging.info(f"Start delay: {self.ping_run_parameters.start_delay_seconds} seconds.")
        time.sleep(self.ping_run_parameters.start_delay_seconds)

        logging.info(f"Ping mission started. Interval: {self.ping_run_parameters.ping_interval} seconds.")
        while self.is_running:
            self.write_data_to_ping_file()
            self.transponder_controller.ping()

            _count += 1

            if _count >= self.ping_run_parameters.number_of_pings:
                self.is_running = False
                break
            time.sleep(self.ping_run_parameters.ping_interval)

    def stop_ping_run(self):
        self.is_running = False
        if self.ping_run_thread:
            self.ping_run_thread.join()

    def init_ping_file(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

        Path(self.ping_run_parameters.output_directory_path).mkdir(parents=True, exist_ok=True)
        self.output_filename = Path(self.ping_run_parameters.output_directory_path).joinpath(f"{timestamp}.ping")

        with open(self.output_filename, "w") as f:
            f.write(f"# datetime: {timestamp}\n")
            f.write(f"# ship_name: {self.ping_run_parameters.ship_name}\n")
            f.write(f"# ping_rate: {self.ping_run_parameters.ping_interval}\n")
            f.write(f"# number_of_pings: {self.ping_run_parameters.number_of_pings}\n")
            f.write(f"# start_delay_seconds: {self.ping_run_parameters.start_delay_seconds}\n")
            pass

    def write_data_to_ping_file(self):
        with open(self.output_filename, "a") as f:
            f.write(f"{self.garmin_19x_hvs_controller.nmea_data.date},"
                    f"{self.garmin_19x_hvs_controller.nmea_data.time},"
                    f"{self.garmin_19x_hvs_controller.nmea_data.latitude},"
                    f"{self.garmin_19x_hvs_controller.nmea_data.longitude},"
                    f"{self.ping_run_parameters.transponder_depth}\n")


if __name__ == "__main__":
    m = PingLoggerController()
    m.connect_garmin_19x_hvs(port="")
    m.connect_transponder(port="")

    prp = PingRunParameters("./", "Leim", 1, 1/20, 20, start_delay_seconds=10)

    m.start_ping_run(run_parameters = prp)




