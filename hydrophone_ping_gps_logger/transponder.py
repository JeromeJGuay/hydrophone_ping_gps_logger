import time
import logging
import pywinusb.hid as hid


class TransponderController:
    open_close_delay = 1

    def __init__(self):
        self.client = TransponderClient()
        self.is_connected = False

    def check_connection(self):
        if self.client.device is not None:
            if not self.client.device.is_active():
                return
        self.is_connected = False

    def connect(self):
        self.client.get_device()
        if self.client.open_device() is True:
            self.is_connected = True
            pass
        else:
            logging.info("Could not connect transponder.")
            self.is_connected = False

    def disconnect(self):
        self.client.close_device()
        self.is_connected = False

    def ping(self):
        try:
            if self.client.device.is_opened():
                if self.client.on_all():
                    time.sleep(self.open_close_delay)
                    self.client.off_all()
                    logging.debug("Transponder Pinged")
                    return True
                else:
                    logging.warning("Relay didn't close.")
                    return False
            else:
                self.is_connected = False
                logging.warning("Could not ping transponder not connected")
                return False
        except Exception as e:
            logging.error(f"error: {e}")
            logging.error("Transponder Pinged failed")
            self.disconnect()
            return False


class TransponderClient:
    usb_cfg_vendor_id = 0x16c0  # Should suit, if not check ID with a tool like USBDeview
    usb_cfg_device_id = 0x05DF  # Should suit, if not check ID with a tool like USBDeview

    def __init__(self):
        self.device: hid.HidDevice = None
        self.hid_filter: hid.HidDeviceFilter = None
        self.report: hid.core.HidReport = None
        self.last_row_status = None # Type me

    def get_device(self):
        self.hid_filter = hid.HidDeviceFilter(
            vendor_id=self.usb_cfg_vendor_id,
            product_id=self.usb_cfg_device_id
        )
        hid_device = self.hid_filter.get_devices()

        if hid_device:
            self.device = hid_device[0]
        else:
            self.device = None

    def open_device(self):
        if self.device is not None:
            if self.device.is_active():
                if not self.device.is_opened():
                    self.device.open()
                    self.get_report()
                    return True
                else:
                    logging.info("Device already opened")
                    return True
            else:
                logging.info("Device is not active")
        else:
            logging.info("No device found. Could not open device")
        return False

    def close_device(self):
        if self.device.is_active():
            if self.device.is_opened():
                self.off_all()
                self.device.close()
                return True
            else:
                logging.info("Device already closed")
        else:
            logging.info("Device is not active")
        return True

    def refresh(self):
        self.get_device()
        self.open_device()

    def get_report(self):
        if not self.device.is_active():
            self.report = None

        # FIXME this is weird. why no just take the last report ???
        for rep in self.device.find_output_reports() + self.device.find_feature_reports():
            self.report = rep

    def on_all(self):
        if self.write_row_data(buffer=[0, 0xFE, 0, 0, 0, 0, 0, 0, 1]):
            return self.read_relay_status(relay_number=3)
        else:
            logging.warning("Cannot put ON relays")
            return False

    def off_all(self):
        if self.write_row_data(buffer=[0, 0xFC, 0, 0, 0, 0, 0, 0, 1]):
            return self.read_relay_status(relay_number=3)
        else:
            logging.warning("Cannot put OFF relays")
            return False

    def on_relay(self, relay_number):
        if self.write_row_data(buffer=[0, 0xFF, relay_number, 0, 0, 0, 0, 0, 1]):
            return self.read_relay_status(relay_number)
        else:
            logging.warning("Cannot put ON relay number {}".format(relay_number))
            return False

    def off_relay(self, relay_number):
        if self.write_row_data(buffer=[0, 0xFD, relay_number, 0, 0, 0, 0, 0, 1]):
            return self.read_relay_status(relay_number)
        else:
            logging.warning("Cannot put OFF relay number {}".format(relay_number))
            return False

    def write_row_data(self, buffer):
        if self.report is not None:
            self.report.send(raw_data=buffer)
            return True
        else:
            logging.warning("Cannot write in the report. check if your device is still plugged")
            return False

    def is_relay_on(self, relay_number):
        return self.read_relay_status(relay_number) > 0

    def read_relay_status(self, relay_number):
        buffer = self.read_status_row()
        return relay_number & buffer[8]

    def read_status_row(self):
        if self.report is None:
            logging.warning("Cannot read report")
            self.last_row_status = [0, 1, 0, 0, 0, 0, 0, 0, 3]
        else:
            self.last_row_status = self.report.get()
        return self.last_row_status
