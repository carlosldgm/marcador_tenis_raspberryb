# match_controller.py
import threading
from logic import TennisMatch
import display


class MatchController:
    """
    Dueño único del estado del partido y del display.
    Tanto el gateway serial como la API Flask deben usar SIEMPRE
    esta misma instancia para evitar estados desincronizados.
    El lock evita que un punto por serial y un request HTTP
    modifiquen el estado al mismo tiempo.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.match = TennisMatch()
        display.show_startup()
        display.show_score(self.match)

    def start_match(self, player1="JUG1", player2="JUG2", max_sets=3):
        with self._lock:
            self.match = TennisMatch(player1=player1, player2=player2, max_sets=max_sets)
            display.show_message(f"Nuevo partido:\n{player1} vs {player2}")
            display.show_score(self.match)
            return self.match.get_score()

    def point(self, player):
        with self._lock:
            msg = self.match.punto(player)
            display.show_message(msg, duration=1.5)
            display.show_score(self.match)
            return msg

    def undo(self):
        with self._lock:
            msg = self.match.undo_last_point()
            display.show_message(msg, duration=1.5)
            display.show_score(self.match)
            return msg

    def reset(self):
        with self._lock:
            self.match.reset()
            display.show_message("Marcador\nreiniciado")
            display.show_score(self.match)
            return "Marcador reiniciado"

    def get_score(self):
        with self._lock:
            return self.match.get_score()

    def export_json(self):
        with self._lock:
            filename = f"partido_{self.match.jugadores[0]['nombre']}_{self.match.jugadores[1]['nombre']}.json"
            result = self.match.exportar_json(filename)
            return result, filename

    def test_display(self):
        with self._lock:
            display.show_demo()