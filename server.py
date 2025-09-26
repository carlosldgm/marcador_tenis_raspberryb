# server.py
import os
os.environ["FLASK_SKIP_DOTENV"] = "1"
from flask import Flask, request, jsonify
from logic import TennisMatch
import display

app = Flask(__name__)

# Crear partido inicial
match = TennisMatch()

# Mostrar mensaje de inicio
display.show_startup()
display.show_score(match)

@app.route("/")
def home():
    return jsonify({
        "status": "Servidor del marcador de tenis activo",
        "endpoints": {
            "start_match": "POST /start-match",
            "point": "POST /point", 
            "undo": "POST /undo",
            "reset": "POST /reset",
            "score": "GET /score",
            "export": "GET /export"
        }
    })

@app.route("/start-match", methods=["POST"])
def start_match():
    """Inicia un nuevo partido con jugadores específicos"""
    try:
        data = request.json or {}
        
        # Reiniciar con nuevos datos
        global match
        match = TennisMatch(
            player1=data.get("player1", "JUG1"),
            player2=data.get("player2", "JUG2"),
            max_sets=data.get("sets", 3)
        )
        
        display.show_message(f"Nuevo partido:\n{match.jugadores[0]['nombre']} vs {match.jugadores[1]['nombre']}")
        display.show_score(match)
        
        return jsonify({
            "status": "ok", 
            "message": "Partido iniciado",
            "match": match.get_score()
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/point", methods=["POST"])
def point():
    """Registra un punto para un jugador"""
    try:
        data = request.json or {}
        player = data.get("player")
        
        if player not in [1, 2]:
            return jsonify({"status": "error", "message": "Player must be 1 or 2"}), 400
        
        print(f"Punto para jugador: {player}")
        
        # Registrar el punto
        msg = match.punto(player)
        
        # Mostrar resultado y actualizar marcador
        display.show_message(msg, duration=1.5)
        display.show_score(match)
        
        return jsonify({
            "status": "ok", 
            "message": msg,
            "match": match.get_score()
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/undo", methods=["POST"])
def undo_point():
    """Deshace el último punto registrado"""
    try:
        msg = match.undo_last_point()
        
        # Mostrar resultado y actualizar marcador
        display.show_message(msg, duration=1.5)
        display.show_score(match)
        
        return jsonify({
            "status": "ok", 
            "message": msg,
            "match": match.get_score()
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset():
    """Reinicia el partido actual"""
    try:
        match.reset()
        display.show_message("Marcador\nreiniciado")
        display.show_score(match)
        
        return jsonify({
            "status": "ok", 
            "message": "Marcador reiniciado",
            "match": match.get_score()
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/score", methods=["GET"])
def get_score():
    """Obtiene el marcador actual"""
    try:
        return jsonify({
            "status": "ok",
            "match": match.get_score()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/export", methods=["GET"])
def export_match():
    """Exporta el partido a JSON"""
    try:
        filename = f"partido_{match.jugadores[0]['nombre']}_{match.jugadores[1]['nombre']}.json"
        result = match.exportar_json(filename)
        
        return jsonify({
            "status": "ok",
            "message": result,
            "filename": filename
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/test-display", methods=["POST"])
def test_display():
    """Endpoint para probar el display"""
    try:
        display.show_demo()
        return jsonify({"status": "ok", "message": "Demo mostrada"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Manejador de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "message": "Internal server error"}), 500

if __name__ == "__main__":
    try:
        print("Iniciando servidor del marcador de tenis...")
        print("Endpoints disponibles:")
        print("  POST /start-match - Iniciar partido")
        print("  POST /point - Registrar punto") 
        print("  POST /undo - Deshacer último punto")
        print("  POST /reset - Reiniciar marcador")
        print("  GET /score - Obtener marcador")
        print("  GET /export - Exportar partido")
        print("  POST /test-display - Probar display")
        
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
        display.clear_display()
    except Exception as e:
        print(f"Error al iniciar servidor: {e}")
        display.clear_display()