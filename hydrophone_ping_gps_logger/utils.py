# maybe just use the port as a argument


import logging

import serial.tools.list_ports

import pywinusb.hid as hid # If it doesnt work try `hidapi`


def find_usb_device(device_name) -> str:
    usb_devices = {} # fixme

    if device_name in usb_devices:
        logging.log(f"{device_name} found in USB devices")
        return usb_devices[device_name]

    logging.error(f"{device_name} not found in USB devices")
    return None


def list_usb_devices() -> dict[str, str]:
    devices = hid.HidDeviceFilter().get_devices()

    return {f"{d.vendor_name} {d.product_name} {d.product_id}": d.device_path for d in devices}


def list_serial_ports() -> dict[str, str]:
    """FIXME Test me ?

    :return dict of {device_name: device_path}

    """
    ports_info = serial.tools.list_ports.comports()

    return {pi.device: pi.name for pi in ports_info}
