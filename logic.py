# logic.py
import json

class TennisMatch:
    PUNTOS = ["0", "15", "30", "40", "A"]

    def __init__(self, player1="JUG1", player2="JUG2", max_sets=3):
        self.jugadores = [{"nombre": player1}, {"nombre": player2}]
        self.max_sets = max_sets
        self.historial = []                         # sets cerrados
        self.set_actual = {"set": 1, "games": []}   # set en curso
        self.game_actual = {"game": 1, "puntos": []}# game en curso (lista de snapshots)
        self.puntos = [0, 0]                       # conteo interno del game actual
        self.tie_break = False
        self.match_finished = False
        
        # Historial de acciones para poder deshacer
        self.action_history = []

    def reset(self):
        """Reinicia el partido completo"""
        self.__init__(
            self.jugadores[0]["nombre"], 
            self.jugadores[1]["nombre"], 
            self.max_sets
        )

    def _save_state(self):
        """Guarda el estado actual para poder deshacerlo"""
        import copy
        state = {
            "historial": copy.deepcopy(self.historial),
            "set_actual": copy.deepcopy(self.set_actual),
            "game_actual": copy.deepcopy(self.game_actual),
            "puntos": self.puntos.copy(),
            "tie_break": self.tie_break,
            "match_finished": self.match_finished
        }
        self.action_history.append(state)
        
        # Limitar historial a últimas 50 acciones para no consumir demasiada memoria
        if len(self.action_history) > 50:
            self.action_history.pop(0)

    def undo_last_point(self):
        """Deshace el último punto registrado"""
        if not self.action_history:
            return "No hay acciones para deshacer"
        
        # Restaurar el estado anterior
        last_state = self.action_history.pop()
        self.historial = last_state["historial"]
        self.set_actual = last_state["set_actual"] 
        self.game_actual = last_state["game_actual"]
        self.puntos = last_state["puntos"]
        self.tie_break = last_state["tie_break"]
        self.match_finished = last_state["match_finished"]
        
        return "Último punto deshecho"

    def _label(self, val):
        """Convierte número de puntos a etiqueta de tenis"""
        return self.PUNTOS[val] if val <= 3 else "A"

    def is_tiebreak_game(self, game):
        """Verifica si un game es tie-break"""
        for snap in game.get("puntos", []):
            if not (snap[0] in self.PUNTOS and snap[1] in self.PUNTOS):
                return True
        return False

    def winner_from_game(self, game):
        """Devuelve 0 si ganó jugador1, 1 si ganó jugador2, None si no se puede determinar."""
        pts = game.get("puntos", [])
        if not pts:
            return None
        if self.is_tiebreak_game(game):
            try:
                a = int(pts[-1][0]); b = int(pts[-1][1])
                if a > b: return 0
                if b > a: return 1
                return None
            except Exception:
                return None
        
        # Para games normales, el ganador es quien cerró el game
        # Esto se determina por la lógica de cierre, no por el último snapshot
        # Por eso, necesitamos una lógica diferente aquí
        order = {"0":0, "15":1, "30":2, "40":3, "A":4}
        
        # Buscar el patrón que indica quién ganó basado en el desarrollo del game
        max_a = max_b = 0
        for p in pts:
            a = order.get(p[0], 0)
            b = order.get(p[1], 0)
            max_a = max(max_a, a)
            max_b = max(max_b, b)
        
        # Si alguien llegó a A (advantage), probablemente ganó
        if max_a == 4 and max_b < 4: return 0
        if max_b == 4 and max_a < 4: return 1
        
        # Si ambos llegaron a A, el último snapshot debería mostrar quién ganó
        if max_a == 4 and max_b == 4:
            # En este caso, el game debería haberse cerrado cuando alguien ganó desde A
            # Pero como el game se cerró, el ganador es quien tenía más puntos internamente
            return None  # Esto no debería pasar si la lógica es correcta
            
        # Para casos normales sin advantage
        final_a = order.get(pts[-1][0], 0)
        final_b = order.get(pts[-1][1], 0)
        if final_a > final_b: return 0
        if final_b > final_a: return 1
        
        return None

    def compute_games_counts_for_set(self, set_data, upto_index=None):
        """Cuenta games ganados en el set. upto_index es exclusivo."""
        g1 = g2 = 0
        games = set_data.get("games", [])
        if upto_index is None:
            upto_index = len(games)
        for g in games[:upto_index]:
            # Primero verificar si tenemos información directa del ganador
            if "winner" in g:
                if g["winner"] == 0: 
                    g1 += 1
                elif g["winner"] == 1: 
                    g2 += 1
            else:
                # Fallback a la lógica anterior si no tenemos info del ganador
                w = self.winner_from_game(g)
                if w == 0: g1 += 1
                elif w == 1: g2 += 1
        return g1, g2

    def compute_sets_won(self):
        """Calcula sets ganados por cada jugador"""
        sets_won = [0, 0]
        for s in self.historial:
            g1, g2 = self.compute_games_counts_for_set(s)
            if g1 > g2:
                sets_won[0] += 1
            elif g2 > g1:
                sets_won[1] += 1
        return sets_won

    def check_match_winner(self):
        """Verifica si hay ganador del partido"""
        sets_won = self.compute_sets_won()
        sets_needed = (self.max_sets // 2) + 1
        
        if sets_won[0] >= sets_needed:
            self.match_finished = True
            return 0
        elif sets_won[1] >= sets_needed:
            self.match_finished = True
            return 1
        return None

    def punto(self, jugador):
        """Registra un punto ganado por el jugador especificado"""
        if self.match_finished:
            return "¡Partido terminado!"
            
        if jugador not in [1, 2]:
            return "Jugador inválido"
        
        # Guardar estado antes de hacer cambios
        self._save_state()
            
        jugador = jugador - 1  # convertir a índice 0-1
        otro = 1 - jugador

        # TIE-BREAK: grabar snapshot (números) y si ganó, cerrar game y set
        if self.tie_break:
            self.puntos[jugador] += 1
            # grabar snapshot numérico
            self.game_actual["puntos"].append([str(self.puntos[0]), str(self.puntos[1])])

            # si ganó tie-break -> cerrar game y set
            if self.puntos[jugador] >= 7 and (self.puntos[jugador] - self.puntos[otro]) >= 2:
                self._cerrar_game(jugador)  # Pasar explícitamente el ganador
                self._cerrar_set()
                self.tie_break = False
                self.puntos = [0,0]
                
                # Verificar ganador del partido
                winner = self.check_match_winner()
                if winner is not None:
                    return f"¡{self.jugadores[winner]['nombre']} gana el partido!"

            return f"Punto para {self.jugadores[jugador]['nombre']}"

        # GAME normal: actualizar contador interno
        self.puntos[jugador] += 1
        
        # DEBUG: Imprimir estado de puntos
        print(f"DEBUG: Punto para jugador {jugador+1}. Puntos: [{self.puntos[0]}, {self.puntos[1]}]")

        # Verificar si ese punto ganó el game (condición de ganador)
        if self.puntos[jugador] >= 4 and (self.puntos[jugador] - self.puntos[otro]) >= 2:
            # ¡Game ganado! -> cerrar el game
            print(f"DEBUG: Game ganado por jugador {jugador+1} (índice {jugador})")
            self._cerrar_game(jugador)  # Pasar explícitamente el ganador
            
            # Verificar ganador del partido
            winner = self.check_match_winner()
            if winner is not None:
                return f"¡{self.jugadores[winner]['nombre']} gana el partido!"
                
            return f"Game para {self.jugadores[jugador]['nombre']}"

        # Si no se ganó el game, registrar el snapshot resultante (15/30/40/A)
        self.game_actual["puntos"].append([self._label(self.puntos[0]), self._label(self.puntos[1])])

        return f"Punto para {self.jugadores[jugador]['nombre']}"

    def _cerrar_game(self, ganador=None):
        # Si no se especifica ganador, determinarlo por los puntos (esto no debería pasar)
        if ganador is None:
            if self.tie_break:
                ganador = 0 if self.puntos[0] > self.puntos[1] else 1
            else:
                ganador = 0 if self.puntos[0] > self.puntos[1] else 1
        
        print(f"DEBUG: Cerrando game, ganador especificado: {ganador+1}")
        
        # Agregar información del ganador al game
        self.game_actual["winner"] = ganador
        
        # guardar el game actual en el set
        self.set_actual["games"].append(self.game_actual)
        
        print(f"DEBUG: Game guardado con winner: {self.game_actual['winner']}")
        
        # preparar siguiente game
        self.game_actual = {"game": len(self.set_actual["games"]) + 1, "puntos": []}
        self.puntos = [0, 0]

        # chequear conteo de games en el set para tie-break o cierre de set
        g1, g2 = self.compute_games_counts_for_set(self.set_actual)
        print(f"DEBUG: Conteo de games después de cerrar: J1={g1}, J2={g2}")
        
        if g1 == 6 and g2 == 6:
            # activar tie-break para el próximo game
            self.tie_break = True
        elif (g1 >= 6 or g2 >= 6) and abs(g1 - g2) >= 2:
            self._cerrar_set()

    def _cerrar_set(self):
        # mover set_actual a historial
        self.historial.append(self.set_actual)
        # iniciar nuevo set vacío
        self.set_actual = {"set": self.set_actual["set"] + 1, "games": []}
        self.game_actual = {"game": 1, "puntos": []}
        self.puntos = [0, 0]
        self.tie_break = False

    def get_score(self):
        """Devuelve el marcador actual en formato para la API y display"""
        # Sets completados
        completed_counts = [self.compute_games_counts_for_set(s) for s in self.historial]
        sets_won = self.compute_sets_won()
        
        # Games del set actual
        cur_g1, cur_g2 = self.compute_games_counts_for_set(self.set_actual)

        # Puntos actuales con lógica de advantage
        if self.tie_break:
            p1_points, p2_points = str(self.puntos[0]), str(self.puntos[1])
        else:
            # Lógica especial para advantage: si uno tiene ventaja, el otro no muestra nada
            if self.puntos[0] >= 3 and self.puntos[1] >= 3:  # Situación de deuce o advantage
                if self.puntos[0] > self.puntos[1]:  # Jugador 1 tiene advantage
                    p1_points, p2_points = "A", ""
                elif self.puntos[1] > self.puntos[0]:  # Jugador 2 tiene advantage
                    p1_points, p2_points = "", "A"
                else:  # Empate en deuce
                    p1_points, p2_points = "40", "40"
            else:
                # Puntuación normal
                p1_points, p2_points = self._label(self.puntos[0]), self._label(self.puntos[1])

        return {
            "player1": {
                "name": self.jugadores[0]["nombre"],
                "sets_won": sets_won[0],
                "current_games": cur_g1,
                "current_points": p1_points,
                "completed_sets": [g for g, _ in completed_counts]
            },
            "player2": {
                "name": self.jugadores[1]["nombre"],
                "sets_won": sets_won[1],
                "current_games": cur_g2,
                "current_points": p2_points,
                "completed_sets": [g for _, g in completed_counts]
            },
            "current_set": self.set_actual["set"],
            "tie_break": self.tie_break,
            "match_finished": self.match_finished,
            "max_sets": self.max_sets
        }

    def exportar_json(self, archivo="partido.json"):
        """Exporta el partido completo a JSON"""
        # construimos historial final incluyendo set en curso si tiene games o puntos actuales
        temp_hist = []
        for s in self.historial:
            temp_hist.append({
                "set": s["set"],
                "games": s["games"]
            })
        # si el set actual tiene games cerrados, lo incluimos; si el game actual tiene puntos, lo agregamos también
        if self.set_actual["games"] or self.game_actual["puntos"]:
            sa_games = list(self.set_actual["games"])  # copy
            if self.game_actual["puntos"]:
                sa_games.append(self.game_actual)
            temp_hist.append({
                "set": self.set_actual["set"],
                "games": sa_games
            })

        datos = {
            "jugadores": [{"nombre": self.jugadores[0]["nombre"]}, {"nombre": self.jugadores[1]["nombre"]}],
            "historial": temp_hist,
            "max_sets": self.max_sets
        }
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        return f"JSON exportado a '{archivo}'"