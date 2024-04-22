"""
BaudRates: Garmin=4800, GNSS=9600, Ship=????
"""

import time

from pathlib import Path

import flet as ft
from flet import TextField, ElevatedButton, Text, Row, Column, IconButton, Dropdown, Container
from flet_core.control_event import ControlEvent

from hydrophone_ping_gps_logger.utils import list_serial_ports
from hydrophone_ping_gps_logger.pingloggercontroller import PingLoggerController, PingRunParameters


FONT_SIZE_M = 20


def main(page: ft.Page):
    page.title = "Ping GPS Logger"
    page.window_width = 900
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT # DARK
    ### BackEnd ###

    pingloggercontroller = PingLoggerController()

    ### CONNECT TRANSPONDER ###
    def update_dropdown_transponder_port(e: ControlEvent):
        dropdown_gps_port.options = [ft.dropdown.Option(comport) for comport in list_serial_ports()]
        page.update()

    def validate_transponder_parameters(e: ControlEvent):
        if all([
            dropdown_gps_port.value,
            dropdown_gps_baudrate.value
        ]):

            button_connect_transponder.disabled = False
        else:
            button_connect_transponder.disabled = True

        page.update()

    def connect_transponder(e: ControlEvent):
        pingloggercontroller.connect_transponder(port=dropdown_gps_port.value, baudrate=dropdown_gps_baudrate.value) # FIXME

        if pingloggercontroller.gps_controller.is_connected:
            button_connect_gps.text = "Disconnect Transponder"
            button_connect_gps.bgcolor = ft.colors.RED_200

            dropdown_gps_port.disabled = True
            dropdown_gps_baudrate.disabled = True
            button_refresh_gps_port.disabled = True

            button_connect_gps.on_click = disconnect_transponder

            page.update()

    def disconnect_transponder(e: ControlEvent):
        pingloggercontroller.disconnect_transponder()

        button_connect_gps.text = "Connect Transponder"
        button_connect_gps.on_click = connect_transponder
        button_connect_gps.bgcolor = ft.colors.GREEN_200

        dropdown_gps_port.disabled = False
        dropdown_gps_baudrate.disabled = False
        button_refresh_gps_port.disabled = False

        page.update()


    dropdown_transponder_port = Dropdown(
        label="Transponder ComPort",
        width=210,
        alignment=ft.alignment.center,
        options=list(ft.dropdown.Option(comport) for comport in list_serial_ports()),
        on_change=validate_transponder_parameters,
        )

    button_refresh_transponder_port = IconButton(
        icon=ft.icons.REFRESH, on_click=update_dropdown_transponder_port
    )

    dropdown_transponder_baudrate = Dropdown(
        label="Transponder Baudrate",
        width=210,
        alignment=ft.alignment.center,
        options=list(ft.dropdown.Option(o) for o in (2400, 4800, 9600, 19200, 38400, 57600, 115200)),
        on_change=validate_transponder_parameters
    )
    button_connect_transponder = ElevatedButton(
        text="Connect Transponder", width=200,
        disabled=True, on_click=connect_transponder, bgcolor=ft.colors.LIGHT_GREEN
    )


    ### CONNECT GPS FIELD ###
    def update_dropdown_gps_port(e: ControlEvent):
        dropdown_gps_port.options = [ft.dropdown.Option(comport) for comport in list_serial_ports()]
        page.update()

    def validate_gps_parameters(e: ControlEvent):
        if all([
            dropdown_gps_port.value,
            dropdown_gps_baudrate.value
        ]):

            button_connect_gps.disabled = False
        else:
            button_connect_gps.disabled = True

        page.update()

    def connect_gps(e: ControlEvent):
        pingloggercontroller.connect_gps(port=dropdown_gps_port.value, baudrate=dropdown_gps_baudrate.value) # FIXME

        if pingloggercontroller.gps_controller.is_connected:
            button_connect_gps.text = "Disconnect GPS"
            button_connect_gps.bgcolor = ft.colors.RED_200

            dropdown_gps_port.disabled = True
            dropdown_gps_baudrate.disabled = True
            button_refresh_gps_port.disabled = True

            button_connect_gps.on_click = disconnect_gps

            page.update()

    def disconnect_gps(e: ControlEvent):
        pingloggercontroller.disconnect_gps()

        button_connect_gps.text = "Connect GPS"
        button_connect_gps.on_click = connect_gps
        button_connect_gps.bgcolor = ft.colors.GREEN_200

        dropdown_gps_port.disabled = False
        dropdown_gps_baudrate.disabled = False
        button_refresh_gps_port.disabled = False

        page.update()

    dropdown_gps_port = Dropdown(
        label="Gps ComPort",
        width=200,
        alignment=ft.alignment.center,
        options=list(ft.dropdown.Option(comport) for comport in list_serial_ports()),
        on_change=validate_gps_parameters,
        )

    button_refresh_gps_port = IconButton(
        icon=ft.icons.REFRESH, on_click=update_dropdown_gps_port
    )

    dropdown_gps_baudrate = Dropdown(
        label="Gps Baudrate",
        width=200,
        alignment=ft.alignment.center,
        options=list(ft.dropdown.Option(o) for o in (2400, 4800, 9600, 19200, 38400, 57600, 115200)),
        on_change=validate_gps_parameters
    )
    button_connect_gps = ElevatedButton(
        text="Connect GPS", width=200,
        disabled=True, on_click=connect_gps, bgcolor=ft.colors.LIGHT_GREEN
    )

    text_gps_date = TextField(value="", label="date", width=150, color=ft.colors.LIGHT_BLUE, bgcolor=ft.colors.GREY_100, disabled=True)
    text_gps_time = TextField(value="", label="time", width=150, color=ft.colors.LIGHT_BLUE, bgcolor=ft.colors.GREY_100, disabled=True)
    text_gps_lat = TextField(value="", label="lon", width=150, color=ft.colors.LIGHT_BLUE, bgcolor=ft.colors.GREY_100, disabled=True)
    text_gps_lon = TextField(value="", label="lat", width=150, color=ft.colors.LIGHT_BLUE, bgcolor=ft.colors.GREY_100, disabled=True)



    ### RUN SETTING FIELDS ###
    text_ship_name = TextField(label="Ship Name", value="", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=400)
    text_directory_path = TextField(label="Target Directory", value="", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=400, disabled=True,  color=ft.colors.LIGHT_BLUE, bgcolor=ft.colors.GREY_100)
    text_number_of_ping = TextField(label="Number Of Ping", value="0", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=250)
    text_ping_count = TextField(label="Ping Count", value="0", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=150, disabled=True,  color=ft.colors.LIGHT_BLUE, bgcolor=ft.colors.GREY_100)
    text_ping_interval = TextField(label="Ping Interval", value="1", suffix_text="second", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=250)
    text_start_delay = TextField(label="Start Delay", suffix_text=" second", value="0", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=250)
    text_countdown_delay = TextField(label="Countdown", value="", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=150, disabled=True,  color=ft.colors.LIGHT_BLUE, bgcolor=ft.colors.GREY_100)
    text_transponder_depth = TextField(label="Transponder depth", suffix_text=" meter", value="0", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=250)


    ### START/STOP RUN FIELDS ###
    icon_button_directory = IconButton(icon=ft.icons.FOLDER, icon_size=20)
    button_start = ElevatedButton(text="Start", width=200, disabled=True)
    button_stop = ElevatedButton(text="Stop", width=200, disabled=True)

    def pick_directory_reseult(e: ft.FilePickerResultEvent):
        text_directory_path.value = e.path
        text_directory_path.update()

    # adding directory picker
    directory_picker = ft.FilePicker(on_result=pick_directory_reseult)
    page.overlay.append(directory_picker)

    def validate_ping_run(e: ControlEvent=None): #rename
        if (all([text_ship_name.value,
                text_directory_path.value,
                text_ping_interval.value,
                text_number_of_ping.value,
                text_start_delay.value,
                text_transponder_depth.value])
                and pingloggercontroller.gps_controller.is_running):

            button_start.disabled = False
        else:
            button_start.disabled = True

        page.update()

    def on_start_delay_change(e: ControlEvent=None):
        text_countdown_delay.value = text_start_delay.value

        validate_ping_run(e)

    def start_ping_run(e: ControlEvent):
        pingloggercontroller.start_ping_run(
            PingRunParameters(
                output_directory_path=text_directory_path.value,
                ship_name=text_ship_name.value,
                transponder_depth=text_transponder_depth.value,
                ping_interval=float(text_ping_interval.value),
                number_of_pings=int(text_number_of_ping.value),
                start_delay_seconds=int(text_start_delay.value)
            )
        )
        if pingloggercontroller.is_running:
            button_start.disabled = True
            button_stop.disabled = False

            page.update()

    def stop_ping_run(e: ControlEvent):
        pingloggercontroller.stop_ping_run()
        button_stop.disabled = True

        validate_ping_run(e)

        page.update()

    def select_directory(e: ControlEvent):
        directory_picker.get_directory_path(dialog_title="path to ping log directory", initial_directory=Path().home())


    # link functions to UI
    text_ship_name.on_change = validate_ping_run
    text_directory_path.on_change = validate_ping_run
    text_ping_interval.on_change = validate_ping_run
    text_number_of_ping.on_change = validate_ping_run
    text_start_delay.on_change = on_start_delay_change
    text_transponder_depth.on_change = validate_ping_run

    icon_button_directory.on_click = select_directory

    button_start.on_click = start_ping_run
    button_stop.on_click = stop_ping_run

    page.add(
        Row([dropdown_transponder_port, button_refresh_transponder_port, dropdown_transponder_baudrate, button_connect_transponder],
            alignment=ft.MainAxisAlignment.CENTER),
        Row([dropdown_gps_port, button_refresh_gps_port, dropdown_gps_baudrate, button_connect_gps],
            alignment=ft.MainAxisAlignment.CENTER),
        Row([text_gps_date, text_gps_time, text_gps_lat, text_gps_lon], alignment=ft.MainAxisAlignment.CENTER),
        Row(
            controls=[
                Column(
                    [
                        text_ship_name,
                        Row([text_directory_path, icon_button_directory]),
                        text_ping_interval,
                        Row([text_number_of_ping, text_ping_count]),
                        Row([text_start_delay, text_countdown_delay]),
                        text_transponder_depth,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        Row([
            button_start, button_stop],
            alignment=ft.MainAxisAlignment.CENTER
        ),
    )


    while True:
        text_gps_date.value = str(pingloggercontroller.gps_controller.nmea_data.date)
        text_gps_time.value = str(pingloggercontroller.gps_controller.nmea_data.time)
        text_gps_lat.value = str(pingloggercontroller.gps_controller.nmea_data.latitude)
        text_gps_lon.value = str(pingloggercontroller.gps_controller.nmea_data.longitude)

        text_ping_count.value = str(pingloggercontroller.ping_count)
        text_countdown_delay.value = str(pingloggercontroller.count_down_delay)

        if not pingloggercontroller.is_running:
            button_stop.disabled = True
            validate_ping_run()

        page.update()
        time.sleep(0.1)


if __name__ == '__main__':
    ft.app(target=main)
    #ft.app(target=main, view=ft.AppView.WEB_BROWSER)