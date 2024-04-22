"""
BaudRates: Garmin=4800, GNSS=9600, Ship=????
"""

import time

from pathlib import Path

import flet as ft
from flet import TextField, ElevatedButton, Text, Row, Column, IconButton
from flet_core.control_event import ControlEvent

from hydrophone_ping_gps_logger.utils import list_serial_ports
from hydrophone_ping_gps_logger.pingloggercontroller import PingLoggerController, PingRunParameters


FONT_SIZE_M = 20


def main(page: ft.Page):
    page.title = "Ping GPS Logger"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT # DARK
    ### BackEnd ###

    pingloggercontroller = PingLoggerController()

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
        button_connect_gps.text = "Disconnect GPS"
        button_connect_gps.bgcolor = ft.colors.RED

        dropdown_gps_port.disabled = True
        dropdown_gps_baudrate.disabled = True
        button_refresh_gps_port.disabled = True

        button_connect_gps.on_click = disconnect_gps

        page.update()

    def disconnect_gps(e: ControlEvent):
        pingloggercontroller.disconnect_gps()

        button_connect_gps.text = "Connect GPS"
        button_connect_gps.on_click = connect_gps
        button_connect_gps.bgcolor = ft.colors.GREEN

        dropdown_gps_port.disabled = False
        dropdown_gps_baudrate.disabled = False
        button_refresh_gps_port.disabled = False

        page.update()

    dropdown_gps_port = ft.Dropdown(
        label="Gps ComPort",
        width=200,
        alignment=ft.alignment.center,
        options=list(ft.dropdown.Option(comport) for comport in list_serial_ports()),
        on_change=validate_gps_parameters,
        )

    button_refresh_gps_port = ft.IconButton(
        icon=ft.icons.REFRESH, on_click=update_dropdown_gps_port
    )

    dropdown_gps_baudrate = ft.Dropdown(
        label="Gps Baudrate",
        width=200,
        alignment=ft.alignment.center,
        options=list(ft.dropdown.Option(o) for o in (2400, 4800, 9600, 19200, 38400, 57600, 115200)),
        on_change=validate_gps_parameters
    )
    button_connect_gps = ElevatedButton(
        text="Connect GPS", width=200,
        disabled=True, on_click=connect_gps, bgcolor=ft.colors.GREEN
    )

    text_gps_values = Text(value="", width=600)

    #dropdown_gps_port.on_change = validate_gps_parameters
    #dropdown_gps_baudrate.on_change = validate_gps_parameters


    ### RUN SETTING FIELDS ###
    text_ship_name = TextField(label="Ship Name", value="", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=400)
    text_directory_path = TextField(label="Target Directory", value="", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=400)
    text_number_of_ping = TextField(label="Number Of Ping", value="0", suffix_text=" second", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=250)
    text_ping_interval = TextField(label="Ping Interval", value="0", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=250)
    text_start_delay = TextField(label="Start Delay", suffix_text=" second", value="0", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=250)
    text_transponder_depth = TextField(label="Transponder depth", suffix_text=" meter", value="0", text_size=FONT_SIZE_M, text_align=ft.TextAlign.RIGHT, width=250)


    ### START/STOP RUN FIELDS ###
    icon_button_directory = IconButton(icon=ft.icons.FOLDER, icon_size=20)
    button_start = ElevatedButton(text="Start", width=200, disabled=True)
    button_stop = ElevatedButton(text="Stop", width=200, disabled=True)


    # garmin_connection_indicator = ft.CircleAvatar(
    #     content=ft.Text(""),
    #     bgcolor=ft.colors.RED,
    #     color=ft.colors.BLACK,
    #     #disabled=True
    #     )

    def pick_directory_reseult(e: ft.FilePickerResultEvent):
        text_directory_path.value = e.path
        text_directory_path.update()

    # adding directory picker
    directory_picker = ft.FilePicker(on_result=pick_directory_reseult)
    page.overlay.append(directory_picker)

    def validate_ping_run_parameters(e: ControlEvent):
        if all([text_ship_name.value,
                text_directory_path.value,
                text_ping_interval.value,
                text_number_of_ping.value,
                text_start_delay.value,
                text_transponder_depth.value]):

            button_start.disabled = False
        else:
            button_start.disabled = True

        page.update()

    def start_ping_run(e: ControlEvent):
        # pingloggercontroller.start_ping_run(
        #     PingRunParameters(
        #         output_directory_path=text_directory_path.value,
        #         ship_name=text_ship_name.value,
        #         transponder_depth=text_transponder_depth.value,
        #         ping_interval=text_ping_interval.value,
        #         number_of_pings=text_number_of_ping.value,
        #         start_delay_seconds=text_start_delay.value
        #     )
        # )
        button_start.disabled = True
        button_stop.disabled = False

        page.update()

    def stop_ping_run(e: ControlEvent):
        #pingloggercontroller.stop_ping_run()
        button_stop.disabled = True

        validate_ping_run_parameters(e)

        page.update()

    def select_directory(e: ControlEvent):
        directory_picker.get_directory_path(dialog_title="path to ping log directory", initial_directory=Path().home())


    # link functions to UI
    text_ship_name.on_change = validate_ping_run_parameters
    text_directory_path.on_change = validate_ping_run_parameters
    text_ping_interval.on_change = validate_ping_run_parameters
    text_number_of_ping.on_change = validate_ping_run_parameters
    text_start_delay.on_change = validate_ping_run_parameters
    text_transponder_depth.on_change = validate_ping_run_parameters


    icon_button_directory.on_click = select_directory

    button_start.on_click = start_ping_run
    button_stop.on_click = stop_ping_run

    page.add(
        Row(
            controls=[
                Row(
                    [
                    dropdown_gps_port, button_refresh_gps_port, dropdown_gps_baudrate, button_connect_gps
                    ]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
            ),
        Row([text_gps_values], alignment=ft.MainAxisAlignment.CENTER),
        Row(
            controls=[
                Column(
                    [
                        text_ship_name,
                        Row([text_directory_path, icon_button_directory]),
                        text_ping_interval,
                        text_number_of_ping,
                        text_start_delay,
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
        text_gps_values.value = str(pingloggercontroller.gps_controller.nmea_data)
        page.update()
        time.sleep(0.5)


if __name__ == '__main__':
    ft.app(target=main)
    #ft.app(target=main, view=ft.AppView.WEB_BROWSER)