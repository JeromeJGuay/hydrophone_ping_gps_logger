import logging
import serial

from dataclasses import dataclass

@dataclass
class NmeaData:
    date: str
    time: str
    latitude: str
    longitude: str

    def __str__(self):
        return f'{self.date}, {self.time}, {self.latitude}, {self.longitude}'


class BaseClient:
    """
    The BaseClient class is used to communicate with a serial port.
    Device specific values can be overwritten when creating a child class.


    ----------------------------
    class NewClient(BaseClient):
       encoding = 'utf-8'
       baud_rate = 9600
       buffer_size = 1024
       timeout = 0.5
    ----------------------------
    """
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
