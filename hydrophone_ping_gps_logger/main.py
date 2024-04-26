"""
BaudRates: Garmin=4800, GNSS=9600, Ship=????

TODO
---

+ REMOVE SCALE_FACTOR
+ PUT ROW IN COLUMN FOR PROPER RESIZE SPACING>

+ Integrate USB Trnansponder to test.
+ Better GUI scaling.
+ Augmenter les contrastes du GUI
+ Option to ping even without GPS.
+ Logger NMEA heading True HDT.
+ COMPUTER TIME STAMP WITH TIME ZONE
+ Catch encoding error on connection -> wrong baudrate.
+ Catch Disconnection Error after N number of empty NMEA String.
+ FILE ACCESS DENIED Catch error to stop.



+ Raise Error if Transponder was unable top ping.
    at the moment it will only not ping.


"""

import time

from pathlib import Path

import flet as ft
from flet import TextField, ElevatedButton, Text, Row, Column, IconButton, Dropdown, Divider
from flet_core.control_event import ControlEvent

from hydrophone_ping_gps_logger.utils import list_serial_ports
from hydrophone_ping_gps_logger.pingloggercontroller import PingLoggerController, PingRunParameters

# scales half as much on height vs width
SCALE_FACTOR = 0  # in percent

SCALE_FACTOR /= 100

ICON_SIZE = 30 * (1 + SCALE_FACTOR)

FONT_SIZE_S = 14 * (1 + SCALE_FACTOR)
FONT_SIZE_M = 18 * (1 + SCALE_FACTOR)

FIELD_WIDTH_S = 150 * (1 + SCALE_FACTOR)
FIELD_WIDTH_M = 220 * (1 + SCALE_FACTOR)
FIELD_WIDTH_L = 400 * (1 + SCALE_FACTOR)

FIELD_HEIGHT_S = 60 * (1 + SCALE_FACTOR / 2)
FIELD_HEIGHT_M = 70 * (1 + SCALE_FACTOR / 2)

BUTTON_WIDTH_M = 150
BUTTON_WIDTH_L = 220
BUTTON_HEIGHT_M = 40


RUN_BUTTONS_WIDTH = 150
RUN_BUTTONS_HEIGHT = 40
BUTTON_SCALE = (1 + SCALE_FACTOR)

WINDOW_WIDTH = 900 * (1 + SCALE_FACTOR)
WINDOW_HEIGHT = 900 * (1 + SCALE_FACTOR / 2)

VERSION = '1.0.0'

SCALE = 1


def main(page: ft.Page):
    ##### INIT PAGE ####
    page.title = "Ping GPS Logger"
    page.window_width = WINDOW_WIDTH * SCALE
    page.window_height = WINDOW_HEIGHT * SCALE
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT  # DARK

    ###### BackEnd ######
    ping_controller = PingLoggerController()

    ping_controller.transponder_controller.connect()

    ###### CONNECT GPS FIELD ######

    def refresh_comports(e: ControlEvent):
        comport_list = list_serial_ports()
        used_comports = []
        if ping_controller.gps_controller.is_connected:
            used_comports.append(ping_controller.gps_controller.client.port)

        if ping_controller.transponder_controller.is_connected:
            used_comports.append(ping_controller.transponder_controller.client.port)

        dropdown_gps_port.options = [
            ft.dropdown.Option(cp, disabled=True if cp in used_comports else False) for cp in comport_list
        ]

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
        ping_controller.connect_gps(port=dropdown_gps_port.value, baudrate=dropdown_gps_baudrate.value)

        if ping_controller.gps_controller.is_connected:
            button_connect_gps.text = "Disconnect GPS"
            button_connect_gps.bgcolor = ft.colors.RED_200

            dropdown_gps_port.disabled = True
            dropdown_gps_baudrate.disabled = True

            button_connect_gps.on_click = disconnect_gps

            page.update()

    def disconnect_gps(e: ControlEvent):
        ping_controller.disconnect_gps()

        button_connect_gps.text = "Connect GPS"
        button_connect_gps.on_click = connect_gps
        button_connect_gps.bgcolor = ft.colors.GREEN_200

        dropdown_gps_port.disabled = False
        dropdown_gps_baudrate.disabled = False

        page.update()

    button_refresh_comports = IconButton(icon=ft.icons.REFRESH, icon_size=ICON_SIZE, scale=SCALE)

    dropdown_gps_port = Dropdown(
        label="Gps ComPort",
        width=FIELD_WIDTH_M,
        height=FIELD_HEIGHT_M,
        text_size=FONT_SIZE_M,
        alignment=ft.alignment.center,
        options=list(ft.dropdown.Option(comport) for comport in list_serial_ports()),
        on_change=validate_gps_parameters,
        bgcolor=ft.colors.GREY_50,
        scale=SCALE
    )

    dropdown_gps_baudrate = Dropdown(
        label="Gps Baudrate",
        width=FIELD_WIDTH_M,
        height=FIELD_HEIGHT_M,
        text_size=FONT_SIZE_M,
        alignment=ft.alignment.center,
        options=list(ft.dropdown.Option(key=k, text=t) for k, t in zip(
            [2400, 4800, 9600, 19200, 38400, 57600, 115200],
            [None, "4800 (Garmin 19x Hvs)", "9600 (GNSS)", None, None, None, None]
        )),
        on_change=validate_gps_parameters,
        bgcolor=ft.colors.GREY_50,
        scale=SCALE
    )
    button_connect_gps = ElevatedButton(
        text="Connect GPS",
        width=BUTTON_WIDTH_M,
        height=BUTTON_HEIGHT_M,
        disabled=True,
        on_click=connect_gps,
        bgcolor=ft.colors.LIGHT_GREEN,
        scale=SCALE
    )

    text_gps_date = TextField(
        value="", label="date",
        width=FIELD_WIDTH_S,
        height=FIELD_HEIGHT_S,
        text_size=FONT_SIZE_S,
        color=ft.colors.LIGHT_BLUE,
        bgcolor=ft.colors.GREY_50,
        disabled=True,
        scale=SCALE
    )
    text_gps_time = TextField(
        value="",
        label="time",
        width=FIELD_WIDTH_S,
        height=FIELD_HEIGHT_S,
        text_size=FONT_SIZE_S,
        color=ft.colors.LIGHT_BLUE,
        bgcolor=ft.colors.GREY_50,
        disabled=True,
        scale=SCALE
    )
    text_gps_lat = TextField(
        value="",
        label="lon",
        width=FIELD_WIDTH_S,
        height=FIELD_HEIGHT_S,
        text_size=FONT_SIZE_S,
        color=ft.colors.LIGHT_BLUE,
        bgcolor=ft.colors.GREY_50,
        disabled=True,
        scale=SCALE
    )
    text_gps_lon = TextField(
        value="",
        label="lat",
        width=FIELD_WIDTH_S,
        height=FIELD_HEIGHT_S,
        text_size=FONT_SIZE_S,
        color=ft.colors.LIGHT_BLUE,
        bgcolor=ft.colors.GREY_50,
        disabled=True,
        scale=SCALE
    )

    ###### Transponder ######

    def connect_transponder(e: ControlEvent):
        ping_controller.connect_transponder()


    button_connect_transponder = ElevatedButton(
        text="Connect transponder",
        width=BUTTON_WIDTH_L,
        height=BUTTON_HEIGHT_M,
        disabled=True,
        on_click=connect_transponder,
        bgcolor=ft.colors.LIGHT_GREEN,
        scale=SCALE
    )

    icon_transponder_status = IconButton(
        ft.icons.CIRCLE_OUTLINED, icon_color=ft.colors.RED_200, icon_size=ICON_SIZE,
        disabled=True
    )


    ###### RUN SETTING FIELDS ######
    def pick_directory_result(e: ft.FilePickerResultEvent):
        text_directory_path.value = e.path
        text_directory_path.update()

    # adding directory picker
    directory_picker = ft.FilePicker(on_result=pick_directory_result)
    page.overlay.append(directory_picker)

    def select_directory(e: ControlEvent):
        directory_picker.get_directory_path(dialog_title="path to ping log directory", initial_directory=Path().home())

    def on_change_start_delay(e: ControlEvent = None):
        text_countdown_delay.value = str(int(text_start_delay.value))

        validate_ping_run(e)

    def validate_ping_run(e: ControlEvent = None):  #rename
        if (all([text_ship_name.value,
                 text_directory_path.value,
                 text_ping_interval.value,
                 text_number_of_ping.value,
                 text_start_delay.value,
                 text_transponder_depth.value])
                and ping_controller.gps_controller.is_running
                and ping_controller.transponder_controller.is_connected):
            button_start.disabled = False
        else:
            button_start.disabled = True

        page.update()


    text_ship_name = TextField(
        label="Ship Name",
        value="",
        text_size=FONT_SIZE_M,
        text_align=ft.TextAlign.RIGHT,
        width=FIELD_WIDTH_M,
        height=FIELD_HEIGHT_M,
        #scale=SCALE
    )
    text_transponder_depth = TextField(
        label="Transponder depth",
        suffix_text=" meter",
        value="0",
        text_size=FONT_SIZE_M,
        height=FIELD_HEIGHT_M,
        text_align=ft.TextAlign.RIGHT, width=FIELD_WIDTH_S,
        input_filter=ft.InputFilter('^[0-9]*\.?[0-9]{0,2}'),
        #scale=SCALE
    )
    text_directory_path = TextField(
        label="Target Directory",
        value="",
        text_size=FONT_SIZE_M,
        text_align=ft.TextAlign.RIGHT,
        width=FIELD_WIDTH_L,
        height=FIELD_HEIGHT_M,
        disabled=True,
        color=ft.colors.LIGHT_BLUE,
        bgcolor=ft.colors.GREY_50,
        #scale=SCALE
    )
    icon_button_directory = IconButton(
        icon=ft.icons.FOLDER,
        icon_size=ICON_SIZE,
        #scale=SCALE
    )

    text_number_of_ping = TextField(
        label="Number Of Ping",
        value="0",
        text_size=FONT_SIZE_M,
        text_align=ft.TextAlign.RIGHT,
        width=FIELD_WIDTH_M,
        height=FIELD_HEIGHT_M,
        input_filter=ft.InputFilter('^[0-9]*'),
        #scale=SCALE
    )
    text_ping_count = TextField(
        label="Ping Count",
        value="0",
        text_size=FONT_SIZE_M,
        text_align=ft.TextAlign.RIGHT,
        width=FIELD_WIDTH_S,
        height=FIELD_HEIGHT_M,
        disabled=True,
        color=ft.colors.LIGHT_BLUE,
        bgcolor=ft.colors.GREY_50,
        #scale=SCALE
    )
    text_ping_interval = TextField(
        label="Ping Interval",
        value="1",
        suffix_text="second",
        text_size=FONT_SIZE_M,
        text_align=ft.TextAlign.RIGHT,
        width=FIELD_WIDTH_M,
        height=FIELD_HEIGHT_M,
        input_filter=ft.InputFilter('^[0-9]*'),
        #scale=SCALE
    )
    text_start_delay = TextField(
        label="Start Delay",
        suffix_text=" second",
        value="0",
        text_size=FONT_SIZE_M,
        text_align=ft.TextAlign.RIGHT,
        width=FIELD_WIDTH_M,
        height=FIELD_HEIGHT_M,
        input_filter=ft.InputFilter('^[0-9]*'),
        #scale=SCALE
    )
    text_countdown_delay = TextField(
        label="Countdown",
        value="0",
        text_size=FONT_SIZE_M,
        text_align=ft.TextAlign.RIGHT,
        width=FIELD_WIDTH_S,
        height=FIELD_HEIGHT_M,
        disabled=True, suffix_text="second",
        color=ft.colors.LIGHT_BLUE,
        bgcolor=ft.colors.GREY_50,
        #scale=SCALE
    )


    text_ship_name.on_change = validate_ping_run
    text_directory_path.on_change = validate_ping_run
    text_ping_interval.on_change = validate_ping_run
    text_number_of_ping.on_change = validate_ping_run
    text_start_delay.on_change = on_change_start_delay
    text_transponder_depth.on_change = validate_ping_run

    icon_button_directory.on_click = select_directory


    ##### START/STOP RUN #####

    def start_ping_run(e: ControlEvent):
        ping_controller.start_ping_run(
            PingRunParameters(
                output_directory_path=text_directory_path.value,
                ship_name=text_ship_name.value,
                transponder_depth=text_transponder_depth.value,
                ping_interval=float(text_ping_interval.value),
                number_of_pings=int(text_number_of_ping.value),
                start_delay_seconds=int(text_start_delay.value)
            )
        )
        if ping_controller.is_running:
            button_start.disabled = True
            button_pause.disabled = False
            button_stop.disabled = False

            text_ship_name.disabled = True
            icon_button_directory.disabled = True
            text_ping_interval.disabled = True
            text_number_of_ping.disabled = True
            text_start_delay.disabled = True
            text_transponder_depth.disabled = True


            page.update()

    def pause_ping_run(e: ControlEvent = None):
        if ping_controller.is_running:
            ping_controller.pause_ping_run()
        button_pause.text = "Resume"
        button_pause.icon = ft.icons.START_ROUNDED
        button_pause.on_click = unpause_ping_run
        page.update()

    def unpause_ping_run(e: ControlEvent = None):
        ping_controller.unpause_ping_run()
        button_pause.text = "Pause"
        button_pause.icon = ft.icons.PAUSE_ROUNDED
        button_pause.on_click = pause_ping_run

        page.update()

    def stop_ping_run(e: ControlEvent):

        unpause_ping_run(e)
        time.sleep(0.1)  # this prevent threading bug with the pause event.

        button_stop.disabled = True
        button_pause.disabled = True

        validate_ping_run(e)

        text_ship_name.disabled = False
        icon_button_directory.disabled = False
        text_ping_interval.disabled = False
        text_number_of_ping.disabled = False
        text_start_delay.disabled = False
        text_transponder_depth.disabled = False

        page.update()

        ping_controller.stop_ping_run()

    button_start = ElevatedButton(
        text="start",
        icon=ft.icons.PLAY_ARROW_ROUNDED,
        width=RUN_BUTTONS_WIDTH,
        height=RUN_BUTTONS_HEIGHT,
        disabled=True,
        on_click=start_ping_run,
        bgcolor=ft.colors.GREEN_200,
        #scale=(1 + SCALE_FACTOR)
    )
    button_pause = ElevatedButton(
        text="Pause",
        width=RUN_BUTTONS_WIDTH,
        height=RUN_BUTTONS_HEIGHT,
        disabled=True,
        on_click=pause_ping_run,
        bgcolor=ft.colors.ORANGE_200,
        icon=ft.icons.PAUSE_ROUNDED,
        #scale=(1 + SCALE_FACTOR)
    )
    button_stop = ElevatedButton(
        text="Stop",
        width=BUTTON_WIDTH_M,
        height=BUTTON_HEIGHT_M,
        disabled=True,
        on_click=stop_ping_run,
        bgcolor=ft.colors.RED_200,
        icon=ft.icons.STOP_ROUNDED,
        #scale=(1 + SCALE_FACTOR)
    )

    text_title = Text(
        value="Ping GPS Logger",
        theme_style=ft.TextThemeStyle.DISPLAY_SMALL,
        weight=ft.FontWeight.W_500,
        #scale=SCALE
    )
    text_version = Text(
        f"Version: {VERSION}  ",
        theme_style=ft.TextThemeStyle.BODY_SMALL,
        weight=ft.FontWeight.W_500,
        #scale=SCALE
    )


    #### Layout ####

    def add_divier():
        return Divider(height=2*SCALE, thickness=2*SCALE, leading_indent=30, trailing_indent=30)


    layout_title = Row(
        [text_title, text_version],
        alignment=ft.MainAxisAlignment.CENTER,
        scale=SCALE
    )

    layout_gps = Row(
        [button_refresh_comports, dropdown_gps_port,  dropdown_gps_baudrate, button_connect_gps],
        alignment=ft.MainAxisAlignment.CENTER,
        scale=SCALE
    )

    page.add(
        layout_title,
        add_divier(),
        layout_gps,
        Row(
            [text_gps_date, text_gps_time, text_gps_lat, text_gps_lon],
            alignment=ft.MainAxisAlignment.CENTER,
            scale=SCALE
        ),
        add_divier(),
        Row(
            [button_connect_transponder, icon_transponder_status],
            alignment=ft.MainAxisAlignment.CENTER,
            scale=SCALE
        ),
        add_divier(),
        Row(
            controls=[
                Column(
                    [
                        Row([text_directory_path, icon_button_directory], alignment=ft.MainAxisAlignment.CENTER),
                        Row([text_ship_name, text_transponder_depth], alignment=ft.MainAxisAlignment.CENTER),
                    ], alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scale=SCALE
        ),
        add_divier(),
        Row(
            controls=[
                Column(
                    [
                        text_ping_interval,
                        Row([text_number_of_ping, text_ping_count]),
                        Row([text_start_delay, text_countdown_delay]),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scale=SCALE
        ),
        add_divier(),
        Row(
            [button_start, button_pause, button_stop],
            alignment=ft.MainAxisAlignment.CENTER,
            scale=SCALE
        )
    )


    def refresh_gps_values():
        text_gps_date.value = ping_controller.gps_controller.nmea_data.date
        text_gps_time.value = ping_controller.gps_controller.nmea_data.time
        text_gps_lat.value = ping_controller.gps_controller.nmea_data.latitude
        text_gps_lon.value = ping_controller.gps_controller.nmea_data.longitude

    while True:
        refresh_gps_values()

        if not ping_controller.transponder_controller.is_connected:
            icon_transponder_status.icon = ft.icons.CIRCLE_OUTLINED
            icon_transponder_status.icon_color = ft.colors.RED_200
            button_connect_transponder.disabled = False
        else:
            icon_transponder_status.icon = ft.icons.CIRCLE
            icon_transponder_status.icon_color = ft.colors.GREEN_200
            button_connect_transponder.disabled = True

        if ping_controller.is_running:
            text_ping_count.value = str(int(ping_controller.ping_count))
            text_countdown_delay.value = str(int(ping_controller.count_down_delay)) or "----"

        if not ping_controller.is_running:
            validate_ping_run()

        page.update()
        time.sleep(0.05)


import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ft.app(target=main)
