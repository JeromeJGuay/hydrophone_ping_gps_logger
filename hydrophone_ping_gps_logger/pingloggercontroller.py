import time
import datetime
import logging
import threading

from dataclasses import dataclass

from pathlib import Path

from hydrophone_ping_gps_logger.gps import GpsController, NmeaData
from hydrophone_ping_gps_logger.transponder import TransponderController


GARMIN_19XHVS_SAMPLING_INTERVAL = 1/20


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

        self.gps_controller = GpsController()
        self.transponder_controller = TransponderController()
        self.ping_run_thread: threading.Thread = None

        self.is_running = False  # FIXME CHANGE NAME

        self.ping_run_parameters: PingRunParameters = None

        self.output_filename: str = None

    def connect_gps(self, port, baudrate):
        self.gps_controller.start(port=port, baudrate=baudrate)

    def disconnect_gps(self):
        self.gps_controller.stop()
        self.gps_controller.nmea_data = NmeaData("", "", "", "")
        self.stop_ping_run()

    def connect_transponder(self, port, baudrate=9600): #FIXME bauderate ???
        self.transponder_controller.start(port=port, baudrate=baudrate)

    def disconnect_transponder(self):
        self.transponder_controller.stop()
        self.stop_ping_run()

    def start_ping_run(self, run_parameters: PingRunParameters):
        if self.is_running:
            logging.warning("Already running")
            return

        self.ping_run_parameters = run_parameters

        if self.ping_run_parameters.number_of_pings == 0:
            self.ping_run_parameters.number_of_pings = 1e10 # basically infinite ?

        if self.gps_controller.is_connected and self.transponder_controller.is_connected:
            if self.gps_controller.is_running:

                self.is_running = True

                self.init_ping_file()

                self.ping_run_thread = threading.Thread(target=self._ping_run, name="ping_thread", daemon=True)
                self.ping_run_thread.start()
        else:
            logging.warning("Devices not connected. Ping Run not started")

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
            f.write(f"{self.gps_controller.nmea_data.date},"
                    f"{self.gps_controller.nmea_data.time},"
                    f"{self.gps_controller.nmea_data.latitude},"
                    f"{self.gps_controller.nmea_data.longitude},"
                    f"{self.ping_run_parameters.transponder_depth}\n")


if __name__ == "__main__":
    # garmin 4800
    # GNSS 9600
    # Ship ??

    from utils import list_serial_ports

    d = list_serial_ports()

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    m = PingLoggerController()
    m.connect_gps(
        port="COM4",
        baudrate=4800
    ) # Garmin

    m.connect_transponder(
        port="",
        baudrate=9600
    )

    prp = PingRunParameters(
        output_directory_path="./",
        ship_name="Leim",
        transponder_depth=1,
        ping_interval=1/20,
        number_of_pings=20,
        start_delay_seconds=10
    )

    m.start_ping_run(run_parameters=prp)




