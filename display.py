# display.py
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time

# Configuración del panel
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.gpio_slowdown = 4
options.brightness = 80
options.led_rgb_sequence = 'RGB'

matrix = RGBMatrix(options=options)
canvas = matrix.CreateFrameCanvas()

# Fuentes
font_main = graphics.Font()
font_names = graphics.Font()

# Cargar fuentes según el número de sets
try:
    font_main.LoadFont("../../fonts/7x13.bdf")  # Fuente para 3 sets
    font_names.LoadFont("../../fonts/6x9.bdf")  # Fuente para nombres
except:
    # Fallback si no encuentra las fuentes
    try:
        font_main.LoadFont("../fonts/7x13.bdf")
        font_names.LoadFont("../fonts/6x9.bdf")
    except:
        print("Error: No se pudieron cargar las fuentes")

# Colores
red = graphics.Color(255, 0, 0)
green = graphics.Color(0, 255, 0)
blue = graphics.Color(0, 0, 255)
white = graphics.Color(255, 255, 255)
yellow = graphics.Color(255, 255, 0)

def show_message(text, duration=2, y=15, color=yellow):
    """Muestra un mensaje temporal en el panel"""
    canvas.Clear()
    
    # Si el texto es muy largo, dividirlo en líneas
    lines = text.split('\n')
    if len(lines) == 1 and len(text) > 10:
        # Texto largo en una línea, dividir por palabras
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            if len(current_line + " " + word) <= 10:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
    
    # Mostrar las líneas centradas horizontalmente
    start_y = y - (len(lines) * 6) // 2
    for i, line in enumerate(lines):
        # Para textos largos como "Punto para:", usar posición más a la izquierda
        if len(line) > 8:  # Si el texto es largo
            x_centered = 1  # Posición fija cerca del borde izquierdo
        else:
            # Calcular posición x para centrar textos cortos
            text_width = len(line) * 5
            x_centered = max(1, (64 - text_width) // 2)
        graphics.DrawText(canvas, font_names, x_centered, start_y + i * 10, color, line)
    
    matrix.SwapOnVSync(canvas)
    time.sleep(duration)

def show_score(match):
    """Muestra el marcador completo del partido"""
    canvas.Clear()
    
    score = match.get_score()
    
    # Posiciones base
    x0 = 2
    y0 = 10
    
    # Nombres de jugadores (máximo 3 caracteres)
    p1_name = score["player1"]["name"][:3].upper()
    p2_name = score["player2"]["name"][:3].upper()
    
    graphics.DrawText(canvas, font_names, x0, y0, blue, p1_name)
    graphics.DrawText(canvas, font_names, x0, y0 + 12, blue, p2_name)
    
    # Sets completados
    x_offset = 23
    for i, (g1, g2) in enumerate(zip(score["player1"]["completed_sets"], 
                                    score["player2"]["completed_sets"])):
        graphics.DrawText(canvas, font_main, x0 + x_offset + (i * 8), y0, green, str(g1))
        graphics.DrawText(canvas, font_main, x0 + x_offset + (i * 8), y0 + 12, green, str(g2))
    
    # Games del set actual (si el partido no ha terminado)
    if not score["match_finished"]:
        games_x = x0 + x_offset + (len(score["player1"]["completed_sets"]) * 8)
        graphics.DrawText(canvas, font_main, games_x, y0, green, 
                         str(score["player1"]["current_games"]))
        graphics.DrawText(canvas, font_main, games_x, y0 + 12, green, 
                         str(score["player2"]["current_games"]))
        
        # Puntos actuales - siempre en la posición del tercer set (x0 + 47)
        points_x = x0 + 47  # Posición fija donde estaría el tercer set
        
        # Color especial para tie-break
        points_color = red if score["tie_break"] else yellow
        
        graphics.DrawText(canvas, font_main, points_x, y0, points_color, 
                         str(score["player1"]["current_points"]))
        graphics.DrawText(canvas, font_main, points_x, y0 + 12, points_color, 
                         str(score["player2"]["current_points"]))
    else:
        # Si el partido terminó, mostrar indicador
        winner_name = ""
        if score["player1"]["sets_won"] > score["player2"]["sets_won"]:
            winner_name = p1_name
        else:
            winner_name = p2_name
            
        # Mostrar indicador de ganador
        graphics.DrawText(canvas, font_names, x0 + 40, y0 + 6, red, "WIN:")
        graphics.DrawText(canvas, font_names, x0 + 40, y0 + 16, red, winner_name)
    
    matrix.SwapOnVSync(canvas)

def show_startup():
    """Muestra mensaje de inicio"""
    show_message("TENIS\nMARCADOR", 2, 16, green)

def clear_display():
    """Limpia el display"""
    canvas.Clear()
    matrix.Clear()

def show_demo():
    """Función de demostración para probar las posiciones"""
    canvas.Clear()
    x0 = 2
    y0 = 10
    
    # Simular marcador: CAR vs EMI, 6-4, 2-6, 5-2, 15-30
    graphics.DrawText(canvas, font_names, x0, y0, blue, "CAR")
    graphics.DrawText(canvas, font_names, x0, y0+12, blue, "EMI")    
    
    # Set 1
    graphics.DrawText(canvas, font_main, x0+23, y0, green, "6")
    graphics.DrawText(canvas, font_main, x0+23, y0+12, green, "4") 
    
    # Set 2
    graphics.DrawText(canvas, font_main, x0+31, y0, green, "2")
    graphics.DrawText(canvas, font_main, x0+31, y0+12, green, "6") 
    
    # Set 3 (games actuales)
    graphics.DrawText(canvas, font_main, x0+39, y0, green, "5")
    graphics.DrawText(canvas, font_main, x0+39, y0+12, green, "2")         
    
    # Puntos
    graphics.DrawText(canvas, font_main, x0+47, y0, yellow, "15")
    graphics.DrawText(canvas, font_main, x0+47, y0+12, yellow, "30")   
    
    matrix.SwapOnVSync(canvas)
    time.sleep(5)

if __name__ == "__main__":
    show_demo()
    clear_display()