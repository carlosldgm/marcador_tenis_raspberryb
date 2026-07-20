# server.py
from flask import Flask, request, jsonify


def create_app(controller):
    """
    Crea la app Flask usando una instancia ya existente de MatchController.
    Flask nunca tiene su propio estado: siempre lee/escribe sobre la
    misma instancia que usa el gateway serial.
    """
    app = Flask(__name__)

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
        try:
            data = request.json or {}
            score = controller.start_match(
                player1=data.get("player1", "JUG1"),
                player2=data.get("player2", "JUG2"),
                max_sets=data.get("sets", 3)
            )
            return jsonify({"status": "ok", "message": "Partido iniciado", "match": score})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/point", methods=["POST"])
    def point():
        try:
            data = request.json or {}
            player = data.get("player")

            if player not in [1, 2]:
                return jsonify({"status": "error", "message": "Player must be 1 or 2"}), 400

            msg = controller.point(player)
            return jsonify({"status": "ok", "message": msg, "match": controller.get_score()})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/undo", methods=["POST"])
    def undo_point():
        try:
            msg = controller.undo()
            return jsonify({"status": "ok", "message": msg, "match": controller.get_score()})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/reset", methods=["POST"])
    def reset():
        try:
            msg = controller.reset()
            return jsonify({"status": "ok", "message": msg, "match": controller.get_score()})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/score", methods=["GET"])
    def get_score():
        try:
            return jsonify({"status": "ok", "match": controller.get_score()})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/export", methods=["GET"])
    def export_match():
        try:
            result, filename = controller.export_json()
            return jsonify({"status": "ok", "message": result, "filename": filename})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/test-display", methods=["POST"])
    def test_display():
        try:
            controller.test_display()
            return jsonify({"status": "ok", "message": "Demo mostrada"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"status": "error", "message": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    # Permite seguir corriendo server.py solo, standalone,
    # para debug rápido sin gateway serial ni main.py.
    from match_controller import MatchController

    controller = MatchController()
    app = create_app(controller)

    try:
        print("Iniciando servidor del marcador de tenis (standalone)...")
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
        controller.match  # noop, sólo referencia