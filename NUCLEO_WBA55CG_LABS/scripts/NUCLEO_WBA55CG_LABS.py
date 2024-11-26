import clr
clr.AddReference("Renode-peripherals")
clr.AddReference("IronPython.StdLib")

import os
import time

import SimpleHTTPServer
import SocketServer
from threading import Thread
import base64
import tempfile
import subprocess

from Antmicro.Renode.Peripherals.Miscellaneous import Button
from Antmicro.Renode.Peripherals.Miscellaneous import LED
from Antmicro.Renode.Peripherals.Sensors import ArduCAMMini2MPPlus
from Antmicro.Renode.Peripherals.UART import IUART
from Antmicro.Renode.Peripherals.CPU import BaseCPU
from Antmicro.Renode.Core import Machine

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
parent_directory = os.path.dirname(current_directory)
templates_directory = os.path.dirname(parent_directory)

os.chdir(templates_directory)

sys.path.append(templates_directory)

from websocket_server import WebsocketServer

def send_message(message):
    if websocket_server is not None and len(websocket_server.clients) > 0:
        for client in websocket_server.clients:
            try:
                websocket_server.send_message(client, message)
            except Exception as e:
                # in case something got disconnected
                pass

def message_received(client, server, message):
    splitted = message.split("|", 1)
    if splitted[0] == "IMAGE":
        imageFile = tempfile.NamedTemporaryFile(delete=False)
        data = base64.b64decode(splitted[1])
        imageFile.write(data)
        imageFile.close()
        camera_replace_image(imageFile.name)
    elif message == "PRESS_BUTTON":
	press_button()	
    elif message == "RELEASE_BUTTON":
	release_button()
    elif message == "RESET_BUTTON_PRESSED":
        reset_cpu()	
    elif message == "RESET_BUTTON_RELEASED":
        start_machine()
    elif splitted[0] == "RECEIVE_UART":
        if len(splitted) > 1:
            uart_char = splitted[1]
            if uart_char:
                receive_uart_chars('sysbus.usart2', uart_char)
    else:
        if len(message) > 200:
            message = message[:200]+'..'
            print("Client(%d) said: %s" % (client['id'], message))

def reset_cpu():
    machine.Pause()
    cpus = machine.GetPeripheralsOfType[BaseCPU]()
    for cpu in cpus:
        cpu.Reset()
    
def start_machine():
    machine.Start() 
    
def press_button():
    print("Press Button")
    buttons = machine.GetPeripheralsOfType[Button]()
    for button in buttons:
      button.Press()

def release_button():
    print("Release Button")
    buttons = machine.GetPeripheralsOfType[Button]()
    for button in buttons:
    	button.Release()

def blink_led(led, state):
    send_message("|".join(["LED", machine.GetLocalName(led), str(state)]))


def send_uart_chars(char, uartName):
    send_message("|".join(["UART", uartName, chr(char)]))
    
    
def receive_uart_chars(uart_name, uart_char):
    uarts = machine.GetPeripheralsOfType[IUART]()

    for uart in uarts:
        print
        uartName = clr.Reference[str]()
        if machine.TryGetAnyName(uart, uartName):
            if machine.GetAnyNameOrTypeName(uart) == uart_name:
                byte_value = ord(uart_char)
                print("Writing byte", byte_value, "to UART {uartName}",uart_name)
                uart.WriteChar(byte_value)
                return
        else:
            print("Failed to get the name of the UART peripheral")
        

def camera_replace_image(imagePath):
    cameras = machine.GetPeripheralsOfType[ArduCAMMini2MPPlus]()
    for camera in cameras:
        camera.ImageSource = imagePath
        break
    print("Image uploaded")


main_server = None
server_thread = None
websocket_server = None
websocket_thread = None

uart_event_map = {}
machine = None

print("Adding serveVisualization command.")
def mc_serveVisualization(port, ws_port):
    global main_server
    global server_thread
    global websocket_server
    global websocket_thread
    global machine

    # get emulation
    emulation = Antmicro.Renode.Core.EmulationManager.Instance.CurrentEmulation

    # Assume a single machine for now.
    machine = emulation.Machines[0]

    leds = machine.GetPeripheralsOfType[LED]()
    for led in leds:
        led.StateChanged += blink_led

    uarts = machine.GetPeripheralsOfType[IUART]()
    for uart in uarts:
        uartName = clr.Reference[str]()
        if not machine.TryGetAnyName(uart, uartName):
            on_received = lambda char: send_uart_chars(char, uartName)
        else:
            on_received = lambda char: send_uart_chars(char, "unknown_uart")
        uart.CharReceived += on_received
        uart_event_map[uart] = on_received

    # setting up server threads
    websocket_server = WebsocketServer(ws_port)
    websocket_server.set_fn_message_received(message_received)
    websocket_thread = Thread(target=websocket_server.serve_forever)
    websocket_thread.deamon = True
    websocket_thread.start()

    try:
        main_server = SocketServer.TCPServer(("", port), SimpleHTTPServer.SimpleHTTPRequestHandler)
        server_thread = Thread(target=main_server.serve_forever)
        server_thread.deamon = True

        print("Serving interactive visualization at port", port)
        server_thread.start()
    except:
        import traceback
        traceback.print_exc()

def mc_stopVisualization():
    global main_server
    global server_thread
    global websocket_server
    global websocket_thread
    global uart_event_map

    if main_server is None:
        print("Start visualization with `serveVisualization {port}` first")
        return

    for uart in uart_event_map.keys():
        uart.CharReceived -= uart_event_map[uart]

    main_server.shutdown()
    main_server.server_close()
    websocket_server.close_server()
    server_thread.join()
    websocket_thread.join()
    main_server = None
    server_thread = None
    websocket_server = None
    websocket_thread = None

