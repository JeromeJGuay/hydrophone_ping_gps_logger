import logging
import serial

from dataclasses import dataclass

@dataclass
class NmeaData:
    date: str
    time: str
    latitude: str
    longitude: str


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
    baud_rate = 9600
    buffer_size = 1024
    timeout = 0.5

    def __init__(self, port: str):
        """
        :param port: Usb port address (path)
        """
        self.port = port
        self.serial: serial.Serial = None
        self.serial_input_buffer: str = None

        self.client_name = str(self.__class__).split('.')[-1][:-2]  # for logging purposes

    def connect(self):
        """

        :return: `1` if connected else `0`
        """
        try:
            self.serial = serial.Serial(port=self.port, baudrate=self.baud_rate, timeout=self.timeout)
            logging.log(f"[{self.client_name}] Client connected")
            return 1
        except serial.serialutil.SerialException:
            logging.error(f"[{self.client_name}] Could not connect")
            return 0

    def disconnect(self):
        self.serial.close()
        logging.log(f"[{self.client_name}] Client closed")

    def read(self) -> str:
        try:
            self.serial_input_buffer = self.serial.readline(size=self.buffer_size).decode(self.encoding)
            logging.log(f"[{self.client_name}] Serial input buffer: {self.serial_input_buffer}")
        except serial.SerialTimeoutException:
            self.serial_input_buffer = None
            logging.warning(f"[{self.client_name}] Serial input buffer: None")

        return self.serial_input_buffer

    def write(self, msg: str):
        try:
            self.serial.write(msg.encode(self.encoding))
            logging.log(f"[{self.client_name}] Serial write: {msg}")
        except serial.serialutil.SerialException:
            logging.warning(f"[{self.client_name}] Serial write failed")
