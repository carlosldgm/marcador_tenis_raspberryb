# PROJECT_CONTEXT.md

# Marcador Electrónico de Tenis

## Descripción General

Este proyecto implementa un marcador electrónico de tenis completamente autónomo.

El objetivo es permitir que dos jugadores puedan llevar el marcador del partido sin intervención de un árbitro.

El sistema debe ser:

- Muy rápido
- Muy confiable
- Funcionar sin Internet
- Ser fácil de instalar
- Tener bajo consumo de energía
- Poder operar durante un partido completo

La arquitectura está basada en dos ESP32 y una Raspberry Pi.

---

# Arquitectura General

```
                Jugador

           Brazalete ESP32
          (ESP32-C3 SuperMini)

      Botón Punto Jugador A
      Botón Punto Jugador B

                 │
                 │ ESP-NOW
                 ▼

        ESP32 Receptor USB

                 │
            Serial USB

                 ▼

          Raspberry Pi

     serial_gateway.py

                 │

           HTTP localhost

                 ▼

            server.py

                 │

        lógica del partido

             logic.py

                 │

        render del marcador

            display.py

                 │

          Matriz HUB75
```

---

# Componentes

## ESP32 Emisor

Ubicación:

arduino/Emisor_EspNow/

Responsabilidades:

- Leer dos botones físicos.
- Aplicar debounce.
- Enviar mensajes mediante ESP-NOW.
- Funcionar con batería.
- Minimizar consumo.

No mantiene estado del partido.

Sólo transmite eventos.

Ejemplos:

PLAYER1_POINT

PLAYER2_POINT

En el futuro podrían agregarse:

UNDO

RESET_MATCH

SERVICE_CHANGE

---

## ESP32 Receptor

Ubicación:

arduino/receptor-esp-now/

Responsabilidades:

- Recibir ESP-NOW.
- Validar mensaje.
- Enviar mensaje por Serial USB.
- No contiene lógica del marcador.

Su único trabajo es actuar como gateway inalámbrico → USB.

---

## Raspberry Pi

Responsabilidades:

- Ejecutar el servidor Flask.
- Ejecutar el gateway serial.
- Mantener el estado del partido.
- Dibujar la matriz LED.

---

# Archivos Python

## serial_gateway.py

Lee continuamente el puerto serial.

Convierte los mensajes recibidos desde el ESP32 en llamadas HTTP hacia Flask.

No contiene lógica del tenis.

Sólo convierte:

Serial

↓

HTTP

---

## server.py

Servidor Flask.

Expone API REST para controlar el marcador.

Ejemplos:

POST /player1/point

POST /player2/point

POST /undo

POST /reset

Las APIs llaman directamente a logic.py.

---

## logic.py

Este archivo contiene TODA la lógica del tenis.

Es la única fuente de verdad del estado del partido.

Debe permanecer independiente del hardware.

No debe contener código relacionado con:

- Serial
- ESP-NOW
- Flask
- Display

Sólo reglas del tenis.

Mantiene:

- puntos
- games
- sets
- servidor
- tie-break
- historial (para undo)

---

## display.py

Responsabilidad única:

Dibujar el estado actual del partido sobre la matriz HUB75.

Nunca modifica el estado del juego.

Sólo renderiza.

---

# Flujo de Datos

Jugador presiona botón

↓

ESP32 Emisor

↓

ESP-NOW

↓

ESP32 Receptor

↓

USB Serial

↓

serial_gateway.py

↓

HTTP

↓

Flask

↓

logic.py

↓

display.py

↓

Matriz LED

---

# Filosofía del Proyecto

La lógica del tenis debe estar completamente separada del hardware.

Todo dispositivo externo debe comunicarse mediante eventos.

Nunca debe existir lógica del tenis en los ESP32.

Los ESP32 sólo generan eventos.

Toda decisión se toma en Raspberry Pi.

---

# Estado Actual

Actualmente implementado:

✔ ESP-NOW funcionando.

✔ Comunicación Serial funcionando.

✔ Flask funcionando.

✔ Marcador funcionando.

✔ Integración ESP32 → Raspberry Pi funcionando.

✔ Actualización del display funcionando.

---

# Funcionalidades Pendientes

- Undo mediante botón físico.
- Reset de partido.
- Configuración mediante página web.
- Cambio de lado.
- Cambio automático de saque.
- Tie-break avanzado.
- Persistencia del estado.
- Reinicio automático tras corte eléctrico.
- Modo entrenamiento.
- Estadísticas.

---

# Restricciones

El sistema debe funcionar sin acceso a Internet.

Toda la comunicación debe ser local.

Debe minimizar la latencia.

Debe tolerar desconexiones del puerto serial.

Debe recuperarse automáticamente ante errores.

---

# Decisiones de Diseño

Se utiliza ESP-NOW porque:

- muy baja latencia
- no requiere router
- bajo consumo
- alta confiabilidad

La comunicación entre ESP32 receptor y Raspberry Pi se realiza mediante USB Serial porque es más robusta que WiFi local.

La lógica del partido reside únicamente en Raspberry Pi.

---

# Convenciones

Nunca modificar logic.py para solucionar problemas de hardware.

Nunca agregar lógica del tenis dentro de los ESP32.

Nunca llamar display.py directamente desde los ESP32.

Toda actualización del marcador debe pasar por Flask.

---

# APIs

El servidor Flask expone endpoints HTTP para controlar el marcador.

Estos endpoints también son utilizados por:

- Postman
- serial_gateway.py
- futuras aplicaciones móviles
- futuras páginas web

---

# Objetivos de Calidad

Prioridad 1

Confiabilidad.

Prioridad 2

Latencia.

Prioridad 3

Facilidad de mantenimiento.

---

# Tecnologías

Arduino

ESP32

ESP-NOW

Python

Flask

Raspberry Pi

HUB75

USB Serial

Postman

VS Code

Git

---

# Cómo ejecutar el proyecto

1. Conectar el ESP32 receptor mediante USB.
2. Ejecutar Flask.

sudo python3 server.py

3. En otra terminal ejecutar:

python3 serial_gateway.py

4. Encender el ESP32 emisor.

5. Presionar botones para enviar puntos.

---

# Objetivo Final

Construir un marcador electrónico profesional para tenis, modular, fácilmente mantenible y extensible, donde el hardware sólo genere eventos y toda la inteligencia del sistema resida en la Raspberry Pi.