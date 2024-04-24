import time
import logging
import pywinusb.hid as hid


class TransponderController:
    open_close_delay = 0.01

    def __init__(self):
        self.client = TransponderClient()
        self.is_connected = False

    def connect(self):
        self.client.get_device()
        if self.client.open_device() is True:
            self.is_connected = True
            pass
        else:
            logging.warning("Could not connect transponder.")
            self.is_connected = False

    def disconnect(self):
        self.client.close_device()
        self.is_connected = False

    def ping(self):
        if self.client.device.is_opened():
            self.client.on_relay(0) # fixme need relay number
            time.sleep(self.open_close_delay) #fIXME
            self.client.off_relay(0)  # fixme need relay number
            return True
        else:
            logging.warning("could not ping transponder not connected")
            return False




class TransponderClient: # usb client ?
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


if __name__ == "__main__":
    t = TransponderClient()
    t.get_device()
    t.open_device()

    print(" --- read_status_row: {}".format(t.read_status_row()))
    print("TURN OFF ALL: {}".format(t.off_all()))

    print("TURN ON 1: {} ".format(t.on_relay(1)))
    print("READ STATE 1: {}".format(t.read_relay_status(1)))
    time.sleep(1)
    print("TURN OFF 1: {} ".format(t.off_relay(1)))
    print("READ STATE 1: {}".format(t.read_relay_status(1)))
    time.sleep(1)

    print("TURN ON ALL: {}".format(t.on_all()))
    time.sleep(1)
    print("TURN OFF ALL: {}".format(t.off_all()))

