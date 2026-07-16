#!/usr/bin/env python3

import serial
import requests

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 115200

BASE_URL = "http://localhost:5000"

print("--------------------------------")
print(" Tennis Serial Gateway")
print("--------------------------------")

ser = serial.Serial(
    SERIAL_PORT,
    BAUDRATE,
    timeout=1
)

def post(endpoint, body=None):

    try:

        if body:

            r = requests.post(
                BASE_URL + endpoint,
                json=body,
                timeout=2
            )

        else:

            r = requests.post(
                BASE_URL + endpoint,
                timeout=2
            )

        print(f"{endpoint} -> {r.status_code}")

    except Exception as e:

        print(e)


while True:

    try:

        command = ser.readline().decode().strip()

        if command == "":
            continue

        print("RX:", command)

        if command == "POINT:1":

            post("/point", {
                "player":1
            })

        elif command == "POINT:2":

            post("/point", {
                "player":2
            })

        elif command == "UNDO":

            post("/undo")

        elif command == "RESET":

            post("/reset")

        elif command == "TEST":

            post("/test-display")

        else:

            print("Comando desconocido:", command)

    except Exception as e:

        print(e)