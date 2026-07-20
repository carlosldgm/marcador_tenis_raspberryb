#!/usr/bin/env python3
# serial_gateway.py
import serial

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 115200


def run(controller):
    """
    Lee continuamente el puerto serial y llama directo a los métodos
    del MatchController. No conoce Flask ni HTTP.
    """
    print("--------------------------------")
    print(" Tennis Serial Gateway")
    print("--------------------------------")

    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

    while True:
        try:
            command = ser.readline().decode().strip()

            if command == "":
                continue

            print("RX:", command)

            if command == "POINT:1":
                controller.point(1)

            elif command == "POINT:2":
                controller.point(2)

            elif command == "UNDO":
                controller.undo()

            elif command == "RESET":
                controller.reset()

            elif command == "TEST":
                controller.test_display()

            else:
                print("Comando desconocido:", command)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    # Permite correr el gateway solo, sin main.py ni Flask,
    # para pruebas rápidas del hardware.
    from match_controller import MatchController

    controller = MatchController()
    run(controller)