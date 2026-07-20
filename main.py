#!/usr/bin/env python3
# main.py
import argparse
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from match_controller import MatchController
import serial_gateway
from server import create_app


def main():
    parser = argparse.ArgumentParser(description="Marcador de tenis")
    parser.add_argument(
        "--with-api",
        action="store_true",
        help="Levanta también la API Flask (opcional) sobre el mismo estado del partido"
    )
    args = parser.parse_args()

    # Única instancia de estado, compartida por gateway y Flask
    controller = MatchController()

    if args.with_api:
        app = create_app(controller)

        def run_flask():
            app.run(host="0.0.0.0", port=5000, use_reloader=False)

        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        print("API Flask disponible en http://0.0.0.0:5000")

    try:
        # El gateway serial corre en el hilo principal
        serial_gateway.run(controller)
    except KeyboardInterrupt:
        print("\nCerrando...")


if __name__ == "__main__":
    main()