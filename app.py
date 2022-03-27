import websocket
from time import sleep
import rel
import json
import RPi.GPIO as GPIO
from examples.pn532 import *

def on_message(ws, message):
    pass

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print('Disconnected')

def on_open(ws):
    print('Connected')
    pn532 = PN532_UART(debug=False, reset=20)
    ic, ver, rev, support = pn532.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
    # Configure PN532 to communicate with MiFare cards
    pn532.SAM_configuration()
    while ws.sock.connected:
        try:
            print('Waiting for RFID/NFC card...')
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=0.5)
            print('.', end="")
            # Try again if no card is available.
            if uid is None:
                continue
            card_id = ''.join([hex(i).lstrip("0x") for i in uid])
            print('Found card with UID:', card_id)
            message = json.dumps({"type": "keyDetected", "key": card_id})
            ws.send(message)
            sleep(1)
        except Exception as e:
            print(e)
    GPIO.cleanup()

if __name__ == '__main__':
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://141.45.33.204:5001",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)        # Keyboard Interrupt
    rel.dispatch()
