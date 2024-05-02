"""
Fields should look like this:
` 20240424T083551, 2024-04-24, 12:35:54+00:00, 4838.4572 N,06809.4211 W`

"""


import time
import datetime
import logging
import threading

from dataclasses import dataclass

from pathlib import Path

try:
    from hydrophone_ping_gps_logger.gps import GpsController
    from hydrophone_ping_gps_logger.transponder import TransponderController
except ImportError:
    from gps import GpsController
    from transponder import TransponderController


GARMIN_19XHVS_SAMPLING_INTERVAL = 1/20

FIELD_NAME = ["timestamp", "gsp_date", "gps_time", "gps_lat", "gps_lon", "heading"]
FIELD_PADDING = [21, 11, 15, 12, 13, 8] # review heading FIXME

@dataclass
class PingRunParameters:
    output_directory_path: str = None
    ship_name: str = None
    transponder_depth: float = None
    ping_interval: int = None
    number_of_pings: int = None
    start_delay_seconds: int = None


class PingLoggerController:

    def __init__(self):

        self.gps_controller = GpsController()
        self.transponder_controller = TransponderController()
        self.ping_run_thread: threading.Thread = None

        self.is_running = False

        self.ping_run_parameters: PingRunParameters = None

        self.ping_count = 0
        self.count_down_delay = 0

        self.ping_paused_event = threading.Event()
        self.ping_paused_event.set()

        self.output_filename: str = None
        self.bypass_gps = False

    def connect_gps(self, port, baudrate):
        self.gps_controller.connect(port=port, baudrate=baudrate)

    def disconnect_gps(self):
        self.gps_controller.disconnect()
        self.stop_ping_run()

    def connect_transponder(self):
        self.transponder_controller.connect()

    def disconnect_transponder(self):
        self.stop_ping_run()
        self.transponder_controller.disconnect()

    def start_ping_run(self, run_parameters: PingRunParameters, bypass_gps=False):

        self.bypass_gps = bypass_gps

        if self.is_running:
            logging.warning("Already running")
            return

        self.ping_run_parameters = run_parameters

        if ((self.gps_controller.is_running or self.bypass_gps)
                and self.transponder_controller.is_connected):

            self.is_running = True

            self.init_ping_file()

            time.sleep(0.1)

            self.ping_run_thread = threading.Thread(target=self._ping_run, name="ping_thread", daemon=True)
            self.ping_run_thread.start()
        else:
            logging.warning("Devices (GPS or transponder) not connected. Ping Run not started")

    def _ping_run(self):
        self.ping_count = 0

        logging.info(f"Start delay: {self.ping_run_parameters.start_delay_seconds} seconds.")

        self.count_down_delay = self.ping_run_parameters.start_delay_seconds
        while self.count_down_delay > 0:
            self.count_down_delay -= 1
            time.sleep(1)

        logging.info(f"Ping mission started. Interval: {self.ping_run_parameters.ping_interval} seconds.")
        while self.is_running:
            if not self.ping_paused_event.is_set():
                logging.info("Enter ping run wait section")
                self.ping_paused_event.wait()
                logging.info("Enter ping run wait released")

            # if self.bypass_gps:
            #     if (not self.gps_controller.is_running):
            #         self.is_running = False
            #         logging.info("Ping Run Break GPS Disconnected")
            #         break

            if self.transponder_controller.ping():
                self.write_data_to_ping_file()
                self.ping_count += 1
            else:
                self.is_running = False
                logging.info("Ping Run Break Ping Failed")
                break # FIXME Raise Error

            if 0 < self.ping_run_parameters.number_of_pings <= self.ping_count:
                self.is_running = False
                logging.info("Ping Run Break Ping Count Reach")
                break

            time.sleep(self.ping_run_parameters.ping_interval)

    def pause_ping_run(self):
        self.ping_paused_event.clear()
        logging.info("pause event clear")

    def unpause_ping_run(self):
        self.ping_paused_event.set()
        logging.info("pause event set")

    def stop_ping_run(self):
        self.unpause_ping_run()
        time.sleep(0.1)
        self.is_running = False
        self.ping_count = 0
        if self.ping_run_thread:
            self.ping_run_thread.join()


    def init_ping_file(self):
        timestamp = (
                self.gps_controller.nmea_data.date.replace("-", "")
                + self.gps_controller.nmea_data.time.split("+")[0].replace(":", "")
        )

        if timestamp == "": # if no gps use the computer time.
            timestamp = get_timestamp()

        Path(self.ping_run_parameters.output_directory_path).mkdir(parents=True, exist_ok=True)
        self.output_filename = Path(self.ping_run_parameters.output_directory_path).joinpath(
            f"{timestamp}_{self.ping_run_parameters.ship_name}.ping"
        )

        with open(self.output_filename, "w") as f:
            f.write(f"# datetime: {timestamp}\n")
            f.write(f"# ship_name: {self.ping_run_parameters.ship_name}\n")
            f.write(f"# ping_interval_second: {self.ping_run_parameters.ping_interval}\n")
            f.write(f"# number_of_pings: {int(self.ping_run_parameters.number_of_pings) or -1}\n")
            f.write(f"# start_delay_second: {self.ping_run_parameters.start_delay_seconds}\n")
            f.write(f"# transponder_depth_meter: {self.ping_run_parameters.transponder_depth}\n")
            f.write(format_data_line(FIELD_NAME) + "\n")

    def write_data_to_ping_file(self):
        with open(self.output_filename, "a") as f:
            f.write(
                format_data_line(
                    [
                        get_timestamp(),
                        self.gps_controller.nmea_data.date,
                        self.gps_controller.nmea_data.time,
                        self.gps_controller.nmea_data.latitude,
                        self.gps_controller.nmea_data.longitude,
                        self.gps_controller.nmea_data.heading,
                    ]

                )+"\n"
            )


def format_data_line(data: list) -> str:
    line = ",".join(f"{d:>{p}}" for d, p in zip(data, FIELD_PADDING))
    logging.debug(f"Data written: {line}")
    return line


def get_timestamp():
    return datetime.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
