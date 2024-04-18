import logging
import serial


class TransponderClient:
    encoding = "utf-8"  # fixme
    baude_rate = 9600
    buffer_size = 1024
    timeout = 0.5  # Fixme Maybe reduce it to 0.1 ?

    open_command: str = "" # hexa
    close_command: str = "" # hexa

    def __init__(self, port: int):
        self.port = port

        self.serial: serial.Serial = None
        self.is_running = False

    def start_client(self):
        try:
            self.serial = serial.Serial(port=self.port, baudrate=self.baude_rate, timeout=self.timeout)
            logging.log("Transponder Client started")
            return 1
        except serial.serialutil.SerialException:
            logging.error("Could not connect Transponder client")
            return 0

    def close_client(self):
        self.serial.close()
        logging.log("Transponder Client closed")

    def send_close_command(self):
        self.serial.write(self.close_command.encode(self.encoding))

    def send_open_command(self):
        self.serial.write(self.open_command.encode(self.encoding))

    def ping(self):
        self.send_open_command()
        time.sleep(.01) #fIXME
        self.send_close_command()
